# M3c: HDC Semantic Transfer Experiments

## Overview

This series proves that **semantic knowledge can be transferred between neural networks using only HDC (Hyperdimensional Computing) vectors**, without sharing any text.

## The Core Question

> Can a Student model learn sentiment classification from ternary HDC vectors alone, **never seeing any text**?

**Answer: Yes.** M3c″ achieved 73.4% accuracy with 59% transfer efficiency.

---

## Experiments Summary

| Experiment | Goal | Result | Transfer Efficiency |
|------------|------|--------|---------------------|
| [M3c″](m3c_double_prime/) | Prove HDC transfer works | ✅ SUCCESS | **59.2%** |
| [M3c‴ v3](m3c_triple_prime_v3/) | Optimize with curriculum | ❌ FAILED | -16.5% |

---

## M3c″: The Breakthrough

```
┌─────────────────┐     HDC Encode      ┌─────────────────┐
│    Teacher      │ ──────────────────► │  Knowledge      │
│  (DistilBERT)   │                     │  Packet         │
│  Learns: TEXT   │                     │  {-1,0,+1}      │
└─────────────────┘                     └────────┬────────┘
        │                                        │
        │ 86.8% accuracy                         │ 500 examples
        │                                        │ 4096d ternary
        ▼                                        ▼
┌─────────────────┐                     ┌─────────────────┐
│   Test Set      │                     │    Student      │
│   (TEXT)        │                     │    (MLP)        │
│                 │                     │  Learns: HDC    │
└─────────────────┘                     └─────────────────┘
                                                │
                                                │ 73.4% accuracy
                                                │ NEVER SAW TEXT
                                                ▼
                                        ┌─────────────────┐
                                        │   Test Set      │
                                        │   (HDC encoded) │
                                        └─────────────────┘
```

### Key Results

| Metric | Value |
|--------|-------|
| Teacher accuracy | 86.8% |
| Student accuracy | 73.4% |
| Transfer efficiency | 59.2% |
| Student saw text | **ZERO** |

---

## Why This Matters

### 1. Meaning is Universal
Semantics can be encoded as numbers {-1, 0, +1}, independent of:
- Language
- Model architecture
- Training framework

### 2. Massive Compression
```
Float32 embedding: 384 × 4 = 1,536 bytes
HDC ternary (4096d): 4096 × 2 bits = 1,024 bytes
With packing: ~350 bytes per example
```

### 3. Architecture Independence
- Teacher: Transformer (66M params)
- Student: MLP (2.2M params)
- Transfer works despite 30× size difference

### 4. Foundation for Distributed AI
Nodes can share **meaning**, not models:
- Privacy preserved (no raw text)
- Bandwidth efficient (ternary vectors)
- Model-agnostic (any architecture can participate)

---

## Lessons Learned

See [LESSONS_LEARNED.md](LESSONS_LEARNED.md) for detailed analysis.

**Key takeaway:** Simple approaches work. Clever optimizations can backfire.

---

## Current Status

**Baseline to beat:** M3c″ at 59.2% transfer efficiency

**Target:** 75%+ transfer efficiency

**Next experiments planned:**
1. Soft labels (teacher probabilities instead of hard labels)
2. More training examples (500 → 2000)
3. Larger HDC dimension (4096 → 20000)

---

## File Structure

```
m3c_hdc_transfer/
├── README.md                    # This file
├── LESSONS_LEARNED.md           # Key insights from all experiments
├── m3c_double_prime/            # ✅ SUCCESS
│   ├── README.md
│   ├── teacher.ipynb
│   ├── student.ipynb
│   └── results/
│       ├── teacher_results.json
│       ├── student_results.json
│       └── student_results.png
└── m3c_triple_prime_v3/         # ❌ FAILED (documented)
    ├── README.md
    ├── FAILURE_ANALYSIS.md
    ├── teacher.ipynb
    ├── student.ipynb
    └── results/
        ├── teacher_results.json
        ├── student_results.json
        └── student_results.png
```

---

## Running the Experiments

### Requirements
- Google Colab with GPU (T4 sufficient)
- Firebase Realtime Database credentials
- Python packages: transformers, sentence-transformers, firebase-admin

### Steps

1. **Teacher notebook:**
   - Insert Firebase credentials
   - Run all cells
   - Wait for "Knowledge packet uploaded"

2. **Student notebook:**
   - Insert same Firebase credentials
   - Run all cells
   - View results

### Firebase Setup

Replace `"INSERT KEY HERE"` in notebooks with your Firebase service account JSON.

---

## Citation

Part of the SEP (Semantic Event Protocol) research project.

Repository: https://github.com/nick-yudin/SEP
