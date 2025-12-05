# M3c‴ v3 Failure Analysis

## What We Tried

Applied insights from M2.5c and M2.5e experiments:

1. **HDC K-means curation** (from M2.5c) — cluster-based selection instead of confidence threshold
2. **Sharp curriculum** (from M2.5e) — easy examples first (epochs 1-15), then add hard (epochs 16-50)
3. **Constant LR** (from M2.5e) — no learning rate decay, fixed at 5e-4
4. **Difficulty scoring** — distance from centroid = difficulty

## What Happened

```
Student accuracy: 53% → 47%  (WORSE than before training!)
Transfer efficiency: -16.5%  (negative = unlearning)

Model behavior: Oscillated around 50% for all 50 epochs
               Never showed any learning signal
```

## Why It Failed

### Problem 1: Different Contexts

| M2.5e (worked) | M3c‴ (failed) |
|----------------|---------------|
| Fine-tuning LLM (TinyLlama 1.1B) | Training MLP from scratch |
| Model already knew language | Model knew nothing |
| Curriculum refined existing knowledge | Curriculum confused empty model |
| Text input (rich signal) | HDC ternary input (compressed) |

### Problem 2: Easy/Hard Split Created Different Distributions

```python
# What we did:
easy_examples = nearest_to_centroid(all_examples)   # "typical" examples
hard_examples = farthest_from_centroid(all_examples) # "boundary" examples

# The problem:
# - Easy and Hard are fundamentally DIFFERENT distributions
# - This is NOT curriculum learning
# - This is training on one distribution, then switching to another
```

In M2.5e, curriculum meant **sorting one dataset** by difficulty.
In M3c‴, we created **two separate datasets** with different statistical properties.

### Problem 3: Catastrophic Forgetting

When we added hard examples at epoch 15:
- Model had learned (somewhat) on easy examples
- Hard examples had different distribution
- Model forgot easy patterns while failing to learn hard ones
- Result: worse than random

### Problem 4: No Pre-training Buffer

LLMs have massive pre-trained knowledge that acts as a buffer:
- Curriculum learning adjusts this knowledge
- Even "forgetting" doesn't go to zero

MLPs from scratch have no buffer:
- All knowledge comes from training data
- Distribution shift = catastrophic failure

## What M2.5e Actually Proved

M2.5e showed that for **LLM fine-tuning**:
- Sharp curriculum (easy → hard) beats gradual
- Constant LR preserves adaptability
- Distance from centroid correlates with difficulty

These findings were **specific to LLM fine-tuning context**.

## Lessons Learned

### 1. Context Matters
Techniques that work in one context don't automatically transfer:
- LLM fine-tuning ≠ MLP training from scratch
- Text input ≠ HDC input
- Pre-trained ≠ random initialization

### 2. One Change at a Time
We changed too many variables:
- HDC dimension (4096 → 10000)
- Curation method (confidence → kmeans)
- Training strategy (random → curriculum)
- LR schedule (cosine → constant)

Should have tested each in isolation.

### 3. Easy/Hard Split ≠ Curriculum
True curriculum learning requires:
- Single continuous distribution
- Ordering by difficulty
- Gradual exposure

What we did:
- Two separate distributions
- Binary split
- Abrupt transition

### 4. Validate Assumptions
We assumed "curriculum works" without validating:
- Does it work for MLP?
- Does it work for HDC input?
- Does it work without pre-training?

Answer to all: **No**.

## Recommendations for Future Experiments

1. **Return to M3c″ baseline** — it worked (59%)
2. **Test one improvement at a time**
3. **For MLP from scratch, consider:**
   - More data (not different data organization)
   - Soft labels (richer signal)
   - Larger model (more capacity)
   - Standard training (not curriculum)

## The Silver Lining

This failure taught us:
- M3c″ approach is more robust than we thought
- Curriculum learning has specific requirements
- Simple approaches sometimes beat clever ones
- Negative results are valuable data
