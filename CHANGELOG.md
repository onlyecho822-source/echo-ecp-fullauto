# CHANGELOG

All notable changes to echo-ecp-fullauto.

Format: [Version] — Date — What changed — Why

---

## [4.0] — 2026-03-31 — SubstantiveValidator, GraphMemory, Semantic Convergence

### Added
- `SubstantiveValidator` — checks content quality beyond structure
  - Evidence must share keywords with Invariant
  - Action must contain a concrete verb (20+ verbs)
  - Uncertainty and Failure Modes must be distinct
- `GraphMemory` — triple store with temporal versioning
  - `add_claim(claim, source)` — stores with timestamp + version
  - `get_history(keywords)` — retrieve claims on topic over time
  - `contradictions(claim)` — find stored claims that contradict
  - networkx optional; falls back to list-based store
- Semantic convergence — embedding-based Jaccard via sentence-transformers
  - Detects paraphrased claims that word-overlap misses
  - Falls back to Jaccard if library not installed
- Context threading — primitives share state across passes
  - Devil attacks available to Light
  - God expansions persist to next pass
  - Echo reads prior claims for theme extraction
- 14 new tests in `tests/test_v4.py`
- `docs/EVOLUTION.md` — honest account of stubs vs real behavior

### Fixed (from Devil pass before commit)
- God primitive was reversing input string as "creative expansion"
- InputSpec gate had regressed — accepted 5-char inputs like "vague"
- SubstantiveValidator verb whitelist was missing deploy/push/fix/run/send
- GraphMemory._save() had no try/except — crashed on write failure
- Nathan/Echo stubs not clearly marked as stubs

---

## [3.1] — 2026-03-31 — OOP structure, low-signal detection, merge

### Added
- OOP primitive architecture (Manus) — each primitive is a class
- Low-signal detection — suppresses full output when <3 validated claims overlap input
- `CONTRIBUTING.md`, `SECURITY.md`, `docs/PRIMITIVES.md`
- 21 tests across 4 test files

### Fixed
- Primitives now use actual input (were returning hardcoded boilerplate)
- Action field derived from claim frequency (was pointing to system's own TODO list)
- False convergence only fires when genuinely shared (not on every run)
- Labels tied to claim content (not trivial string matching)

---

## [3.0] — 2026-03-31 — First operational version

### Added
- Input gate: question / proposition / audit statement
- Flow selector: Standard / Fast / Research / Audit
- Five input-responsive primitives: Nathan, Echo, Devil, Light, God
- ECP loop with Jaccard convergence
- 5-label schema: Validated / Plausible / UnresolvedDirectional / DeceptionIndicating / Unsupported
- Truth Partition with 5 required fields
- Validator — rejects incomplete outputs
- JSONL memory
- `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`

---

## [1.0 / 2.x] — 2026-03-30 — Architecture and skeleton phases

- ECP conceptual architecture
- Multi-document review sessions
- Convergence metric definition
- Variation engine specification
- Six gap identifications (now all closed in v3+)

---

*∇θ — 2026-03-31*
