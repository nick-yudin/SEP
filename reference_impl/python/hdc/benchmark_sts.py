"""
Benchmark: HDC vs Sentence-Transformers on STS Dataset

Evaluates semantic similarity performance on STS Benchmark dataset.
Metric: Spearman correlation with human similarity judgments.

Success criterion: HDC within 5% of baseline
Failure criterion: Gap > 15%

Dataset: STS Benchmark (Semantic Textual Similarity)
- 8,628 sentence pairs with human similarity scores (0-5)
"""

import torch
import numpy as np
from scipy.stats import spearmanr
from sentence_transformers import SentenceTransformer
from datasets import load_dataset
from hdc.text_encoder import HDCTextEncoder
from typing import List, Tuple
import time
import json


def load_sts_benchmark() -> Tuple[List[str], List[str], List[float]]:
    """
    Load STS Benchmark dataset.

    Returns:
        sentences1: List of first sentences
        sentences2: List of second sentences
        scores: List of human similarity scores (0-5)
    """
    print("Loading STS Benchmark dataset...")
    dataset = load_dataset("mteb/stsbenchmark-sts", split="test")

    sentences1 = []
    sentences2 = []
    scores = []

    for item in dataset:
        sentences1.append(item['sentence1'])
        sentences2.append(item['sentence2'])
        # Normalize scores to 0-1 range
        scores.append(item['score'] / 5.0)

    print(f"✓ Loaded {len(scores)} sentence pairs\n")
    return sentences1, sentences2, scores


def evaluate_hdc(
    sentences1: List[str],
    sentences2: List[str],
    human_scores: List[float],
    dimensions: int = 10000
) -> dict:
    """
    Evaluate HDC text encoder on STS benchmark.

    Returns:
        Dictionary with results including Spearman correlation
    """
    print("=" * 60)
    print("EVALUATING HDC TEXT ENCODER")
    print("=" * 60)
    print(f"Dimensions: {dimensions}")
    print(f"N-gram size: 3")
    print()

    encoder = HDCTextEncoder(dimensions=dimensions, ngram_size=3)

    # Encode all sentences
    print("Encoding sentences...")
    start_time = time.time()

    similarities = []
    for i, (sent1, sent2) in enumerate(zip(sentences1, sentences2)):
        if i % 500 == 0:
            print(f"  Progress: {i}/{len(sentences1)}")

        vec1 = encoder.encode(sent1)
        vec2 = encoder.encode(sent2)
        sim = encoder.cosine_similarity(vec1, vec2)
        similarities.append(sim)

    encoding_time = time.time() - start_time

    # Compute Spearman correlation
    correlation, p_value = spearmanr(human_scores, similarities)

    results = {
        "method": "HDC (Binary Spatter Codes)",
        "dimensions": dimensions,
        "spearman_correlation": correlation,
        "p_value": p_value,
        "encoding_time_seconds": encoding_time,
        "pairs_per_second": len(sentences1) / encoding_time
    }

    print(f"\n✓ Encoding complete in {encoding_time:.2f}s")
    print(f"  Speed: {results['pairs_per_second']:.1f} pairs/sec")
    print()

    return results


def evaluate_sentence_transformers(
    sentences1: List[str],
    sentences2: List[str],
    human_scores: List[float],
    model_name: str = "all-MiniLM-L6-v2"
) -> dict:
    """
    Evaluate Sentence-Transformers baseline on STS benchmark.

    Returns:
        Dictionary with results including Spearman correlation
    """
    print("=" * 60)
    print("EVALUATING SENTENCE-TRANSFORMERS BASELINE")
    print("=" * 60)
    print(f"Model: {model_name}")
    print()

    model = SentenceTransformer(model_name)

    # Encode all sentences
    print("Encoding sentences...")
    start_time = time.time()

    embeddings1 = model.encode(sentences1, show_progress_bar=False, convert_to_numpy=True)
    embeddings2 = model.encode(sentences2, show_progress_bar=False, convert_to_numpy=True)

    encoding_time = time.time() - start_time

    # Compute cosine similarities
    similarities = []
    for emb1, emb2 in zip(embeddings1, embeddings2):
        # Cosine similarity
        sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        similarities.append(sim)

    # Compute Spearman correlation
    correlation, p_value = spearmanr(human_scores, similarities)

    results = {
        "method": f"Sentence-Transformers ({model_name})",
        "dimensions": embeddings1.shape[1],
        "spearman_correlation": correlation,
        "p_value": p_value,
        "encoding_time_seconds": encoding_time,
        "pairs_per_second": len(sentences1) / encoding_time
    }

    print(f"\n✓ Encoding complete in {encoding_time:.2f}s")
    print(f"  Speed: {results['pairs_per_second']:.1f} pairs/sec")
    print()

    return results


