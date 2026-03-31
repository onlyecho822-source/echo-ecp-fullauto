# echo-ecp-fullauto

> **A governed reasoning engine that runs any problem through five adversarial perspectives, measures convergence, and returns a structured Truth Partition — with zero external dependencies.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-4.0-green.svg)](echo_system_v4.py)
[![No Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen.svg)](echo_system_v4.py)
[![Tests](https://img.shields.io/badge/Tests-21_passing-success.svg)](tests/)

---

## What this is

Most AI systems answer questions. This system interrogates them.

**echo-ecp-fullauto** implements the **Echo Convergence Protocol (ECP)** — a reasoning architecture built on five adversarial primitives that challenge every input from five distinct angles, measure when the perspectives stop producing new insight, and force a structured output before returning anything.

It does not hallucinate confidence. It labels what it does not know. It flags when the output is too vague to act on. It tells you when convergence might be false.

**Built and validated by a dual-AI loop** — Claude (strategist) and Manus (executor) — across five review sessions, three validation tests, and a Devil pass before every commit.

---

## Quick start

```bash
git clone https://github.com/onlyecho822-source/echo-ecp-fullauto
cd echo-ecp-fullauto
python echo_system_v4.py
```

No pip install. No API keys. No configuration. Just Python 3.8+.

**Optional** (semantic convergence):
```bash
pip install sentence-transformers
```

---

## How it works

Every input passes through five primitives in sequence:

| Primitive | Question | Role |
|-----------|----------|------|
| **Echo** | How does it fit together? | Maps structure and dependencies |
| **God** | What are we not considering? | Expands beyond current frame (capped at 5) |
| **Devil** | How does this break? | Attacks assumptions adversarially |
| **Light** | What is being obscured? | Surfaces hidden load-bearing assumptions |
| **Nathan** | What is the move? | Derives action from all prior passes |

The **ECP loop** runs passes until two consecutive passes converge (Jaccard ≥ 72%, or semantic similarity if `sentence-transformers` is installed). False convergence is detected by scanning for shared unchallenged assumptions across passes.

Every output is a **Truth Partition** — five required fields that must all be present or the output is rejected:

```
TRUTH PARTITION
├── Invariant      — claims that survived all passes
├── Evidence       — how many passes, convergence score, method
├── Uncertainty    — confidence level, shared assumptions flagged
├── Failure Modes  — what could make this output wrong
└── Action         — derived from actual claims, not hardcoded
```

Claims are labeled:
- **Validated** — directly addresses the input
- **Plausible** — credible but unverified
- **UnresolvedDirectional** — directional, needs follow-up
- **DeceptionIndicating** — Devil/Light findings, attack before acting
- **Unsupported** — injected adversarial constraints

---

## Four flows

```python
from echo_system_v4 import run

# Standard — new complex decision
result = run("What is the highest-leverage action to deploy this system?")

# Fast — time pressure
result = run("Should we ship now?", {"time_pressure": True})

# Research — unknown domain  
result = run("What revenue model fits this product?", {"unknown_domain": True})

# Audit — review existing work
result = run("The auth system is missing rate limiting", {"audit": True})
```

**Flow priority:** unknown domain > audit > time pressure > standard

---

## What v4 adds over v3

| Feature | v3.1 | v4.0 |
|---------|------|------|
| SubstantiveValidator | ✗ | ✅ Content quality checks |
| GraphMemory | ✗ | ✅ Triple store + temporal queries |
| Semantic convergence | Jaccard only | ✅ Embeddings + Jaccard fallback |
| Context threading | ✗ | ✅ Primitives share state across passes |
| Verb validation | ✗ | ✅ Action must contain concrete verb |
| Evidence-Invariant check | ✗ | ✅ Evidence must support Invariant |

---

## Run the tests

```bash
# All 21 tests
python tests/test_gate.py
python tests/test_convergence.py
python tests/test_partition.py
python tests/test_v4.py
```

Or trigger the CI workflow manually in GitHub Actions.

---

## What this is not

- **Not a chatbot.** It does not generate creative content or answer factual questions.
- **Not a finished product.** Primitives generate directional claims, not verified facts. Operator grounds the output.
- **Not a replacement for reasoning.** It amplifies the operator. It does not replace them.

---

## Architecture

```
INPUT
  └── InputSpec gate (question / proposition / audit statement)
        └── FlowSelector (priority routing)
              └── ECP Loop
                    ├── Primitives run in sequence
                    ├── Jaccard / semantic convergence check
                    ├── Variation enforcement (≥1 new claim per pass)
                    └── False convergence scan
                          └── Truth Partition (5 required fields)
                                ├── Structural validator
                                ├── SubstantiveValidator (v4)
                                └── GraphMemory storage (v4)
```

Full spec: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## Roadmap

| Version | Status | Focus |
|---------|--------|-------|
| v3.1 | ✅ Shipped | OOP primitives, 5-label schema, low-signal detection |
| v4.0 | ✅ Shipped | SubstantiveValidator, GraphMemory, semantic convergence |
| v3.2 | Next patch | Low-signal threshold fix, batch mode, JSON output flag |
| v5.0 | Planned | LLM integration per primitive, multi-agent coordination |

Full roadmap: [docs/ROADMAP.md](docs/ROADMAP.md)

---

## File structure

```
echo-ecp-fullauto/
├── echo_system_v3.py      v3.1 engine (stable baseline)
├── echo_system_v4.py      v4.0 engine (current)
├── tests/
│   ├── test_gate.py       8 input gate tests
│   ├── test_convergence.py 7 convergence tool tests
│   ├── test_partition.py  6 Truth Partition tests
│   └── test_v4.py         14 v4-specific tests
├── docs/
│   ├── ARCHITECTURE.md    Full spec + extension points
│   ├── EVOLUTION.md       v3.1 → v4.0 changes + honest stubs list
│   └── ROADMAP.md         v3.2 → v5.0 path
├── .echo/config.yaml      Echo nervous system node registration
└── .github/workflows/
    └── test.yml           Manual CI (no auto-trigger)
```

---

## Built by

**Nathan Poinsette** (∇θ Operator) — Army veteran, systems engineer, founder.
Echo Universe ecosystem — `github.com/onlyecho822-source`

Developed through a dual-AI collaboration loop:
- **Claude** (Anthropic) — strategist, reviewer, adversarial auditor
- **Manus** — executor, builder, first-pass author

Every commit passed a Devil review before merging.

---

## License

MIT — use it, extend it, build on it.

---

*∇θ — chain sealed, truth preserved.*
