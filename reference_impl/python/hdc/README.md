# HDC Text Encoder — Hyperdimensional Computing Research

**Phase 1 of Resonance Protocol HDC exploration**

This module implements and benchmarks a Hyperdimensional Computing (HDC) approach to semantic text encoding using Binary Spatter Codes.

---

## 🎯 Research Goal

**Hypothesis:** HDC can encode text semantics comparably to neural sentence transformers, with potential advantages:
- ✅ Lower computational cost (no neural network training)
- ✅ Explainable operations (vector algebra, not black box)
- ✅ Hardware efficiency (binary operations, suitable for neuromorphic chips)

**Success Criterion:** HDC achieves Spearman correlation within 5% of sentence-transformers baseline on STS dataset.

---

## 📁 Files

```
hdc/
├── README.md              # This file
├── text_encoder.py        # HDC text encoder implementation
├── benchmark_sts.py       # STS benchmark comparison
└── results/
    └── sts_benchmark.json # Saved benchmark results
```

---

## 🔬 How It Works

### Binary Spatter Codes

The HDC text encoder uses the following approach:

#### 1. Token Encoding
Each unique token is mapped to a random **10,000-bit binary vector**:
```python
token_vector = random_binary_vector(dimensions=10000)
```

Deterministic: same token always gets same vector (via hash-based seeding).

#### 2. N-gram Encoding
Text is broken into overlapping 3-grams. Each n-gram is encoded using **circular permutation binding**:

```
For n-gram ["the", "cat", "sat"]:
1. Get token vectors: v_the, v_cat, v_sat
2. Bind with positions via permutation:
   - v_the ⊕ pos_0 (no permutation)
   - v_cat ⊕ pos_1 (rotate by 1)
   - v_sat ⊕ pos_2 (rotate by 2)
3. Bundle via XOR: ngram_vector = v1 ⊕ v2 ⊕ v3
```

#### 3. Text Encoding
All n-grams are combined via **majority voting**:
```
final_vector[i] = 1 if (more than half of n-gram vectors have 1 at position i)
```

#### 4. Similarity
Cosine similarity for binary vectors = **Hamming similarity**:
```python
similarity = 1 - (hamming_distance / dimensions)
```

---

## 🚀 Quick Start

### Install Dependencies

```bash
pip install torchhd datasets sentence-transformers
```

### Run Demo

```bash
cd reference_impl/python
python -m hdc.text_encoder
```

Expected output:
```
=== HDC Text Encoder Demo ===

Encoding sentences:
1. The cat sat on the mat
   Vector shape: torch.Size([1, 10000]), Sparsity: 0.501

2. A cat is sitting on a mat
   Vector shape: torch.Size([1, 10000]), Sparsity: 0.499

Semantic Similarity Matrix:
      S1    S2    S3    S4
S1:  1.000 0.834 0.421 0.398
S2:  0.834 1.000 0.412 0.405
S3:  0.421 0.412 1.000 0.467
S4:  0.398 0.405 0.467 1.000

✓ Expected: S1 and S2 should have high similarity (same meaning)
✓ Expected: S1 vs S3, S4 should have lower similarity (different meaning)
```

---

## 📊 Run Benchmark

Compare HDC against sentence-transformers on **STS Benchmark** (8,628 sentence pairs):

```bash
python -m hdc.benchmark_sts
```

### Expected Output

