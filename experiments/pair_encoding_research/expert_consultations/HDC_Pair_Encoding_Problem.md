# HDC Pair Encoding Bottleneck: Full Problem Description

## Context

We're building Resonance Protocol — a system for distributed AI where nodes communicate via semantic HDC (Hyperdimensional Computing) vectors instead of raw data. The core idea: encode meaning into ternary vectors {-1, 0, +1}, transmit only when meaning changes.

**What works:** Single-sentence tasks achieve 85-93% of teacher model performance.
**What doesn't:** Sentence-pair tasks hit a ~45-54% ceiling regardless of teacher quality.

---

## The Experimental Setup

### Pipeline
```
Text → Sentence Transformer (384d) → HDC Projection (4096d) → Ternary Quantization → Student MLP
```

### Components
1. **Semantic Encoder:** `all-MiniLM-L6-v2` (384 dimensions)
2. **HDC Projection:** Random matrix (input_dim → 4096d)
3. **Quantization:** Values → {-1, 0, +1} based on threshold
4. **Student:** 3-layer MLP (~2.2M params)

### Tasks Tested
| Task | Type | Teacher | Student | Ratio |
|------|------|---------|---------|-------|
| SST-2 | Single sentence (sentiment) | 88% | 77% | 87.5% ✅ |
| AG News | Single sentence (4 topics) | 93% | 87% | 92.9% ✅ |
| MNLI | Sentence pairs (NLI) | 91% | 43-54% | 47-59% ❌ |

---

## The Core Problem

### Natural Language Inference (NLI) Task

Given two sentences, classify their relationship:
- **Entailment:** Premise implies hypothesis ("A man sleeps" → "A person rests")
- **Contradiction:** Premise contradicts hypothesis ("A man sleeps" → "A man runs")
- **Neutral:** No clear logical relation ("A man sleeps" → "The man is tired")

### Why It's Hard for HDC

The relationship is NOT in either sentence alone — it's in HOW they relate.

```python
# Current approach (concatenation)
premise_emb = encode("A man is sleeping")      # 384d vector
hypothesis_emb = encode("A person is resting") # 384d vector
combined = concat([premise_emb, hypothesis_emb])  # 768d
hdc_vec = random_projection(combined) → 4096d → ternary
```

**Problem:** Concatenation treats sentences as independent features. The "entailment" information exists in the RELATIONSHIP, not in the concatenation.

---

## What We Tried

### Experiment: Alternative Encoding Strategies

| Strategy | Formula | Accuracy | vs Baseline |
|----------|---------|----------|-------------|
| concat | [P, H] | 47.8% | baseline |
| difference | P - H | 51.8% | +4.0% |
| abs_diff | \|P - H\| | 43.2% | -4.6% |
| product | P * H | 42.6% | -5.2% |
| concat+diff | [P, H, P-H] | 52.0% | +4.2% |
| concat+diff+prod | [P, H, P-H, P*H] | 49.6% | +1.8% |
| **diff+prod** | **[P-H, P*H]** | **54.4%** | **+6.6%** 🏆 |
| symmetric | [\|P-H\|, P*H, P+H] | 48.8% | +1.0% |

### Key Observations

1. **Difference (P-H) helps:** Captures directional relationship
2. **Product alone hurts:** Too much noise without context
3. **diff+prod is best:** Combination captures both direction and interaction
4. **Adding raw embeddings hurts:** concat+diff+prod < diff+prod

### But Still Far From Goal
- Best result: 54.4%
- Teacher: 91.4%
- Ratio: 59.5% (vs 85-93% for single sentences)
- Gap: ~37% accuracy lost somewhere

---

## Hypotheses for the Bottleneck

### H1: Information Loss in Random Projection

Random projection is designed to preserve distances, but may lose specific relational features.

```
768d (diff+prod) → 4096d (random projection) → ternary
```

**Question:** Is random projection the right choice for relational data?

### H2: Ternary Quantization Too Aggressive

Converting float → {-1, 0, +1} may destroy subtle relationship signals.

```
Before: [-0.3, 0.8, -0.1, 0.5, ...]
After:  [-1, +1, 0, +1, ...]  # Fine-grained info lost
```

**Question:** Would 5-level or 7-level quantization help?

### H3: Semantic Encoder Not Designed for Relations

`all-MiniLM-L6-v2` creates embeddings for individual sentences, not for pairs. It may not encode relational semantics well.

**Question:** Would a model trained on NLI (e.g., sentence-transformers/nli-*) work better?

