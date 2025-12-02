"""
Ternary HDC Encoder: Phase 2 Quantization

Converts float hypervectors to ternary {-1, 0, +1} representation.
Goal: 16-32× compression with < 10% accuracy loss.

Theory:
- Signal lives in distribution tails (high magnitude values)
- Middle values (~0) are noise, can be zeroed out
- Ternary uses 2 bits per dimension (packed: 0.25 bytes/dim)
- 10,000 dims × 0.25 bytes = 2.5 KB (vs 40 KB float32)

Reference: "TernaryBERT" (Bai et al., 2020)
"""

import torch
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Tuple
import struct


class TernaryHDCEncoder:
    """
    Ternary quantized HDC encoder for ultra-low bandwidth transmission.

    Parameters:
        hd_dim: Hypervector dimensions (default: 10,000)
        base_model_name: Pretrained model for semantic seed
        sparsity: Fraction of values to zero out (default: 0.7 = 70% sparse)
        device: torch device ('cpu' or 'cuda')
    """

    def __init__(
        self,
        hd_dim: int = 10000,
        base_model_name: str = 'all-MiniLM-L6-v2',
        sparsity: float = 0.7,
        device: str = 'cpu'
    ):
        self.hd_dim = hd_dim
        self.sparsity = sparsity
        self.device = device

        # Load base model
        print(f"Loading pretrained model: {base_model_name}")
        self.base_model = SentenceTransformer(base_model_name, device=device)
        self.base_dim = self.base_model.get_sentence_embedding_dimension()

        # Initialize random projection matrix (Johnson-Lindenstrauss)
        print(f"Initializing projection matrix: {self.base_dim} → {self.hd_dim}")
        torch.manual_seed(42)  # Reproducibility
        self.projection = torch.randn(self.base_dim, self.hd_dim).to(device)
        # Normalize by sqrt(input_dim) for J-L lemma
        self.projection = self.projection / torch.sqrt(torch.tensor(self.base_dim, dtype=torch.float32))

    def _project_to_hyperspace(self, embeddings: torch.Tensor) -> torch.Tensor:
        """
        Project dense embeddings to high-dimensional space.

        Args:
            embeddings: (batch, base_dim) dense embeddings

        Returns:
            (batch, hd_dim) hypervectors
        """
        return torch.matmul(embeddings, self.projection)

    def ternarize(self, vectors: torch.Tensor) -> torch.Tensor:
        """
        Convert float vectors to ternary {-1, 0, +1}.

        Strategy: Keep top (1 - sparsity) fraction of values by absolute magnitude.
        - Positive tail → +1
        - Negative tail → -1
        - Middle (noise) → 0

        Args:
            vectors: (batch, hd_dim) float tensors

        Returns:
            (batch, hd_dim) ternary tensors {-1, 0, +1}
        """
        # Find threshold: (sparsity)-th percentile of absolute values
        abs_vectors = torch.abs(vectors)
        threshold = torch.quantile(abs_vectors, self.sparsity, dim=1, keepdim=True)

        # Create ternary values
        ternary = torch.zeros_like(vectors)
        ternary[vectors > threshold] = 1.0
        ternary[vectors < -threshold] = -1.0

        return ternary

    def encode(self, texts: List[str]) -> torch.Tensor:
        """
        Encode texts into ternary hypervectors.

        Args:
            texts: List of text strings

        Returns:
            (len(texts), hd_dim) ternary tensor {-1, 0, +1}
        """
        # Get base embeddings
        with torch.no_grad():
            embeddings = self.base_model.encode(
                texts,
                convert_to_tensor=True,
                show_progress_bar=False,
                device=self.device
            )

        # Project to hyperspace
        hyper_vectors = self._project_to_hyperspace(embeddings)

        # Ternarize
        ternary_vectors = self.ternarize(hyper_vectors)

        return ternary_vectors

    def cosine_similarity(self, vec1: torch.Tensor, vec2: torch.Tensor) -> float:
        """
        Compute cosine similarity between ternary vectors.

        Args:
            vec1: (hd_dim,) ternary vector
            vec2: (hd_dim,) ternary vector

        Returns:
            Cosine similarity in [0, 1]
        """
        dot_product = torch.dot(vec1, vec2)
        norm1 = torch.norm(vec1)
        norm2 = torch.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)
        # Normalize to [0, 1] range
        return (similarity.item() + 1) / 2

    def pack_ternary(self, vector: torch.Tensor) -> bytes:
        """
        Pack ternary vector {-1, 0, +1} into compressed binary format.

        Encoding: 2 bits per value
        - 00: 0
        - 01: +1
        - 10: -1
        - 11: unused

        Args:
            vector: (hd_dim,) ternary tensor

        Returns:
            Packed bytes (hd_dim / 4 bytes)
        """
        vector = vector.cpu().numpy().astype(np.int8)

        # Map {-1, 0, +1} → {0b10, 0b00, 0b01}
        bits = []
        for val in vector:
            if val == 0:
                bits.append(0b00)
            elif val == 1:
                bits.append(0b01)
            elif val == -1:
                bits.append(0b10)

        # Pack 4 ternary values into 1 byte (4 × 2 bits = 8 bits)
        packed = bytearray()
        for i in range(0, len(bits), 4):
            byte = 0
            for j in range(4):
                if i + j < len(bits):
                    byte |= (bits[i + j] << (6 - j * 2))
            packed.append(byte)

        return bytes(packed)

    def unpack_ternary(self, packed_bytes: bytes, hd_dim: int) -> torch.Tensor:
        """
        Unpack compressed binary format back to ternary vector.

        Args:
            packed_bytes: Packed binary representation
            hd_dim: Original hypervector dimension

        Returns:
            (hd_dim,) ternary tensor {-1, 0, +1}
        """
        values = []

        for byte in packed_bytes:
            for shift in [6, 4, 2, 0]:
                bits = (byte >> shift) & 0b11
                if bits == 0b00:
                    values.append(0)
                elif bits == 0b01:
                    values.append(1)
                elif bits == 0b10:
                    values.append(-1)

                if len(values) >= hd_dim:
                    break
            if len(values) >= hd_dim:
                break

        return torch.tensor(values[:hd_dim], dtype=torch.float32)

    def get_vector_size(self) -> dict:
        """
        Calculate storage requirements for different representations.

        Returns:
            Dictionary with sizes in bytes
        """
        return {
            "float32": self.hd_dim * 4,  # 4 bytes per float32
            "float16": self.hd_dim * 2,  # 2 bytes per float16
            "binary": self.hd_dim // 8,  # 1 bit per value
            "ternary_packed": (self.hd_dim * 2) // 8,  # 2 bits per value
            "compression_ratio_vs_float32": (self.hd_dim * 4) / ((self.hd_dim * 2) // 8)
        }


def demo():
    """Demo ternary HDC encoder"""
    print("=" * 60)
    print("TERNARY HDC ENCODER DEMO (Phase 2)")
    print("=" * 60)
    print()

    # Test different sparsity levels
    sparsities = [0.5, 0.7, 0.9]

    encoder = TernaryHDCEncoder(hd_dim=10000, sparsity=0.7, device='cpu')

    sentences = [
        "The cat sat on the mat",
        "A cat is sitting on a mat",
        "The weather is nice today",
        "Dogs are playing in the park"
    ]

    print("\nEncoding sentences:")
    for i, sent in enumerate(sentences):
        print(f"{i+1}. {sent}")
    print()

    # Encode with ternary quantization
    print("Encoding with ternary quantization (sparsity=0.7)...")
    vectors = encoder.encode(sentences)

    print(f"✓ Encoded {len(sentences)} sentences")
    print(f"  Vector shape: {vectors.shape}")
    print(f"  Sparsity: {(vectors == 0).float().mean():.1%} zeros")
    print(f"  Positive: {(vectors == 1).float().mean():.1%}")
    print(f"  Negative: {(vectors == -1).float().mean():.1%}")
    print()

    # Size analysis
    sizes = encoder.get_vector_size()
    print("STORAGE REQUIREMENTS:")
    print(f"  Float32:        {sizes['float32']:>6} bytes (baseline)")
    print(f"  Float16:        {sizes['float16']:>6} bytes")
    print(f"  Binary:         {sizes['binary']:>6} bytes")
    print(f"  Ternary packed: {sizes['ternary_packed']:>6} bytes")
    print(f"  Compression:    {sizes['compression_ratio_vs_float32']:.1f}× vs float32")
    print()

    # Semantic similarity
    print("SEMANTIC SIMILARITY MATRIX:")
    print("     ", end="")
    for i in range(len(sentences)):
        print(f"  S{i+1}  ", end="")
    print()

    for i in range(len(sentences)):
        print(f"S{i+1}:  ", end="")
        for j in range(len(sentences)):
            sim = encoder.cosine_similarity(vectors[i], vectors[j])
            print(f"{sim:.3f}  ", end="")
        print()

    print()
    print("✓ Expected: S1 and S2 should have high similarity (same meaning)")
    print("✓ Expected: S1 vs S3, S4 should have lower similarity")
    print()

    # Test packing/unpacking
    print("TESTING BINARY PACKING:")
    test_vector = vectors[0]
    packed = encoder.pack_ternary(test_vector)
    unpacked = encoder.unpack_ternary(packed, encoder.hd_dim)

    print(f"  Original size:  {test_vector.numel() * 4} bytes (float32)")
    print(f"  Packed size:    {len(packed)} bytes")
    print(f"  Compression:    {test_vector.numel() * 4 / len(packed):.1f}×")
    print(f"  Reconstruction: {torch.equal(test_vector.cpu(), unpacked)} (lossless)")
    print()

    print("=" * 60)
    print("PHASE 2 DEMO COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    demo()
