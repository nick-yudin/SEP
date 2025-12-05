# HDC Pair Encoding: Expert Consultation Round 2

## Context
We're building Resonance Protocol — distributed AI where nodes communicate via ternary HDC vectors {-1, 0, +1}.

## What Works Well
**Single-sentence tasks achieve 87-93% of teacher performance:**
- SST-2 (sentiment, 2 classes): 77% student / 88% teacher = 87.5% ratio
- AG News (topics, 4 classes): 86.6% / 93.2% = 92.9% ratio

## The Problem
**Sentence-pair tasks (NLI) hit a ceiling around 65-66%:**
- Teacher (RoBERTa-large-mnli): 91.4%
- Best student so far: 65.6%
- Ratio: 71.8% (vs 87-93% for single sentences)

---

## Experiments Conducted

### Phase 1: Ablation Study
**Question:** Where is information lost — projection, quantization, or features?

| Config | Description | Accuracy |
|--------|-------------|----------|
| A | 1536-float (no HDC) | 54.6% |
| B | 4096-float (projection only) | 51.6% |
| C | 1536-ternary (quantization only) | 48.8% |
| D | 4096-ternary (full HDC) | 52.6% |

**Finding:** Baseline A is only 54.6% — the encoder/features are the bottleneck, not HDC!

---

### Phase 2: NLI-Tuned Encoder
**Question:** Does using an NLI-specialized encoder help?

| Encoder | Embedding | Float (A) | HDC (D) |
|---------|-----------|-----------|---------|
| all-MiniLM-L6-v2 | 384d | 53.0% | 50.4% |
| nli-distilroberta-base-v2 | 768d | 66.6% | 64.4% |
| **nli-mpnet-base-v2** | 768d | **67.8%** | **63.8%** |

**Finding:** NLI encoder gives +14.8% improvement! Encoder WAS the bottleneck.

---

### Phase 3: Project-First-Bind-Later
**Question:** Does doing HDC operations in high-dimensional space help?

Based on expert advice that "math should happen in HDC space, not dense space."

| Strategy | Description | Float | Ternary |
|----------|-------------|-------|---------|
| 0_baseline_concat | [P,H,P-H,P*H] → project | 64.0% | 61.4% |
| 1_project_bundle | P_hdc + H_hdc + P_hdc*H_hdc | 55.4% | 55.6% |
| 2_project_permute | roll(P_hdc) * H_hdc | 54.0% | 54.0% |
| 3_project_tanh | tanh before binding | 57.2% | 54.6% |
| 4_project_tanh_permute | tanh + permute | 53.6% | 55.4% |
| **5_two_vectors** | [P_hdc, H_hdc, diff, prod] | **67.6%** | **65.6%** |
| 6_two_vectors_tanh | same with tanh | 66.8% | 64.6% |

**Finding:** 
- ❌ Binding strategies (bundle, permute) made things WORSE (-5 to -7%)
- ✅ Two-vectors approach works best (+4.2% over baseline)

---

## Current Best Pipeline

```
Premise → NLI-MPNet (768d) → Random Projection → P_hdc (4096d)
Hypothesis → NLI-MPNet (768d) → Random Projection → H_hdc (4096d)

Features = [P_hdc, H_hdc, P_hdc - H_hdc, P_hdc * H_hdc]  # 16384d
→ Ternary Quantization
→ MLP (3 layers)
→ 65.6% accuracy
```

---

## Summary of Findings

| What We Tried | Result | Conclusion |
|---------------|--------|------------|
| General encoder (MiniLM) | 50-54% | ❌ Doesn't understand NLI |
| NLI encoder (MPNet) | 63-67% | ✅ +14% improvement |
| HDC binding (P + H + P*H) | 54-56% | ❌ Loses information |
| HDC permutation (asymmetry) | 54% | ❌ Doesn't help |
| tanh non-linearity | 54-57% | ❌ Doesn't help |
| Two separate HDC vectors | 65.6% | ✅ Best so far |

---

## The Gap

```
Teacher: 91.4%
Best HDC: 65.6%
Gap: 25.8%

For comparison, single-sentence gap:
Teacher: 88-93%
HDC: 77-87%
Gap: 6-11%
```

**The pair-encoding gap is 2-4x larger than single-sentence gap.**

---

## Questions for Experts

1. **Why did Project-First-Bind-Later fail?**
   - All three experts recommended this approach
   - But bundling/binding made results WORSE
   - Is our implementation wrong, or is the approach fundamentally flawed for NLI?

2. **Is 65-66% the ceiling for this approach?**
   - Two-vectors works but requires 16384d (large for protocol)
   - Is there a way to achieve similar results with smaller vectors?

3. **What about role-filler binding?**
   - We haven't tried explicit role vectors (PREMISE_ROLE, HYPOTHESIS_ROLE)
   - Would this help capture the asymmetric relationship?

4. **Should we try learned projections?**
   - Random projection preserves distances but maybe not relational structure
   - Would training the projection matrix on NLI help?

5. **Is the problem fundamental?**
   - NLI requires understanding logical relationships (entailment, contradiction)
   - Can this be captured in ANY fixed-dimensional vector representation?
   - Or does it inherently require attention-like mechanisms?

6. **Practical question for Resonance Protocol:**
   - Should we accept that pair tasks need different handling?
   - Maybe HDC for encoding, something else for relations?

---

## Constraints Reminder

For Resonance Protocol we need:
- Ternary output {-1, 0, +1} (for efficient transmission)
- Compact vectors (ideally 4096-8192d, 16384d is borderline acceptable)
- Deterministic encoding (same input → same output)
- No shared model requirement between nodes

---

## Code Reference

### Current Best Encoder
```python
class TwoVectorHDCEncoder:
    def __init__(self, hdc_dim=4096, seed=42):
        self.encoder = SentenceTransformer('nli-mpnet-base-v2')
        self.semantic_dim = 768
        
        np.random.seed(seed)
        self.projection = np.random.randn(self.semantic_dim, hdc_dim)
        self.projection /= np.linalg.norm(self.projection, axis=0)
    
    def encode_pair(self, premise, hypothesis):
        # Get semantic embeddings
        p_emb = self.encoder.encode(premise)
        h_emb = self.encoder.encode(hypothesis)
        
        # Project to HDC space
        p_hdc = p_emb @ self.projection
        h_hdc = h_emb @ self.projection
        
        # Create features (keep both vectors!)
        diff = p_hdc - h_hdc
        prod = p_hdc * h_hdc
        features = np.concatenate([p_hdc, h_hdc, diff, prod])  # 16384d
        
        # Ternary quantization
        thr = 0.3 * np.std(features)
        ternary = np.where(features > thr, 1,
                          np.where(features < -thr, -1, 0))
        return ternary
```

### What We Tried That Didn't Work
```python
# Binding approach (WORSE than baseline)
def project_then_bind(p_emb, h_emb, projection):
    p_hdc = p_emb @ projection
    h_hdc = h_emb @ projection
    binding = p_hdc * h_hdc
    return p_hdc + h_hdc + binding  # 4096d — loses information!

# Permutation for asymmetry (DIDN'T HELP)
def with_permutation(p_hdc, h_hdc):
    p_rotated = np.roll(p_hdc, shift=1)
    binding = p_rotated * h_hdc
    return p_hdc + h_hdc + binding
```

---

## What We're Looking For

1. **Diagnosis:** Why did the recommended approaches fail?
2. **Direction:** Should we continue optimizing HDC for pairs, or accept the limitation?
3. **Concrete next step:** If continuing, what specific experiment should we run?

Thank you for your expertise!