### H4: HDC Dimension Too Small for Relations

4096d might be enough for single concepts but not for relationships.

**Question:** Would 8192d or 16384d help?

### H5: Need Learned (Not Random) Projection

Random projection works for preserving distances but may not capture task-specific patterns.

**Question:** Would a learned projection matrix work better? (But this adds trainable parameters)

### H6: Asymmetry of Relations Not Captured

Entailment is asymmetric: P→H ≠ H→P. Current encoding may not capture this.

```
"All dogs are animals" → "Some animals are dogs" = Entailment
"Some animals are dogs" → "All dogs are animals" = Neutral
```

**Question:** Should we encode P→H and H→P differently?

### H7: Need Cross-Attention Mechanism

Transformers use attention to find which parts of P relate to which parts of H. Simple vector operations can't do this.

**Question:** Can we approximate cross-attention in HDC? Or do we need a different architecture?

---

## Constraints We Must Preserve

### For Resonance Protocol
1. **Ternary output required:** Final vectors must be {-1, 0, +1} for efficient transmission
2. **No shared model required:** Nodes may use different semantic encoders
3. **Compact representation:** Vectors should be transmittable (4096-8192 bits reasonable)
4. **Deterministic encoding:** Same input → same HDC vector (for protocol consistency)

### Acceptable Trade-offs
1. **Larger intermediate dimensions:** OK if final output is still compact
2. **More computation at encoding:** OK since encoding happens locally
3. **Task-specific projections:** OK if they can be shared as protocol parameters

---

## What We Need

### Ideal Solution
- Achieve 80%+ of teacher accuracy on MNLI (currently 54%)
- Preserve ternary output format
- Work without requiring same model on all nodes
- Be computationally reasonable for edge devices

### Minimum Viable Solution
- Achieve 70%+ accuracy on MNLI
- Understand WHY the ceiling exists
- Clear path to further improvement

---

## Questions for Discussion

1. **Is this a fundamental HDC limitation?** Or just a matter of finding the right encoding?

2. **Should we look at HDC literature?** Has anyone solved relational encoding in HDC?

3. **Cross-attention approximation?** Can attention-like mechanism be approximated with vector operations?

4. **Different semantic encoders?** Would NLI-specific encoders help?

5. **Learned projections?** Is it acceptable to have trainable components in HDC encoding?

6. **Alternative architectures?** Should we consider something beyond simple projections?

---

## Relevant Code

### Current HDC Encoder
```python
class HDCEncoder:
    def __init__(self, hdc_dim=4096, semantic_dim=384, seed=42):
        np.random.seed(seed)
        self.projection = np.random.randn(semantic_dim * 2, hdc_dim)
        self.projection /= np.linalg.norm(self.projection, axis=0)
        self.semantic_encoder = SentenceTransformer('all-MiniLM-L6-v2')
    
    def encode_pair(self, premise, hypothesis, quantize=True):
        p_emb = self.semantic_encoder.encode(premise)
        h_emb = self.semantic_encoder.encode(hypothesis)
        
        # Best strategy so far: diff + product
        combined = np.concatenate([p_emb - h_emb, p_emb * h_emb])
        
        hdc_vec = combined @ self.projection
        
        if quantize:
            threshold = 0.3 * np.std(hdc_vec)
            hdc_vec = np.where(hdc_vec > threshold, 1,
                       np.where(hdc_vec < -threshold, -1, 0))
        return hdc_vec
```

### Student Model
```python
class HDCClassifier(nn.Module):
    def __init__(self, hdc_dim=4096, hidden_dim=512, num_classes=3):
        super().__init__()
        self.classifier = nn.Sequential(
            nn.Linear(hdc_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim // 2, num_classes)
        )
```

---

## Resources

- **GitHub:** https://github.com/nick-yudin/resonance-protocol
- **Firebase:** Results stored in `sep_m4a_*` paths
- **Dataset:** GLUE MNLI (via HuggingFace datasets)
- **Semantic Encoder:** `sentence-transformers/all-MiniLM-L6-v2`

---

## Summary

**The problem:** HDC encoding loses relational information when encoding sentence pairs, hitting a 54% ceiling vs 91% teacher on MNLI.

**Best attempt so far:** `[P-H, P*H]` encoding achieves 54.4% (+6.6% over baseline concatenation).

**The gap:** 37% accuracy lost compared to teacher, vs only 7-13% for single-sentence tasks.

**The question:** How do we encode semantic RELATIONSHIPS, not just semantic CONTENT, in HDC vectors?
