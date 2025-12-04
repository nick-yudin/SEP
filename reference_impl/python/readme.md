# SEP — Python Reference Implementation

> Semantic event filtering for distributed edge intelligence.

---

## What This Demonstrates

This implementation demonstrates the core SEP concepts in controlled environments:

| Concept | File | What it shows |
|---------|------|---------------|
| Semantic filtering | `quick_demo.py` | 90%+ reduction in synthetic test scenarios |
| Procrustes alignment | `basic/alignment.py` | Cross-model vector space alignment (toy example) |
| Mesh propagation | `basic/gossip.py` | Simulated P2P event propagation (10 nodes) |
| Wire protocol | `basic/sender.py`, `basic/receiver.py` | Basic TCP transmission of semantic events |
| Benchmark | `benchmarks/mqtt_vs_resonance.py` | Comparison with traditional approach (synthetic data) |

---

## Quick Start

```bash
# Install dependencies
pip install sentence-transformers numpy

# Run interactive demo
python quick_demo.py
```

The demo will:
1. Load a sentence transformer model
2. Ask you to type sentences
3. Show which sentences trigger transmission (semantic change) vs silence (similar meaning)

---

## Project Structure

```
reference_impl/python/
├── quick_demo.py           # Interactive demo — start here
├── basic/
│   ├── README.md           # Detailed explanation of each example
│   ├── alignment.py        # Procrustes alignment between vector spaces
│   ├── gossip.py           # 10-node mesh simulation
│   ├── sender.py           # TCP sender with semantic filtering
│   └── receiver.py         # TCP receiver
└── benchmarks/
    ├── README.md           # Benchmark methodology
    ├── mqtt_vs_resonance.py # Main comparison benchmark
    └── results/
        └── comparison.json  # Saved benchmark results
```

---

## Examples

### 1. Semantic Filtering (quick_demo.py)

```python
# Core concept: only transmit when meaning changes
if cosine_distance(current_vector, last_vector) > THRESHOLD:
    transmit()  # Meaningful change — send event
else:
    silence()   # Similar meaning — stay quiet
```

Try typing:
- "The cat sat on the mat" → TRANSMIT (new topic)
- "A cat is sitting on a mat" → SILENCE (same meaning)
- "The weather is nice today" → TRANSMIT (different topic)

### 2. Procrustes Alignment (basic/alignment.py)

```python
# Different models have different vector spaces
# Procrustes finds rotation matrix R to align them

R = orthogonal_procrustes(anchors_model_A, anchors_model_B)
aligned_vector = foreign_vector @ R
```

This suggests potential for heterogeneous meshes. Real-world validation needed.

### 3. Mesh Propagation (basic/gossip.py)

```python
# Gossip protocol: events spread P2P
# Each node tells random neighbors
# No central server needed

for neighbor in random.sample(peers, k=3):
    neighbor.receive(event)
```

### 4. Benchmark (benchmarks/mqtt_vs_resonance.py)

Compares traditional approach (send everything) vs SEP (send on meaning change):

```
Traditional (MQTT-style):
  Messages sent: 1,847
  Total bandwidth: 2.3 MB

SEP:
  Events sent: 23
  Total bandwidth: 34 KB
  Reduction: 98.7%
```

---

## Configuration

Key parameters in the code:

```python
SEMANTIC_THRESHOLD = 0.15    # Cosine distance threshold for "meaningful change"
EMBEDDING_DIM = 384          # Dimension of sentence embeddings
MODEL_NAME = "all-MiniLM-L6-v2"  # Sentence transformer model
```

Adjust `SEMANTIC_THRESHOLD`:
- Lower (0.05) = more sensitive, more transmissions
- Higher (0.3) = less sensitive, fewer transmissions

---

## Requirements

- Python 3.8+
- sentence-transformers
- numpy
- (optional) torch with CUDA for faster embeddings

```bash
pip install sentence-transformers numpy
```

---

## Future: Ternary Computing

Current implementation uses float32 vectors (1536 bytes per embedding).

Future optimization path:
1. **Ternary quantization** — {-1, 0, +1} reduces to 96 bytes
2. **HDC integration** — Hyperdimensional computing for native ternary
3. **BitNet-style inference** — 10-100× speedup on right hardware

This requires hardware that doesn't exist yet in production. The protocol is designed to be ready when it arrives.

---

## Running on Edge Devices

Tested informally on:
- Raspberry Pi 4/5 — runs, ~2 sec per embedding
- Jetson Nano — runs, ~0.5 sec per embedding
- Jetson Orin — runs, ~0.1 sec per embedding

Note: These are preliminary tests, not production benchmarks.

---

## Next Steps

1. **Run quick_demo.py** — understand semantic filtering
2. **Read basic/README.md** — learn each component
3. **Run benchmark** — see quantified results
4. **Experiment** — try different thresholds, models, scenarios

---

## Contributing

See [main README](../../README.md) for contribution guidelines.

Key areas needing help:
- Ternary quantization implementation
- More embedding models (multilingual, domain-specific)
- Hardware benchmarks on different devices
- Integration with Gonka.ai or similar projects

---

## Links

- [Main Repository](https://github.com/nick-yudin/SEP)
- [Technical Specification](../../docs/01_specs/v1.0_current/spec_v1_final.md)
- [Website](https://seprotocol.ai)