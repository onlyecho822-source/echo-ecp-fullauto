#!/usr/bin/env python3
"""
Echo Compression Stack v1.1-hardened — 15-Case Adversarial Test Suite
Repo: onlyecho822-source/echo-ecp-fullauto

Tests:  5 valid, 5 malformed/fatal, 5 borderline/edge
Run:    python tests/test_protocol_validator.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.validate_protocol import validate

def run(name, text, expect_pass, expect_warns=None, expect_fatals=None):
    errors, warns, compat, _, _ = validate(text)
    fatals = [c for c in compat if c.startswith("FATAL")]
    passed = not errors and not fatals
    result = "PASS" if passed else "FAIL"
    ok = (passed == expect_pass)
    warn_ok = True
    if expect_warns is not None:
        warn_ok = len(warns) >= expect_warns
    status = "✓" if (ok and warn_ok) else "✗"
    print(f"  {status} [{result}] {name}")
    if not ok:
        for e in errors:  print(f"      ERROR: {e}")
        for f in fatals:  print(f"      {f}")
    return ok and warn_ok

results = []
print("\n=== VALID CASES (expect PASS) ===")

results.append(run("V1 — standard L1 Δ cross-domain alert",
"""Scope: PUBLIC
Truth: ✔
Mode: Δ
Confidence: 94%
Decision: ACT
Level: L1
Claim: Seismic M5.2 + solar wind jumped from 400 to 780 km/s at 2025-04-02 13:10 UTC.
Risk: Possible coincidence; events may be independent.
Action: Review raw waveforms and corroborate with additional sensors.
Test: Replay with 24h baseline to confirm Z-scores are not artifacts.
Audit: Assumes USGS and NOAA timestamps synchronized within 60 seconds.
Why not higher: No third-domain corroboration; geographic relevance unverified.""",
expect_pass=True))

results.append(run("V2 — standard L1 ⚖ comparison",
"""Scope: PUBLIC
Truth: ≈
Mode: ⚖
Confidence: 88%
Decision: CHK
Level: L1
Claim: Async I/O throughput vs direct write throughput under 10k req/s load.
Risk: Memory contention may dominate over I/O at high concurrency.
Action: Profile both paths under production-equivalent load.
Test: Benchmark async queue vs direct write at 10k req/s for 60 seconds.
Audit: Assumes CPU saturation is not primary bottleneck.
Why not higher: Memory profiling not yet completed.""",
expect_pass=True))

results.append(run("V3 — L0 light mode INFO (allowed)",
"""Scope: PUBLIC
Truth: ✔
Mode: ⚙
Confidence: 91%
Decision: INFO
Level: L0
Claim: Protocol v1.1-hardened committed to repo.
Risk: Low.
Action: None required.
Test: Confirm commit hash.
Audit: Assumes commit push succeeded.
Why not higher: Not checked post-push.""",
expect_pass=True))

results.append(run("V4 — L2 with 🔍 audit mode",
"""Scope: PUBLIC
Truth: ≈
Mode: 🔍
Confidence: 87%
Decision: CHK
Level: L2
Claim: Validator heuristics may produce false positives on legitimate short Risk fields.
Risk: Over-strict validator reduces adoption.
Action: Add exception for Risk fields under 10 chars when Truth is ✔ and Confidence > 90%.
Test: Run 50 historical messages through validator and measure false-positive rate.
Audit: Could be wrong because short Risk fields may genuinely be underspecified.
Why not higher: No systematic measurement of false-positive rate yet.""",
expect_pass=True))

results.append(run("V5 — L3 full evidence block",
"""Scope: CONTEXT-LOCKED
Truth: ✔
Mode: 🧪
Confidence: 96%
Decision: ACT
Level: L3
Claim: Validator correctly rejects L0+ACT combination per FATAL rule.
Risk: Rule may be too strict for edge cases in collaborative environments.
Action: Deploy validator with FATAL on L0+ACT as confirmed safe.
Test: Ran 15-case adversarial suite — zero false failures on valid cases.
Audit: Assumes test suite covers representative usage patterns.
Why not higher: Multi-user adversarial testing not yet completed.""",
expect_pass=True))

print("\n=== MALFORMED / FATAL CASES (expect FAIL) ===")

results.append(run("M1 — L0 + ACT (FATAL)",
"""Scope: PUBLIC
Truth: ✔
Mode: ⚙
Confidence: 94%
Decision: ACT
Level: L0
Claim: Deploy the patch now.
Risk: Low.
Action: Deploy.
Test: Smoke test post-deploy.
Audit: Assumes staging passed.
Why not higher: Staging only.""",
expect_pass=False))

results.append(run("M2 — Unknown Mode symbol (FATAL)",
"""Scope: PUBLIC
Truth: ✔
Mode: 💥
Confidence: 90%
Decision: INFO
Level: L1
Claim: System is healthy.
Risk: Minor drift possible.
Action: Monitor.
Test: Check metrics dashboard.
Audit: Assumes monitoring is accurate.
Why not higher: No external audit.""",
expect_pass=False))

results.append(run("M3 — Missing required fields",
"""Scope: PUBLIC
Truth: ✔
Confidence: 85%
Decision: INFO
Claim: System running normally.""",
expect_pass=False))

results.append(run("M4 — Confidence > 95% + Why not higher: unknown (FAIL)",
"""Scope: PUBLIC
Truth: ✔
Mode: ⚙
Confidence: 99%
Decision: ACT
Level: L1
Claim: This fix resolves all latency issues permanently.
Risk: Minor regression possible.
Action: Deploy fix.
Test: Run regression suite.
Audit: Assumes tests are comprehensive.
Why not higher: unknown""",
expect_pass=False))

results.append(run("M5 — Invalid Audit prefix",
"""Scope: PUBLIC
Truth: ✔
Mode: ⚙
Confidence: 88%
Decision: ACT
Level: L1
Claim: Refactored database query reduces latency by 40%.
Risk: Index rebuild may cause temporary slowdown.
Action: Deploy in maintenance window.
Test: Benchmark before and after.
Audit: I think this is probably fine.
Why not higher: Only tested on staging.""",
expect_pass=False))

print("\n=== BORDERLINE / EDGE CASES (expect PASS with warnings) ===")

results.append(run("E1 — Truth ∼ with high confidence (WARN, not FAIL)",
"""Scope: PUBLIC
Truth: ∼
Mode: ⚙
Confidence: 89%
Decision: CHK
Level: L1
Claim: The anomaly may be caused by sensor calibration drift.
Risk: Alternative cause is network latency spike.
Action: Inspect calibration logs from last 48h.
Test: Compare readings from backup sensor.
Audit: Could be wrong because backup sensor shares same power circuit.
Why not higher: Hypothesis not yet tested against calibration data.""",
expect_pass=True, expect_warns=1))

results.append(run("E2 — Δ with narrative change language (no timestamp, but valid)",
"""Scope: PUBLIC
Truth: ≈
Mode: Δ
Confidence: 82%
Decision: CHK
Level: L1
Claim: System entered instability phase after config change was applied.
Risk: Rollback may not fully restore prior state.
Action: Monitor for 30 minutes before declaring stable.
Test: Compare error rate before and after config change.
Audit: Assumes config change is the only variable that changed.
Why not higher: Insufficient post-change observation window.""",
expect_pass=True))

results.append(run("E3 — ⚖ with implicit comparison (should warn)",
"""Scope: PUBLIC
Truth: ≈
Mode: ⚖
Confidence: 85%
Decision: INFO
Level: L1
Claim: The new algorithm processes requests and returns results more efficiently.
Risk: Efficiency gain may not hold under all load profiles.
Action: Document benchmark results.
Test: Run load test at 1x, 5x, 10x baseline.
Audit: Assumes benchmark environment matches production.
Why not higher: Only tested at up to 5x baseline load.""",
expect_pass=True, expect_warns=1))

results.append(run("E4 — Risk: none with strong justification (should warn)",
"""Scope: PUBLIC
Truth: ✔
Mode: ⚙
Confidence: 97%
Decision: INFO
Level: L1
Claim: README typo corrected — no functional change.
Risk: none — documentation-only change with no code path affected.
Action: Merge PR.
Test: Confirmed no test failures in CI.
Audit: Assumes CI covers all affected paths.
Why not higher: External review not required for documentation fix.""",
expect_pass=True, expect_warns=1))

results.append(run("E5 — 🧪 with minimal but non-trivial Test",
"""Scope: PUBLIC
Truth: ≈
Mode: 🧪
Confidence: 79%
Decision: CHK
Level: L1
Claim: Retry logic reduces timeout error rate under transient network failures.
Risk: Retry storm possible under sustained failure conditions.
Action: Implement exponential backoff with jitter.
Test: Inject network failures at 5% rate and measure timeout error reduction.
Audit: Assumes synthetic failure injection matches production failure patterns.
Why not higher: Production failure patterns not yet fully characterized.""",
expect_pass=True))

# Summary
passed = sum(results)
total  = len(results)
print(f"\n{'='*50}")
print(f"Results: {passed}/{total} passed")
print(f"{'SUITE PASS' if passed == total else 'SUITE FAIL — review failures above'}")
print("\n∇θ — chain sealed, truth preserved.")
