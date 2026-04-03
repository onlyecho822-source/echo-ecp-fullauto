# Migration Guide: Echo Compression Stack v1.0 → v1.1-hardened

---

## Summary of Changes

| Change | v1.0 | v1.1-hardened |
|--------|------|---------------|
| Truth vs Mode | Single `Type:` field | Separate `Truth:` and `Mode:` |
| Risk field | Optional | Mandatory |
| Audit field | Free text | Constrained prefixes |
| Confidence | % only | % + `Why not higher:` |
| Field order | Variable | Fixed |
| Level | None | L0–L3 |
| Δ meaning | Undefined | State change over time only |
| L0 rules | None | Hard exclusions enforced |
| Compatibility rules | None | Validator-enforced table |
| Unknown symbols | Ignored | FATAL |

---

## Migration Steps

1. Split `Type:` into `Truth:` (✔/≈/∼) and `Mode:` (⚙/⚖/Δ/🧪/🔍)
2. Add `Level:` — default to L1 for technical outputs
3. Add `Why not higher:` with a concrete limitation
4. Reformat `Audit:` to start with a constrained prefix
5. Ensure `Risk:` is present and non-trivial
6. Reorder fields to canonical sequence
7. Run `python validate_protocol.py <file> --explain` and fix all ERRORs and FATALs

---

## Δ Disambiguation Checklist (critical for legacy messages)

For every `Type: Δ` in old messages, ask:

| Question | If YES | If NO |
|----------|--------|-------|
| Does it describe a change **over time**? | Keep `Mode: Δ` | → next question |
| Does it compare two **static states**? | Convert to `Mode: ⚖` | Expand to L2 and clarify |
| Is it ambiguous? | Expand to L2 | — |

**Time-based example (keep Δ):**
```
Mode: Δ
Claim: Seismic magnitude increased from 2.4 to 5.2 at 13:10 UTC.
```

**Static comparison (convert to ⚖):**
```
Mode: ⚖
Claim: Post-patch latency (25ms) vs pre-patch latency (10ms).
```

---

## Before / After Examples

### Example 1 — Standard technical claim

**v1.0:**
```
Scope: PUBLIC
Type: ≈
Confidence: 88%
Decision: CHK
Claim: The bottleneck is likely I/O.
Risk: Could be memory.
Action: Profile.
Test: Compare async vs direct.
Audit: Assumes CPU not saturated.
```

**v1.1-hardened:**
```
Scope: PUBLIC
Truth: ≈
Mode: ⚖
Confidence: 88%
Decision: CHK
Level: L1
Claim: Async I/O throughput vs direct write throughput under load.
Risk: Memory contention may be primary bottleneck instead.
Action: Profile concurrent write paths under load.
Test: Compare async queue vs direct writes at 10k req/s.
Audit: Assumes CPU saturation is not primary factor.
Why not higher: Memory profiling not yet completed.
```

### Example 2 — Ambiguous Δ corrected

**v1.0:**
```
Type: Δ
Claim: System performance changed.
```

**v1.1-hardened (time-based → Δ):**
```
Truth: ✔
Mode: Δ
Claim: API latency increased from 10ms to 25ms between 12:00 and 12:30 UTC.
```

**v1.1-hardened (static comparison → ⚖):**
```
Truth: ✔
Mode: ⚖
Claim: API latency after patch (25ms) vs before patch (10ms).
```

---

*∇θ — chain sealed, truth preserved.*
