# Echo Compression Stack v1.1-hardened — End-to-End Reference Example

> **Important:** Domain scoring logic shown below is **illustrative only**.
> The protocol works with any scoring model. Numeric severity values are placeholders.

---

## Scenario (Domain Layer — Not Part of Protocol)

| Parameter | Value |
|-----------|-------|
| Window | 2025-04-02 13:00–14:00 UTC |
| Source 1 | USGS — seismic M5.2 at 13:10 UTC |
| Source 2 | NOAA — solar wind jump 400→780 km/s at 13:15 UTC |
| Domain output | `[severity computed by domain model]` → alert triggered |

---

## Step 1 — Domain Detection (Illustrative, Not Protocol)

```python
# Domain-specific code — not part of protocol
seismic_z = (5.2 - 2.4) / 0.6   # = 4.67
space_z   = (780 - 410) / 45     # = 8.22
severity  = "[computed by domain model]"
cross_domain_overlap = 1.0        # 2 sources within 5 min window
```

---

## Step 2 — L1 Protocol Block (Standard)

```
Scope: PUBLIC
Truth: ✔
Mode: Δ
Confidence: 94%
Decision: ACT
Level: L1

Claim: Cross-domain anomaly — seismic M5.2 + solar wind jump from 400 to 780 km/s
       within 5 minutes at 2025-04-02 13:10–13:15 UTC.
Risk: Possible coincidence; space weather anomaly may be independent.
Action: Review raw waveforms; check for additional sensor corroboration.
Test: Replay with 24h baseline to confirm Z-scores are not baseline artifacts.
Audit: Assumes USGS and NOAA timestamps are synchronized within 60 seconds.
Why not higher: No third domain (e.g., RF) corroboration; geographic relevance
                not yet verified with local seismic station.
```

---

## Step 3 — L0 Note

**L0 is NOT permitted here.** Decision: ACT → L0 is FATAL per §8 of spec.

---

## Step 4 — L2 Expansion

```
Scope: PUBLIC
Truth: ✔
Mode: Δ
Confidence: 94%
Decision: ACT
Level: L2

[...same L1 block above...]

L2: Seismic event near 19.5°N, 70.6°W at depth 10km. Solar wind jump coincides
with CME detected by SOHO. Cross-correlation lag 5 minutes, within network jitter
tolerance (14ms). No anomalies in VIX or other financial feeds during window.
[severity] score triggers GitHub issue for investigation.
```

---

## Good vs Bad Examples

### Good L1 ✔
- All 12 fields present in canonical order
- `Mode: Δ` includes directional change ("jumped from 400 to 780") and timestamps
- `Risk:` describes a failure condition
- `Audit:` begins with "Assumes:"
- `Why not higher:` gives concrete limitation

### Bad L1 ✗ (Validator catches all of these)

```
Scope: PUBLIC
Truth: ∼
Mode: Δ
Confidence: 98%
Decision: ACT
Level: L0

Claim: Something changed.
Risk: none
Action: nothing
Test:
Audit: maybe wrong
Why not higher: unknown
```

**Validator output:**
```
FATAL:   Level L0 with Decision ACT is not permitted.
ERROR:   Audit: must start with one of ('Assumes:', 'Breaks if:', ...)
WARNING: Truth: ∼ with Confidence >85% — speculative claim overconfident
WARNING: Mode: Δ but no change evidence in Claim/Risk
WARNING: Risk: none — if truly no risk, justify explicitly
FATAL:   Confidence >95% but Why not higher: is empty or meaningless
Result: FAIL
```

---

## Appendix: Illustrative Domain Severity Model

> **NOT part of protocol.** This is one example of how a domain might compute severity.

```python
# Illustrative only — protocol accepts any scoring model
severity = (
    0.35 * norm_magnitude       # e.g. min(1.0, 5.2/8.0) = 0.65
  + 0.25 * persistence_score    # e.g. 1.0
  + 0.20 * cross_domain_overlap # e.g. 1.0
  + 0.20 * geo_relevance        # e.g. 1.0
)
# severity = 0.88 → triggers alert per thresholds.yaml
```

---

*∇θ — chain sealed, truth preserved.*