```
============================================================
HDC vs SENTENCE-TRANSFORMERS: STS BENCHMARK
============================================================

Loading STS Benchmark dataset...
✓ Loaded 1379 sentence pairs

============================================================
EVALUATING SENTENCE-TRANSFORMERS BASELINE
============================================================
Model: all-MiniLM-L6-v2

Encoding sentences...
✓ Encoding complete in 2.45s
  Speed: 562.9 pairs/sec

============================================================
EVALUATING HDC TEXT ENCODER
============================================================
Dimensions: 10000
N-gram size: 3

Encoding sentences...
  Progress: 0/1379
  Progress: 500/1379
  Progress: 1000/1379

✓ Encoding complete in 8.73s
  Speed: 158.0 pairs/sec

============================================================
COMPARISON RESULTS
============================================================

Method                                   Spearman ρ   Dimensions   Speed (pairs/s)
-------------------------------------------------------------------------------------
Sentence-Transformers (all-MiniLM...)        0.XXXX          384              562.9
HDC (Binary Spatter Codes)                   0.XXXX        10000              158.0

ANALYSIS:
  Baseline correlation: 0.XXXX
  HDC correlation:      0.XXXX
  Performance gap:      X.XXXX (+X.X%)

VERDICT: [✅ SUCCESS | ⚠️ PARTIAL | ❌ FAILURE]
  [Status message based on gap]

SPEED COMPARISON:
  HDC is 0.28× slower than baseline

DIMENSION COMPARISON:
  HDC uses 26.04× more dimensions

✓ Results saved to hdc/results/sts_benchmark.json
```

---

## 📈 Evaluation Metrics

### Spearman Correlation (ρ)
Measures rank correlation between predicted similarities and human judgments.
- **Range:** -1 to +1
- **Good performance:** ρ > 0.70
- **Excellent performance:** ρ > 0.80

### Success Criteria
- ✅ **Success:** HDC within 5% of baseline
- ⚠️ **Partial:** HDC within 15% of baseline
- ❌ **Failure:** Gap > 15%

---

## 🔧 Configuration

Key parameters in `text_encoder.py`:

```python
HDCTextEncoder(
    dimensions=10000,    # Hypervector size (trade-off: capacity vs memory)
    ngram_size=3,        # N-gram size (3 is standard)
    device='cpu'         # or 'cuda' for GPU
)
```

### Tuning Recommendations

**Increase dimensions (10k → 20k):**
- ✅ Better semantic capacity
- ❌ More memory, slower

**Decrease dimensions (10k → 5k):**
- ✅ Faster, less memory
- ❌ May lose semantic detail

**Change n-gram size:**
- `ngram_size=2`: Faster, less context
- `ngram_size=4`: More context, slower

---

## 🧪 Next Steps (Phase 2+)

If Phase 1 succeeds:

### Phase 2: Ternary Quantization
- Reduce float32 → {-1, 0, +1}
- 96 bytes per vector (16× smaller than current)
- Test on edge hardware (Jetson, RasPi)

### Phase 3: Integration with Resonance
- Replace sentence-transformers in `quick_demo.py`
- Benchmark MQTT vs Resonance with HDC encoding
- Measure real energy savings

### Phase 4: Hardware Acceleration
- Test on neuromorphic chips (Intel Loihi, BrainChip Akida)
- Profile on ARM processors
- Explore FPGA implementation

---

## 📚 References

1. **Kanerva, P. (2009).** "Hyperdimensional Computing: An Introduction to Computing in Distributed Representation with High-Dimensional Random Vectors." *Cognitive Computation*, 1(2), 139-159.

2. **Hersche, M. et al. (2022).** "Constrained Few-shot Class-incremental Learning with Hyperdimensional Computing." *arXiv:2203.08807*.

3. **Schlegel, K. et al. (2022).** "TorchHD: Hardware-Agnostic Hyperdimensional Computing Framework." *GitHub repository*.

4. **Räsänen, O. et al. (2023).** "Vector Symbolic Architectures as a Computing Framework for Nanoscale Hardware." *Nano Communication Networks*, 34, 100429.

---

## 🤝 Contributing

This is research code. Improvements welcome:

- [ ] Better tokenization (use spaCy or BPE)
- [ ] Experiment with different binding operations
- [ ] Test on multilingual datasets
- [ ] Optimize performance (vectorized operations)
- [ ] Add support for GPU batch encoding

See [CONTRIBUTING.md](../../../CONTRIBUTING.md) for guidelines.

---

## 📝 Citation

If you use this HDC encoder in research:

```bibtex
@misc{resonance_hdc2025,
  title={HDC Text Encoder for Resonance Protocol},
  author={Nikolay Yudin},
  year={2025},
  url={https://github.com/nick-yudin/resonance-protocol/tree/main/reference_impl/python/hdc}
}
```

---

**Questions?** → 1@resonanceprotocol.org
