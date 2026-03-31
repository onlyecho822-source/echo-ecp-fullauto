# Contributing to echo-ecp-fullauto

**Authority:** Nathan Poinsette (∇θ Operator)
**Date:** 2026-03-31

---

## Before you contribute

Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) first.
The five design invariants are non-negotiable:
1. Five primitives — no additions without ECP challenge
2. Four flows — compositions only, not new modes
3. Truth Partition — five fields required, no exceptions
4. ECP as meta-method — governs iteration, not a primitive
5. Input gate — three states: accepted, reformulate, rejected

---

## What good contributions look like

**Patches (v3.2 targets):**
- Fix the low-signal threshold (compare against subject keywords, not full input)
- Add `run_batch()` for multiple inputs
- Add `--json` flag to CLI
- Expand test coverage with real-world edge cases

**Extensions (v4 → v5):**
- Replace primitive templates with LLM API calls
- Add semantic claim equivalence via embeddings
- Temporal memory versioning (same question, different dates)

**Documentation:**
- Real-world usage examples
- Edge cases you discovered
- Performance benchmarks

---

## How to submit

1. Run all tests: `python tests/test_gate.py && python tests/test_convergence.py && python tests/test_partition.py && python tests/test_v4.py`
2. Run a Devil pass on your own changes before submitting
3. Document what is a stub vs what is real behavior
4. Open an issue first for anything that changes the five invariants

---

## Devil pass requirement

Every PR must include a Devil pass on its own changes.
Specifically:
- What assumption does this change make?
- Under what condition does this change make things worse?
- What was this not considering?

This is not optional. It is how the system was built.

---

## Code style

- Python 3.8+ compatible
- No external dependencies in core engine
- Optional dependencies degrade gracefully
- Every public function has a docstring
- Stubs must be marked with `# STUB — replace with LLM call`

---

*∇θ — 2026-03-31*
