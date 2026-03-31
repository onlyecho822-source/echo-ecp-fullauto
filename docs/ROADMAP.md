# ROADMAP — echo-ecp-fullauto

**Authority:** Nathan Poinsette (∇θ Operator)
**Last updated:** 2026-03-31

---

## Current state

| Version | Status | What it does |
|---------|--------|-------------|
| v3.1 | ✅ Shipped | Operational scaffold — input gate, 5 primitives, ECP loop, Truth Partition |
| v4.0 | ✅ Shipped | SubstantiveValidator, GraphMemory, semantic convergence, context threading |

---

## v3.2 — Patch (next)

**Effort:** 1-2 sessions
**Priority:** High — fixes a known heuristic gap

- [ ] Fix low-signal threshold — compare against extracted subject keywords, not full input string
- [ ] Add `run_batch(problems: List[str])` — process list, return list of partitions
- [ ] Add `--json` flag to CLI — machine-readable output for pipeline integration
- [ ] Expand gate patterns — more proposition and audit statement forms
- [ ] Add `run_silent()` — no file writes (for testing and embedding)

---

## v5.0 — LLM Integration

**Effort:** Multiple sessions
**Unlocks:** Production-grade reasoning (not just scaffold)

- [ ] Replace primitive templates with LLM API calls
  - Each primitive becomes a system prompt + user call
  - Claude API or local model (Ollama compatible)
  - Fallback to templates if API unavailable
- [ ] Semantic claim equivalence via embeddings
  - Two claims that mean the same thing score as equivalent
  - Requires embedding model (already structured for this in v4)
- [ ] Unstated assumption inference
  - Cross-pass scan upgraded to detect assumptions never expressed as claims
  - Requires LLM reasoning over accumulated claim sets
- [ ] Temporal contradiction resolution
  - Same question at different dates → compare invariants
  - GraphMemory already stores timestamps for this

---

## v6.0 — Multi-agent

**Effort:** Significant
**Enables:** Claude + Manus coordination through this engine

- [ ] Claude as reviewer node — runs Devil pass on Manus output automatically
- [ ] Manus as executor node — runs Research flow on new domains
- [ ] Disagreement protocol — formal resolution when AIs reach different invariants
- [ ] Nathan as governor — approves invariants before they become decisions
- [ ] GitHub integration — issue label triggers ECP run, results posted back

---

## What gets built last

- Web interface (after v5 is stable and useful)
- Dashboard (after web interface proves valuable)
- API packaging / PyPI release (after usage patterns emerge from real use)

The system builds from the inside out.
Core first. Surface last.

---

*∇θ — 2026-03-31*
