"""
Benchmark: Ternary HDC (Phase 2) vs Baseline

Tests compression vs accuracy tradeoff:
- Goal: Spearman ρ > 0.75 (acceptable 8% drop from Phase 1.1)
- Target size: < 2.5 KB per vector (16× compression)

Experiments:
1. Sparsity sweep: 0.5, 0.7, 0.9 (find optimal trade-off)
2. Compare against Phase 1.1 (binary) and baseline (float)
"""

import torch
import numpy as np
from scipy.stats import spearmanr
from sentence_transformers import SentenceTransformer
from datasets import load_dataset
from hdc.ternary_encoder import TernaryHDCEncoder
from typing import List, Tuple
import time
import json
import os


def load_sts_benchmark() -> Tuple[List[str], List[str], List[float]]:
    """Load STS Benchmark dataset"""
    print("Loading STS Benchmark dataset...")
    dataset = load_dataset("mteb/stsbenchmark-sts", split="test")

    sentences1 = []
    sentences2 = []
    scores = []

    for item in dataset:
        sentences1.append(item['sentence1'])
        sentences2.append(item['sentence2'])
        scores.append(item['score'] / 5.0)  # Normalize to [0, 1]

    print(f"✓ Loaded {len(scores)} sentence pairs\n")
    return sentences1, sentences2, scores


def evaluate_ternary_hdc(
    sentences1: List[str],
    sentences2: List[str],
    human_scores: List[float],
    hd_dim: int = 10000,
    sparsity: float = 0.7
) -> dict:
    """Evaluate Ternary HDC encoder"""
    print("=" * 60)
    print("EVALUATING TERNARY HDC ENCODER (Phase 2)")
    print("=" * 60)
    print(f"HD Dimensions: {hd_dim}")
    print(f"Sparsity: {sparsity:.1%} (zero out middle {sparsity:.0%})")
    print(f"Semantic Seed: SentenceTransformer embeddings")
    print()

    encoder = TernaryHDCEncoder(
        hd_dim=hd_dim,
        sparsity=sparsity,
        device='cpu'
    )

    print("\nEncoding sentences...")
    start_time = time.time()

    # Encode all unique sentences
    all_sentences = list(set(sentences1 + sentences2))
    print(f"  Unique sentences: {len(all_sentences)}")

    sentence_vectors = {}
    for i, sent in enumerate(all_sentences):
        if i % 500 == 0 and i > 0:
            print(f"  Progress: {i}/{len(all_sentences)}")
        vec = encoder.encode([sent])[0]
        sentence_vectors[sent] = vec

    # Compute similarities
    similarities = []
    for sent1, sent2 in zip(sentences1, sentences2):
        vec1 = sentence_vectors[sent1]
        vec2 = sentence_vectors[sent2]
        sim = encoder.cosine_similarity(vec1, vec2)
        similarities.append(sim)

    encoding_time = time.time() - start_time

    # Compute Spearman correlation
    correlation, p_value = spearmanr(human_scores, similarities)

    # Get storage sizes
    sizes = encoder.get_vector_size()

    results = {
        "method": f"Ternary HDC (Phase 2, sparsity={sparsity})",
        "hd_dimensions": hd_dim,
        "sparsity": sparsity,
        "spearman_correlation": correlation,
        "p_value": p_value,
        "encoding_time_seconds": encoding_time,
        "pairs_per_second": len(sentences1) / encoding_time,
        "semantic_seed": "SentenceTransformer (all-MiniLM-L6-v2)",
        "vector_size_bytes": sizes["ternary_packed"],
        "compression_ratio": sizes["compression_ratio_vs_float32"]
    }

    print(f"\n✓ Encoding complete in {encoding_time:.2f}s")
    print(f"  Speed: {results['pairs_per_second']:.1f} pairs/sec")
    print(f"  Vector size: {sizes['ternary_packed']} bytes")
    print(f"  Compression: {sizes['compression_ratio_vs_float32']:.1f}× vs float32")
    print()

    return results


def evaluate_baseline(
    sentences1: List[str],
    sentences2: List[str],
    human_scores: List[float]
) -> dict:
    """Evaluate SentenceTransformers baseline"""
    print("=" * 60)
    print("EVALUATING BASELINE (SentenceTransformers)")
    print("=" * 60)

    model = SentenceTransformer('all-MiniLM-L6-v2')

    print("Encoding sentences...")
    start_time = time.time()

    embeddings1 = model.encode(sentences1, show_progress_bar=False, convert_to_numpy=True)
    embeddings2 = model.encode(sentences2, show_progress_bar=False, convert_to_numpy=True)

    # Compute cosine similarities
    similarities = []
    for emb1, emb2 in zip(embeddings1, embeddings2):
        sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        similarities.append(sim)

    encoding_time = time.time() - start_time

    # Compute Spearman correlation
    correlation, p_value = spearmanr(human_scores, similarities)

    results = {
        "method": "SentenceTransformers (Baseline)",
        "dimensions": embeddings1.shape[1],
        "spearman_correlation": correlation,
        "p_value": p_value,
        "encoding_time_seconds": encoding_time,
        "pairs_per_second": len(sentences1) / encoding_time,
        "vector_size_bytes": embeddings1.shape[1] * 4  # float32
    }

    print(f"\n✓ Encoding complete in {encoding_time:.2f}s")
    print(f"  Speed: {results['pairs_per_second']:.1f} pairs/sec")
    print(f"  Vector size: {results['vector_size_bytes']} bytes")
    print()

    return results


