"""
HDC Text Encoder using Binary Spatter Codes

This implements a hyperdimensional computing text encoder that maps text
to high-dimensional binary vectors (10,000 bits) using:
- Random vectors for token vocabulary
- N-gram encoding via circular permutation
- Superposition for composing final vector

Reference: Kanerva, P. (2009). "Hyperdimensional Computing"
"""

import torch
import torchhd
from torchhd import embeddings
from typing import List, Dict
import hashlib


class HDCTextEncoder:
    """
    Binary Spatter Code encoder for text using hyperdimensional computing.

    Parameters:
        dimensions: Number of dimensions (default: 10,000)
        ngram_size: Size of n-grams to use (default: 3)
        device: torch device ('cpu' or 'cuda')
    """

    def __init__(self, dimensions: int = 10000, ngram_size: int = 3, device: str = 'cpu'):
        self.dimensions = dimensions
        self.ngram_size = ngram_size
        self.device = device

        # Token vocabulary: maps tokens to random binary hypervectors
        self.token_vectors: Dict[str, torch.Tensor] = {}

        # Position vectors for n-gram encoding
        self.position_vectors = self._generate_position_vectors()

    def _generate_position_vectors(self) -> List[torch.Tensor]:
        """
        Generate position vectors for n-gram encoding.
        Each position is represented by a permutation of a base vector.
        """
        # Base random binary vector
        base = torchhd.random(1, self.dimensions, device=self.device)

        # Generate permutations for each position
        positions = []
        for i in range(self.ngram_size):
            # Circular permutation by i positions
            positions.append(torch.roll(base, shifts=i, dims=1))

        return positions

    def _get_token_vector(self, token: str) -> torch.Tensor:
        """
        Get or create a random binary hypervector for a token.
        Uses deterministic seeding based on token hash for reproducibility.
        """
        if token not in self.token_vectors:
            # Use token hash as seed for deterministic random vectors
            seed = int(hashlib.md5(token.encode()).hexdigest()[:8], 16)
            torch.manual_seed(seed)
            self.token_vectors[token] = torchhd.random(
                1, self.dimensions, device=self.device
            )

        return self.token_vectors[token]

    def _tokenize(self, text: str) -> List[str]:
        """
        Simple whitespace tokenization and lowercasing.
        For production, use proper tokenizer (e.g., spaCy, NLTK).
        """
        return text.lower().split()

    def _encode_ngram(self, tokens: List[str]) -> torch.Tensor:
        """
        Encode an n-gram using circular permutation binding.

        For n-gram [w1, w2, w3]:
        - Bind w1 with position 0 (no permutation)
        - Bind w2 with position 1 (permute by 1)
        - Bind w3 with position 2 (permute by 2)
        - Bundle (XOR) all together
        """
        ngram_vector = torch.zeros(1, self.dimensions, device=self.device, dtype=torch.bool)

        for i, token in enumerate(tokens):
            token_vec = self._get_token_vector(token)
            # Bind token with position via XOR
            position_vec = self.position_vectors[i]
            bound = torch.logical_xor(token_vec, position_vec)
            # Bundle into n-gram vector
            ngram_vector = torch.logical_xor(ngram_vector, bound)

        return ngram_vector

    def encode(self, text: str) -> torch.Tensor:
        """
        Encode text into a binary hypervector.

        Process:
        1. Tokenize text
        2. Create overlapping n-grams
        3. Encode each n-gram with position binding
        4. Bundle all n-grams via majority voting

        Returns:
            Binary tensor of shape (1, dimensions)
        """
        tokens = self._tokenize(text)

        if len(tokens) == 0:
            # Return zero vector for empty text
            return torch.zeros(1, self.dimensions, device=self.device, dtype=torch.bool)

        # Generate n-grams with padding
        ngrams = []
        for i in range(len(tokens)):
            ngram = tokens[i:i+self.ngram_size]
            if len(ngram) < self.ngram_size:
                # Pad with special token
                ngram = ngram + ['<PAD>'] * (self.ngram_size - len(ngram))
            ngrams.append(ngram)

        # Encode each n-gram
        ngram_vectors = []
        for ngram in ngrams:
            ngram_vectors.append(self._encode_ngram(ngram))

        # Bundle all n-grams using majority voting
        if len(ngram_vectors) == 1:
            final_vector = ngram_vectors[0]
        else:
            # Stack and count 1s
            stacked = torch.cat(ngram_vectors, dim=0).float()
            vote_count = stacked.sum(dim=0)
            # Majority vote: > half of vectors have 1 at this position
            final_vector = (vote_count > len(ngram_vectors) / 2).unsqueeze(0)

        return final_vector

    def cosine_similarity(self, vec1: torch.Tensor, vec2: torch.Tensor) -> float:
        """
        Compute cosine similarity between two binary hypervectors.
        For binary vectors, this is equivalent to Hamming similarity.
        """
        # XOR gives positions where vectors differ
        diff = torch.logical_xor(vec1, vec2)
        # Count differing bits
        hamming_distance = diff.sum().item()
        # Normalize to [0, 1] similarity
        similarity = 1 - (hamming_distance / self.dimensions)
        return similarity

    def batch_encode(self, texts: List[str]) -> torch.Tensor:
        """
        Encode multiple texts into a batch of hypervectors.

        Returns:
            Binary tensor of shape (len(texts), dimensions)
        """
        vectors = [self.encode(text) for text in texts]
        return torch.cat(vectors, dim=0)


def demo():
    """Demo of HDC text encoder"""
    print("=== HDC Text Encoder Demo ===\n")

    encoder = HDCTextEncoder(dimensions=10000, ngram_size=3)

    # Test sentences
    sentences = [
        "The cat sat on the mat",
        "A cat is sitting on a mat",  # Similar meaning
        "The weather is nice today",  # Different meaning
        "Dogs are playing in the park",  # Different meaning
    ]

    print("Encoding sentences:")
    vectors = []
    for i, sent in enumerate(sentences):
        vec = encoder.encode(sent)
        vectors.append(vec)
        print(f"{i+1}. {sent}")
        print(f"   Vector shape: {vec.shape}, Sparsity: {vec.float().mean():.3f}\n")

    print("\nSemantic Similarity Matrix:")
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

    print("\n✓ Expected: S1 and S2 should have high similarity (same meaning)")
    print("✓ Expected: S1 vs S3, S4 should have lower similarity (different meaning)")


if __name__ == "__main__":
    demo()