def compare_results(hdc_results: dict, baseline_results: dict):
    """
    Compare HDC and baseline results, determine success/failure.
    """
    print("=" * 60)
    print("COMPARISON RESULTS")
    print("=" * 60)
    print()

    # Print results table
    print(f"{'Method':<40} {'Spearman ρ':>12} {'Dimensions':>12} {'Speed (pairs/s)':>18}")
    print("-" * 85)

    for results in [baseline_results, hdc_results]:
        print(f"{results['method']:<40} "
              f"{results['spearman_correlation']:>12.4f} "
              f"{results['dimensions']:>12} "
              f"{results['pairs_per_second']:>18.1f}")

    print()

    # Calculate performance gap
    baseline_score = baseline_results['spearman_correlation']
    hdc_score = hdc_results['spearman_correlation']
    gap = baseline_score - hdc_score
    gap_percent = (gap / baseline_score) * 100

    print("ANALYSIS:")
    print(f"  Baseline correlation: {baseline_score:.4f}")
    print(f"  HDC correlation:      {hdc_score:.4f}")
    print(f"  Performance gap:      {gap:.4f} ({gap_percent:+.1f}%)")
    print()

    # Determine success/failure
    if abs(gap_percent) <= 5:
        status = "✅ SUCCESS"
        message = "HDC is within 5% of baseline performance"
    elif abs(gap_percent) <= 15:
        status = "⚠️  PARTIAL SUCCESS"
        message = "HDC is within 15% of baseline, but not optimal"
    else:
        status = "❌ FAILURE"
        message = "HDC gap exceeds 15%, needs improvement"

    print(f"VERDICT: {status}")
    print(f"  {message}")
    print()

    # Additional insights
    speed_ratio = hdc_results['pairs_per_second'] / baseline_results['pairs_per_second']
    print(f"SPEED COMPARISON:")
    print(f"  HDC is {speed_ratio:.2f}× {'faster' if speed_ratio > 1 else 'slower'} than baseline")
    print()

    dim_ratio = hdc_results['dimensions'] / baseline_results['dimensions']
    print(f"DIMENSION COMPARISON:")
    print(f"  HDC uses {dim_ratio:.2f}× {'more' if dim_ratio > 1 else 'fewer'} dimensions")
    print()

    return {
        "status": status,
        "gap_percent": gap_percent,
        "speed_ratio": speed_ratio,
        "dimension_ratio": dim_ratio
    }


def save_results(hdc_results: dict, baseline_results: dict, comparison: dict, output_file: str = "hdc/results/sts_benchmark.json"):
    """Save benchmark results to JSON file"""
    results = {
        "benchmark": "STS Benchmark",
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "hdc": hdc_results,
        "baseline": baseline_results,
        "comparison": comparison
    }

    # Create results directory if needed
    import os
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"✓ Results saved to {output_file}")


def main():
    """Run full benchmark comparison"""
    print("\n" + "=" * 60)
    print("HDC vs SENTENCE-TRANSFORMERS: STS BENCHMARK")
    print("=" * 60)
    print()

    # Load dataset
    sentences1, sentences2, human_scores = load_sts_benchmark()

    # For faster testing, use a subset (remove this for full benchmark)
    # SAMPLE_SIZE = 500
    # sentences1 = sentences1[:SAMPLE_SIZE]
    # sentences2 = sentences2[:SAMPLE_SIZE]
    # human_scores = human_scores[:SAMPLE_SIZE]
    # print(f"⚠️  Using subset of {SAMPLE_SIZE} pairs for quick testing\n")

    # Evaluate baseline
    baseline_results = evaluate_sentence_transformers(
        sentences1, sentences2, human_scores
    )

    # Evaluate HDC
    hdc_results = evaluate_hdc(
        sentences1, sentences2, human_scores,
        dimensions=10000
    )

    # Compare and analyze
    comparison = compare_results(hdc_results, baseline_results)

    # Save results
    save_results(hdc_results, baseline_results, comparison)

    print("\n" + "=" * 60)
    print("BENCHMARK COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
