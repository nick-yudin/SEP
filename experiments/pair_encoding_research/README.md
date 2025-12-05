# HDC Pair Encoding Research: Complete Results

## Executive Summary

**Problem:** HDC transfer works well for single-sentence tasks (87-93% of teacher) but hit a ceiling (~45-54%) for sentence-pair tasks (NLI).

**Solution Found:** Learned Compression achieves **67.2% accuracy in 4096d** — matching 16384d baseline while using 4x less dimensions.

**Key Insight:** The bottleneck was NOT in HDC itself, but in:
1. Using general-purpose encoder instead of NLI-tuned
2. Trying to compress pair information into single vector via binding
3. Using random projection instead of learned compression

---

## Final Results

| Approach | Accuracy | Dim | Ratio vs Teacher (91%) |
|----------|----------|-----|------------------------|
| **Learned Compression** | **67.2%** | **4096d** | **73.5%** 🏆 |
| Two-Vector Baseline | 67.0% | 16384d | 73.3% |
| Segmented | 64.2% | 4096d | 70.2% |
| Role-Filler Binding | 60.0% | 4096d | 65.6% |

---

## Research Phases

### Phase 1: Ablation Study
**Question:** Where is information lost?

| Config | Accuracy | Finding |
|--------|----------|---------|
| A: Float (no HDC) | 54.6% | Baseline |
| B: Float + Projection | 51.6% | -3% from projection |
| C: Ternary only | 48.8% | -5.8% from quantization |
| D: Full HDC | 52.6% | -2% combined |

**Conclusion:** Encoder/features are the bottleneck, not HDC pipeline.

### Phase 2: NLI-Tuned Encoder
**Question:** Does specialized encoder help?

| Encoder | Float | HDC |
|---------|-------|-----|
| MiniLM (baseline) | 53.0% | 50.4% |
| NLI-DistilRoBERTa | 66.6% | 64.4% |
| **NLI-MPNet** | **67.8%** | **63.8%** |

**Conclusion:** NLI encoder gives +14% improvement!

### Phase 3: Project-First-Bind-Later
**Question:** Does HDC-style binding help?

| Strategy | Float | Ternary |
|----------|-------|---------|
| Baseline concat | 64.0% | 61.4% |
| Project + Bundle | 55.4% | 55.6% |
| Project + Permute | 54.0% | 54.0% |
| **Two-Vector** | **67.6%** | **65.6%** |

**Conclusion:** Binding makes things WORSE. Two-Vector (keeping P and H separate) works best.

### Phase 4: Learned Compression
**Question:** Can we compress 16384d → 4096d without losing accuracy?

| Approach | Accuracy | Dim |
|----------|----------|-----|
| Baseline (Two-Vector) | 67.0% | 16384d |
| **Learned Compression** | **67.2%** | **4096d** |
| Segmented | 64.2% | 4096d |
| Role-Filler | 60.0% | 4096d |

**Conclusion:** YES! Learned compression achieves 4x reduction with NO accuracy loss.

---

## Final Architecture

```python
class LearnedCompressionEncoder:
    def __init__(self, hdc_dim=4096):
        self.encoder = SentenceTransformer('nli-mpnet-base-v2')
        
        # Random projection (frozen)
        self.projection = random_matrix(768, hdc_dim)
        
        # Learned compression (trained on MNLI, then frozen)
        self.compressor = Linear(hdc_dim * 4, hdc_dim)
    
    def encode_pair(self, premise, hypothesis):
        # Get semantic embeddings
        p_emb = self.encoder.encode(premise)  # 768d
        h_emb = self.encoder.encode(hypothesis)  # 768d
        
        # Project to HDC
        p_hdc = p_emb @ self.projection  # 4096d
        h_hdc = h_emb @ self.projection  # 4096d
        
        # Two-vector features
        features = concat([p_hdc, h_hdc, p_hdc - h_hdc, p_hdc * h_hdc])  # 16384d
        
        # Learned compression
        compressed = features @ self.compressor  # 4096d
        
        # Ternary quantization
        return ternary_quantize(compressed)  # 4096d ternary
```

---

## Key Findings

### What Works
✅ NLI-tuned encoder (nli-mpnet-base-v2)
✅ Two-Vector features [P, H, P-H, P*H]
✅ Learned compression for dimension reduction
✅ Standard ternary quantization

### What Doesn't Work
❌ General-purpose encoder (MiniLM)
❌ HDC binding/bundling without unbinding
❌ Role-filler binding for classification
❌ Permutation for asymmetry

### Why Binding Failed
Experts explained: HDC binding is designed for creating new symbols with subsequent unbinding/retrieval. Using it as "aggressive compression" for classification destroys information due to:
- Catastrophic interference after ternary quantization
- Commutative binding (P*H = H*P) doesn't capture asymmetry
- No unbinding mechanism to recover original signals

---

## Comparison: Single vs Pair Tasks

| Task Type | Example | Teacher | HDC | Ratio |
|-----------|---------|---------|-----|-------|
| Single-sentence | SST-2 | 88% | 77% | 87.5% |
| Single-sentence | AG News | 93% | 87% | 92.9% |
| **Sentence-pair** | **MNLI** | **91%** | **67%** | **73.5%** |

Gap is larger for pairs, but 73.5% ratio is acceptable for many applications.

---

## For Resonance Protocol

### Recommended Approach
```
Single-sentence tasks:
  → Standard HDC (works great, 87-93% ratio)
  
Sentence-pair tasks:
  → Learned Compression HDC (67.2%, 73.5% ratio)
  → 4096d ternary vectors (~4KB per pair)
  → Requires shared W_compressor matrix in protocol spec
```

### Trade-offs
| Metric | Value |
|--------|-------|
| Accuracy | 67.2% (vs 91% teacher) |
| Vector size | 4096 ternary = 4KB |
| Compression | 4x vs naive Two-Vector |
| Protocol complexity | +1 shared matrix (W_compressor) |

---

## Files

### Notebooks
- `Phase1_AblationStudy.ipynb` - Diagnostic experiments
- `Phase2_NLI_Encoder.ipynb` - Encoder comparison
- `Phase3_ProjectFirst.ipynb` - Binding strategies
- `Phase4_LearnedCompression.ipynb` - Final solution

### Results
- `ablation_study_results.json`
- `phase2_encoder_results.json`
- `phase3_project_first_results.json`
- `phase4_compression_results.json`

### Figures
- `ablation_study_results.png`
- `phase2_encoder_comparison.png`
- `phase3_project_first_results.png`
- `phase4_compression_results.png`

---

## Future Work

1. **8192d middle ground** - May give +2-3% accuracy
2. **Learned W_sent projection** - Replace random with trained
3. **More training data** - 10K+ examples
4. **Cross-lingual** - Test on non-English pairs
5. **Other pair tasks** - QA, STS, paraphrase detection

---

## Citation

This research is part of the Resonance Protocol project.
- GitHub: https://github.com/nick-yudin/resonance-protocol
- Website: https://resonanceprotocol.org
