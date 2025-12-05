# M3c Series: Lessons Learned

## Executive Summary

M3c series proved that **HDC vectors can transfer semantic knowledge** between different neural architectures. A simple MLP learned sentiment classification from ternary vectors alone, achieving 73.4% accuracy without ever seeing text.

However, attempts to optimize beyond 59% transfer efficiency using curriculum learning **failed catastrophically**, teaching us important lessons about technique transferability.

---

## What Works ✅

### M3c″ Proved:

#### 1. HDC Vectors Encode Transferable Semantics
```
Teacher (DistilBERT): learns from TEXT
     ↓
HDC Encoding: text → [1, -1, 0, 1, 0, -1, ...] (4096d ternary)
     ↓  
Student (MLP): learns from HDC ONLY

Result: 73.4% accuracy (vs 86.8% teacher)
```

#### 2. Ternary Quantization Works
- Values: only {-1, 0, +1}
- Compression: 32× vs float32
- Information preserved: enough for 59% transfer efficiency

#### 3. Cross-Architecture Transfer is Possible
- Teacher: Transformer (DistilBERT, 66M params)
- Student: MLP (2.2M params)
- No shared architecture, no shared weights
- Only shared: HDC vectors + labels

#### 4. Simple Approach is Robust
- Random projection (not learned)
- Fixed threshold quantization
- Basic MLP architecture
- Standard training

---

## What Doesn't Work ❌

### M3c‴ v3 Showed:

#### 1. Curriculum Learning Doesn't Transfer to All Contexts

| Context | Works? |
|---------|--------|
| LLM fine-tuning (M2.5e) | ✅ Yes |
| MLP from scratch (M3c‴) | ❌ No |

**Why:** LLMs have pre-trained knowledge buffer. MLPs start empty.

#### 2. Easy/Hard Split ≠ Curriculum Learning

```
Real curriculum (M2.5e):
  Same dataset, sorted by difficulty
  [easy₁, easy₂, ..., hard₁, hard₂]

What we did (M3c‴):
  Two different datasets
  Dataset_A (easy) → Dataset_B (hard)
```

This caused distribution shift, not curriculum learning.

#### 3. Multiple Changes = Undebuggable

Changed simultaneously:
- HDC dim: 4096 → 10000
- Curation: confidence → kmeans  
- Training: random → curriculum
- LR: cosine → constant

Result: -16.5% transfer efficiency (catastrophic failure)

---

## Key Insights

### 1. Technique Transferability is Not Automatic

Just because technique X works in context A doesn't mean it works in context B.

**M2.5e context:**
- Pre-trained 1.1B parameter LLM
- Text input
- Fine-tuning existing knowledge

**M3c context:**
- Randomly initialized MLP
- HDC ternary input
- Learning from scratch

### 2. Simple Baselines Are Valuable

M3c″'s simple approach (59% efficiency) is:
- Reproducible
- Understandable
- Robust to hyperparameters

Clever optimizations can make things worse.

### 3. Negative Results Are Data

M3c‴ failure taught us:
- What NOT to do for MLP training
- Boundaries of curriculum learning applicability
- Importance of incremental experimentation

---

## Baseline Performance

**M3c″ (to beat):**
```
Transfer Efficiency: 59.2%
Student Accuracy: 73.4%
HDC Dimension: 4096
Examples: 500
```

---

## Next Steps to Try

### Priority 1: Low-Risk Improvements

| Change | Expected Impact | Risk |
|--------|-----------------|------|
| Soft labels (probabilities) | +10-15% | Low |
| More examples (500→2000) | +5-10% | Low |
| Warmup + constant LR | +3-5% | Low |

### Priority 2: Medium-Risk Changes

| Change | Expected Impact | Risk |
|--------|-----------------|------|
| Larger HDC (20000d) | +5-10% | Medium |
| Learned projection | +5-10% | Medium |
| Deeper student | +3-5% | Medium |

### Priority 3: Different Approaches

| Change | Expected Impact | Risk |
|--------|-----------------|------|
| Contrastive learning | Unknown | High |
| Multiple teachers | +10-20% | High |
| Attention-based student | Unknown | High |

---

## Experimental Protocol (Updated)

Based on M3c‴ failure, new protocol:

1. **One change at a time**
   - Never change multiple variables simultaneously
   - Compare directly to M3c″ baseline

2. **Validate assumptions**
   - Don't assume technique transfers
   - Test on small scale first

3. **Document everything**
   - Including failures
   - With analysis of why

4. **Simple first**
   - Start with obvious improvements
   - Escalate complexity only if needed

---

## Summary Table

| Experiment | Transfer Efficiency | Status | Key Learning |
|------------|---------------------|--------|--------------|
| M3c″ | 59.2% | ✅ SUCCESS | HDC transfer works |
| M3c‴ v3 | -16.5% | ❌ FAILED | Curriculum doesn't transfer to MLP |

**Current best: M3c″ at 59.2%**

**Target: 75%+**
