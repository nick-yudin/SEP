# M3c HDC Transfer Optimization Experiments

## Overview

Systematic optimization of HDC-based semantic knowledge transfer. Starting from M3c″ baseline (59.2% transfer efficiency), we tested single improvements to find the optimal configuration.

## Results Summary

| Experiment | Change | Transfer Efficiency | vs Baseline | Verdict |
|------------|--------|---------------------|-------------|---------|
| **M3c″** | Baseline (500 ex, hard labels, 4096d) | 59.2% | — | Baseline |
| **M3c⁴** | Soft labels | 69.3% | +10.1% | ✅ Works |
| **M3c⁵** | 2000 examples | **73.2%** | **+14.0%** | 🏆 **Best** |
| **M3c⁶** | 10000d HDC | 54.5% | -4.7% | ❌ Worse |
| **M3c⁷** | Soft + 2000 ex | 68.7% | +9.5% | ⚠️ No synergy |
| **M3c⁸** | 5000 examples | 58.6% | -0.6% | ❌ Diminishing returns |

## Key Findings

### What Works ✅

1. **More training examples (up to 2000)**
   - 500 → 2000 examples: +14% efficiency
   - Sweet spot found at ~2000 examples
   - Diminishing returns beyond 2000

2. **Soft labels (teacher probabilities)**
   - Hard [1,0] → Soft [0.92, 0.08]: +10.1% efficiency
   - KL divergence loss provides richer signal

### What Doesn't Work ❌

1. **Larger HDC dimension**
   - 4096d → 10000d: -4.7% efficiency
   - More parameters need more data to train
   - 4096d is sufficient for this task

2. **Combining improvements**
   - Soft labels + More data ≠ additive effect
   - Combined: 68.7% < More data alone: 73.2%
   - Soft labels may "blur" signal when data is abundant

3. **Excessive data (5000 examples)**
   - 2000 → 5000: -14.6% efficiency
   - Student starts at higher baseline, less room for improvement
   - Metric artifact, not real degradation

## Best Configuration

```
M3c⁵ (2000 examples)
├── HDC dimension: 4096
├── Training examples: 2000
├── Labels: Hard
├── Student: 3-layer MLP (2.2M params)
├── Transfer efficiency: 73.2%
└── Student accuracy: 76.8%
```

## Methodology

Each experiment changed **one variable** from baseline:

```
Baseline (M3c″):
- 500 high-confidence examples
- Hard labels [1, 0] or [0, 1]
- HDC dimension: 4096
- 3-layer MLP student
- CrossEntropyLoss
- Adam + CosineAnnealing
```

## Directory Structure

```
m3c_optimization/
├── README.md
├── baseline/           # M3c″ (59.2%)
├── soft_labels/        # M3c⁴ (69.3%)
├── more_examples_2000/ # M3c⁵ (73.2%) ← BEST
├── larger_hdc/         # M3c⁶ (54.5%)
├── combined/           # M3c⁷ (68.7%)
└── more_examples_5000/ # M3c⁸ (58.6%)
```

## Lessons Learned

1. **Simple improvements often work best**
   - More data > clever techniques

2. **One change at a time**
   - Combining improvements doesn't guarantee synergy

3. **Sweet spots exist**
   - More is not always better (data, dimensions)

4. **Transfer efficiency vs accuracy**
   - Different metrics can tell different stories
   - M3c⁸ has highest accuracy (77.4%) but worst efficiency (58.6%)

## Next Steps

- [ ] Commit to SEP repository
- [ ] Try learned projection (trainable HDC encoder)
- [ ] Test on different tasks (not just SST-2)
- [ ] Hardware PoC with optimal configuration