def compare_results(ternary_results: dict, baseline_results: dict):
    """Compare results and determine success/failure"""
    print("=" * 60)
    print("PHASE 2 RESULTS")
    print("=" * 60)
    print()

    baseline_score = baseline_results['spearman_correlation']
    ternary_score = ternary_results['spearman_correlation']
    gap = baseline_score - ternary_score
    gap_percent = (gap / baseline_score) * 100

    print(f"{'Method':<50} {'Spearman ρ':>12} {'Size (bytes)':>15}")
    print("-" * 80)
    print(f"{baseline_results['method']:<50} {baseline_score:>12.4f} {baseline_results['vector_size_bytes']:>15}")
    print(f"{ternary_results['method']:<50} {ternary_score:>12.4f} {ternary_results['vector_size_bytes']:>15}")
    print()

    print("ANALYSIS:")
    print(f"  Baseline:       {baseline_score:.4f}")
    print(f"  Ternary HDC:    {ternary_score:.4f}")
    print(f"  Gap:            {gap:.4f} ({gap_percent:+.1f}%)")
    print()

    # Determine success (relaxed criterion for compression)
    if abs(gap_percent) <= 10:
        status = "✅ SUCCESS"
        message = "Phase 2 achieves within 10% of baseline!"
    elif abs(gap_percent) <= 15:
        status = "⚠️  PARTIAL SUCCESS"
        message = "Phase 2 within 15%, but lossy compression hurts"
    else:
        status = "❌ FAILURE"
        message = "Phase 2 compression loses too much accuracy"

    print(f"VERDICT: {status}")
    print(f"  {message}")
    print()

    # Compression analysis
    compression_ratio = ternary_results['compression_ratio']
    size_reduction = (1 - ternary_results['vector_size_bytes'] / baseline_results['vector_size_bytes']) * 100

    print(f"COMPRESSION:")
    print(f"  Ternary vs float32: {compression_ratio:.1f}× smaller")
    print(f"  Ternary vs baseline: {size_reduction:.1f}% size reduction")
    print(f"  Final size: {ternary_results['vector_size_bytes']} bytes")
    print()

    # Speed comparison
    speed_ratio = ternary_results['pairs_per_second'] / baseline_results['pairs_per_second']
    print(f"SPEED:")
    print(f"  Ternary HDC is {speed_ratio:.2f}× {'faster' if speed_ratio > 1 else 'slower'}")
    print()

    return {
        "status": status,
        "gap_percent": gap_percent,
        "compression_ratio": compression_ratio,
        "size_reduction_percent": size_reduction,
        "speed_ratio": speed_ratio
    }


def save_results(ternary_results: dict, baseline_results: dict, comparison: dict, sparsity: float):
    """Save results to JSON"""
    output = {
        "phase": "2",
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "approach": "Ternary Quantization HDC",
        "sparsity": sparsity,
        "baseline": baseline_results,
        "ternary_hdc": ternary_results,
        "comparison": comparison
    }

    os.makedirs("hdc/results", exist_ok=True)
    output_file = f"hdc/results/phase_2_ternary_sparsity_{sparsity}.json"

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"✓ Results saved to {output_file}")


def run_sparsity_sweep(sentences1, sentences2, human_scores, baseline_results):
    """Test multiple sparsity levels"""
    print("\n" + "=" * 60)
    print("SPARSITY SWEEP: Finding optimal compression/accuracy trade-off")
    print("=" * 60)
    print()

    sparsities = [0.5, 0.7, 0.9]
    results = []

    for sparsity in sparsities:
        print(f"\n{'=' * 60}")
        print(f"Testing sparsity = {sparsity:.1%}")
        print(f"{'=' * 60}\n")

        ternary_results = evaluate_ternary_hdc(
            sentences1, sentences2, human_scores,
            hd_dim=10000,
            sparsity=sparsity
        )

        comparison = compare_results(ternary_results, baseline_results)
        save_results(ternary_results, baseline_results, comparison, sparsity)

        results.append({
            "sparsity": sparsity,
            "correlation": ternary_results['spearman_correlation'],
            "gap_percent": comparison['gap_percent'],
            "size_bytes": ternary_results['vector_size_bytes']
        })

    # Summary
    print("\n" + "=" * 60)
    print("SPARSITY SWEEP SUMMARY")
    print("=" * 60)
    print()
    print(f"{'Sparsity':<12} {'Spearman ρ':>12} {'Gap':>10} {'Size':>12}")
    print("-" * 50)

    for r in results:
        print(f"{r['sparsity']:<12.1%} {r['correlation']:>12.4f} {r['gap_percent']:>9.1f}% {r['size_bytes']:>12} B")

    print()
    print("✓ Best trade-off: Look for smallest size with gap < 10%")
    print()


def main():
    """Run Phase 2 benchmark"""
    print("\n" + "=" * 60)
    print("PHASE 2: TERNARY QUANTIZATION HDC")
    print("=" * 60)
    print()

    # Load dataset
    sentences1, sentences2, human_scores = load_sts_benchmark()

    # Evaluate baseline
    baseline_results = evaluate_baseline(sentences1, sentences2, human_scores)

    # Run sparsity sweep
    run_sparsity_sweep(sentences1, sentences2, human_scores, baseline_results)

    print("\n" + "=" * 60)
    print("PHASE 2 COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
