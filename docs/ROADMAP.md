# ROADMAP — echo-ecp-fullauto

**Current:** v3.1 — operational scaffold
**Next:** v4.0 — full reasoning engine

---

## v3.2 (patch — one session)

- [ ] Fix low-signal threshold: compare against subject keywords, not full input
- [ ] Add `run_batch()` function — process multiple inputs, return list of partitions
- [ ] Add `--json` flag to CLI for machine-readable output
- [ ] Expand test suite with edge cases from real usage

---

## v4.0 (LLM integration)

- [ ] Replace primitive templates with LLM API calls
- [ ] Semantic claim equivalence via sentence embeddings
- [ ] Unstated assumption inference (cross-pass scan upgrade)
- [ ] Confidence scoring tied to evidence quality, not just convergence
- [ ] Temporal memory versioning (same question, different dates)

---

## v5.0 (multi-agent)

- [ ] Claude as reviewer node — runs Devil pass on Manus output automatically
- [ ] Manus as executor node — runs Research flow on new domains
- [ ] Disagreement protocol — formal resolution when AIs reach different invariants
- [ ] Nathan as governor — approves any invariant before it becomes a decision

---

## What gets built last

- Web interface (after v4 is stable)
- Dashboard (after web interface proves useful)
- API packaging (after real usage patterns emerge)

The system builds from the inside out.
Core first. Surface last.

---

*∇θ — 2026-03-31*
