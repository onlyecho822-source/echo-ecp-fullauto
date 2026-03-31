# EVOLUTION — v3.1 → v4.0

**Date:** 2026-03-31
**Authority:** Nathan Poinsette (∇θ Operator)

---

## What v4 adds

### 1. SubstantiveValidator
Checks content quality, not just structure.
v3.1 Validator only checked that five fields exist and are non-empty.
v4 SubstantiveValidator additionally checks:
- Evidence keywords overlap with Invariant (not disconnected)
- Action contains a concrete verb (deploy/build/fix/run/send/launch etc.)
- Uncertainty and Failure Modes are distinct sections

### 2. GraphMemory — triple store with temporal versioning
Stores converged invariants as triples: (claim, asserted_by, source, timestamp, version)
Enables:
- `get_history(keywords)` — retrieve all claims on a topic over time
- `contradictions(claim)` — find stored claims that contradict a new one
- `networkx` graph if installed; falls back to list-based store
Every ECP run stores its converged invariants automatically.

### 3. Semantic convergence
If `sentence-transformers` is installed, convergence uses embedding cosine similarity.
Two claims that mean the same thing with different words now score high overlap.
Falls back to Jaccard if library not available. Zero behavior change without install.

### 4. Context threading
Primitives now share state across passes via a context dict.
Devil's attacks are available to Light. God's expansions persist to next pass.
Echo reads prior claims and surfaces recurring themes.

---

## What was fixed before pushing (Devil pass findings)

| Finding | Fix |
|---------|-----|
| God reversed input string as "creative expansion" | Replaced with _kw()-based expansion from v3.1 |
| InputSpec gate regressed (accepted 5-char inputs) | Restored full v3.1 gate |
| Verb whitelist too narrow (deploy/push/fix missing) | Expanded to 20+ verbs |
| GraphMemory._save() had no try/except | Wrapped in try/except — fault-tolerant |
| Nathan/Echo stubs not marked as stubs | Docstrings now say STUB explicitly |

---

## What is still a stub (honest)

| Component | Status | What it needs |
|-----------|--------|---------------|
| Nathan prioritization | Stub | LLM call or operator input |
| Echo gap detection | Stub | Semantic analysis or LLM |
| God expansion options | Directional | LLM call for real creativity |
| Devil attacks | Directional | LLM call for targeted falsification |
| Light hidden assumptions | Directional | LLM call for deep scrutiny |

All primitives generate directional claims about the input.
They do not verify claims or reason from evidence.
That is v4. Production reasoning requires LLM integration (v5).

---

## Performance notes

- Semantic convergence: ~50MB download for `all-MiniLM-L6-v2` on first run
- Graph memory: JSON file — replace with Neo4j or SQLite for scale
- All features degrade gracefully without optional dependencies

---

## v5 targets

1. LLM calls per primitive (Claude API or local model)
2. Multi-agent coordination (Claude reviews Manus output through this engine)
3. Temporal contradiction resolution (same question, different dates)
4. Web interface + real-time collaboration

---

*∇θ — 2026-03-31T05:00:07Z*
