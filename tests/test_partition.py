#!/usr/bin/env python3
"""
test_partition.py — Truth Partition validator tests
=====================================================
Authority : Nathan Poinsette (∇θ Operator)
Tests     : 6
Covers    : structural validation (valid, missing section, empty section),
            stability across 3 independent runs (determinism test),
            adversarial input surfaces DeceptionIndicating claims,
            all five required fields present across three problem types

Run: python tests/test_partition.py
     python -m pytest tests/test_partition.py -v
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from echo_system_v3 import validate_tp, run, REQUIRED


def test_valid_partition():
    """A complete Truth Partition with all five fields should be valid."""
    tp = {s: ["content"] for s in REQUIRED}
    tp["Labels"] = {}
    valid, issues = validate_tp(tp)
    assert valid, f"Expected valid, got issues: {issues}"


def test_missing_section():
    """Missing a required section should invalidate the partition."""
    tp = {s: ["content"] for s in REQUIRED if s != "Action"}
    tp["Labels"] = {}
    valid, issues = validate_tp(tp)
    assert not valid, "Missing Action section should fail validation"
    assert any("Action" in i for i in issues),         f"Issues should mention Action, got: {issues}"


def test_empty_section():
    """An empty required section should invalidate the partition."""
    tp = {s: ["content"] for s in REQUIRED}
    tp["Invariant"] = []    # empty — should fail
    tp["Labels"] = {}
    valid, issues = validate_tp(tp)
    assert not valid, "Empty Invariant should fail validation"


def test_stability_3_runs():
    """
    Same problem run 3 times should produce the same invariant count.
    Verifies deterministic behavior — same input = same output.
    """
    problem = "What is the highest-leverage deployment action for art-of-proof?"
    results = [run(problem, {"time_pressure": True}) for _ in range(3)]
    counts  = [len(r["tp"]["Invariant"]) for r in results]
    assert len(set(counts)) == 1,         f"Unstable invariant counts across runs: {counts} — engine is not deterministic"


def test_adversarial_surfaces_deception():
    """
    An input making an unfalsifiable claim should produce DeceptionIndicating claims.
    This verifies Devil and Light are doing their job.
    """
    r = run(
        "The system never fails under any condition if operators follow the rules",
        {"audit": True}
    )
    deception = len(r["tp"]["Labels"].get("DeceptionIndicating", []))
    assert deception > 0,         f"Adversarial input should surface DeceptionIndicating claims, got 0"


def test_all_partitions_have_five_fields():
    """
    All five required fields must be present for three different input types.
    Covers: question, audit_statement, and proposition.
    """
    problems = [
        ("What should we deploy first?", {}),
        ("The auth system is missing rate limiting", {}),
        ("Should we use Netlify or Railway if cost matters?", {"time_pressure": True}),
    ]
    for problem, ctx in problems:
        r = run(problem, ctx)
        for section in REQUIRED:
            assert section in r["tp"],                 f"Missing section '{section}' for problem: {problem}"


if __name__ == "__main__":
    tests = [
        test_valid_partition, test_missing_section, test_empty_section,
        test_stability_3_runs, test_adversarial_surfaces_deception,
        test_all_partitions_have_five_fields,
    ]
    passed = failed = 0
    for t in tests:
        try:
            t(); print(f"  ✅ {t.__name__}"); passed += 1
        except Exception as e:
            print(f"  ❌ {t.__name__}: {e}"); failed += 1
    print(f"\n{passed} passed | {failed} failed")
