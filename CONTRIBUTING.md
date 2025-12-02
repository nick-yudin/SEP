# Contributing to Resonance Protocol

Thank you for your interest in Resonance. This is a research project exploring an alternative path to AI — distributed, energy-efficient, independent.

---

## Philosophy

Before contributing, understand what we're building:

1. **This is research, not a product.** Some things work, some are speculation. We're honest about the difference.

2. **Honesty over hype.** Don't oversell results. If something doesn't work, say so.

3. **Long-term thinking.** We're building for hardware that doesn't exist yet. Quick wins are nice, but we're playing a long game.

4. **English for code and docs.** All public artifacts are in English for global accessibility.

---

## What We Need Help With

### Immediate (Anyone can start)

| Area | Description | Skills needed |
|------|-------------|---------------|
| **Testing** | Run benchmarks on different hardware, report results | Basic Python |
| **Documentation** | Improve READMEs, add examples, fix typos | Technical writing |
| **Visualization** | Build interactive web demo of benchmark | JavaScript, React |

### Research (Requires expertise)

| Area | Description | Skills needed |
|------|-------------|---------------|
| **Ternary quantization** | Implement BitNet-style quantization for embeddings | ML, quantization |
| **Distributed training** | DiLoCo experiments on edge devices | Distributed systems, ML |
| **HDC integration** | Hyperdimensional computing for semantic vectors | HDC research |
| **Governance design** | How to make "no one controls" real | Mechanism design |

### Long-term (Requires connections)

| Area | Description | Who can help |
|------|-------------|--------------|
| **Hardware partnerships** | Memristor, neuromorphic chip researchers | Academics, labs |
| **Sovereign state contacts** | Europe, BRICS, Middle East AI initiatives | Policy people |
| **Research funding** | Grants, not VC | Foundation contacts |

---

## How to Contribute

### 1. Start Small

- Run `quick_demo.py`, understand how it works
- Read the [Technical Specification](docs/01_specs/v1.0_current/spec_v1_final.md)
- Try the benchmark on your hardware

### 2. Open an Issue First

Before writing code:
- Check existing issues
- Open a new issue describing what you want to do
- Wait for feedback (we might have context you don't)

### 3. Code Standards

```python
# Clear variable names
semantic_threshold = 0.15  # not: st = 0.15

# Comments explain WHY, not WHAT
# Good: "Threshold tuned for conversational text, may need adjustment for technical domains"
# Bad: "Set threshold to 0.15"

# Type hints where helpful
def compute_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    ...
```

### 4. Pull Request Process

1. Fork the repository
2. Create a branch: `git checkout -b feature/your-feature`
3. Make changes with clear commits
4. Update relevant README if needed
5. Open PR with description of what and why

---

## What NOT to Contribute

- **Hype or marketing language** — We're allergic to it
- **Unrealistic benchmarks** — If it seems too good, it probably is
- **Scope creep** — Stay focused on semantic events, not general AI
- **Vendor lock-in** — No dependencies on specific cloud providers

---

## Communication

- **GitHub Issues** — Bug reports, feature requests
- **GitHub Discussions** — Questions, ideas, brainstorming
- **Email** — [1@resonanceprotocol.org](mailto:1@resonanceprotocol.org) for private matters
- **Twitter** — [@rAI_stack](https://twitter.com/rAI_stack) for public updates

---

## Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes when their code ships
- Website credits page (coming)

We don't have money to pay contributors yet. This is a labor of belief in a different future.

---

## Questions?

Open an issue or email [1@resonanceprotocol.org](mailto:1@resonanceprotocol.org).

We're a small team and may not respond instantly, but we read everything.

---

*"The clock stops. The resonance begins."*
