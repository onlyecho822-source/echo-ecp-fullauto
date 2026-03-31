# echo-ecp-fullauto

**Echo Convergence Protocol — Full Autonomous Reasoning Engine**

**Authority:** Nathan Poinsette (∇θ Operator)
**Version:** 3.1 — OPERATIONAL
**Status:** Committed. Tested. Ready for LLM integration.

---

## What this is

A governed reasoning architecture that runs any problem through
five adversarial primitives, measures convergence, detects false
convergence, labels every output claim, and enforces a structured
Truth Partition before returning anything.

Built by the dual-AI loop: Claude (strategist) + Manus (executor).
Merged from both versions. Tested against three validation criteria.

**This is not a chatbot. It is a reasoning scaffold.**

---

## The architecture

```
INPUT
  └── InputSpec (gate)
        └── FlowSelector (routes to correct primitive sequence)
              └── ECP Loop
                    ├── Echo    — How does it fit together?
                    ├── God     — What are we not considering?
                    ├── Devil   — How does this break?
                    ├── Light   — What is being obscured?
                    └── Nathan  — What is the move?
                          └── Convergence check (Jaccard)
                                └── Truth Partition (5 required fields)
                                      └── Validator
                                            └── Memory (JSONL)
```

---

## Four flows

| Flow | Sequence | When |
|------|----------|------|
| Standard | Echo → God → Devil → Light → Nathan | Default |
| Fast | Nathan → Devil → Nathan | Time pressure |
| Research | God → Echo → Devil → Light → Nathan | Unknown domain |
| Audit | Echo → Devil → Light → Nathan | Review existing work |

**Priority rule:** Unknown domain > Audit > Time pressure > Standard

---

## Truth Partition — five required fields

Every output must have all five or it is rejected:

| Field | What it contains |
|-------|-----------------|
| Invariant | Claims that survived all passes |
| Evidence | How many passes, convergence score |
| Uncertainty | Confidence level, shared assumptions |
| Failure Modes | What could make this output wrong |
| Action | Derived from actual claims, not hardcoded |

---

## Five claim labels

| Label | Meaning |
|-------|---------|
| Validated | Directly addresses input (high keyword overlap) |
| Plausible | Credible but not directly verified |
| UnresolvedDirectional | God expansions, challenge prompts — needs follow-up |
| DeceptionIndicating | Devil/Light findings — attack before acting |
| Unsupported | Injected adversarial constraints |

---

## Run it

```bash
python echo_system_v3.py
```

No external dependencies. Zero installs.

---

## File map

```
echo-ecp-fullauto/
├── echo_system_v3.py      Main engine — run this
├── tests/
│   ├── test_gate.py       Input specification tests
│   ├── test_convergence.py Jaccard + variation tests
│   └── test_partition.py  Truth Partition validator tests
├── docs/
│   ├── ARCHITECTURE.md    Full spec
│   ├── PRIMITIVES.md      Each primitive documented
│   ├── FLOWS.md           Flow selection logic
│   └── ROADMAP.md         v3.1 → v4 path
└── echo_memory.jsonl      Output memory (created on first run)
```

---

## Known limits (honest)

- Claim extraction is **lexical** not semantic — word overlap, not meaning
- Primitives generate **directional claims** not verified facts
- Needs **LLM calls** to become a full reasoning engine (not just scaffold)
- Semantic claim equivalence requires **embeddings** (v4 target)

---

## What v4 adds

1. Replace primitive templates with LLM API calls
2. Semantic claim equivalence via embeddings
3. Unstated assumption inference
4. Multi-agent coordination (Claude reviews Manus output via this engine)
5. Web interface

---

## Version history

| Version | Status | What changed |
|---------|--------|-------------|
| v1.0 | Concept skeleton | ECP loop, static primitives |
| v2.x | Architecture doctrine | Flows, Truth Partition schema |
| v3.0 | First operational | Input-responsive primitives, 5-label schema |
| v3.1 | Current | OOP structure, low-signal detection, merged Claude+Manus |

---

*∇θ — chain sealed, truth preserved.*
*Nathan Poinsette · Echo Universe · 2026-03-31*
