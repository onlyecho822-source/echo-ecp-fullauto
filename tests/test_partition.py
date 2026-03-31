#!/usr/bin/env python3
"""Tests for Truth Partition validator."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from echo_system_v3 import validate_tp, run, REQUIRED

def test_valid_partition():
    tp = {s: ["content"] for s in REQUIRED}
    tp["Labels"] = {}
    valid, issues = validate_tp(tp)
    assert valid, issues

def test_missing_section():
    tp = {s: ["content"] for s in REQUIRED if s != "Action"}
    tp["Labels"] = {}
    valid, issues = validate_tp(tp)
    assert not valid
    assert any("Action" in i for i in issues)

def test_empty_section():
    tp = {s: ["content"] for s in REQUIRED}
    tp["Invariant"] = []
    tp["Labels"] = {}
    valid, issues = validate_tp(tp)
    assert not valid

def test_stability_3_runs():
    problem = "What is the highest-leverage deployment action for art-of-proof?"
    results = [run(problem, {"time_pressure": True}) for _ in range(3)]
    counts = [len(r["tp"]["Invariant"]) for r in results]
    assert len(set(counts)) == 1, f"Unstable invariant counts: {counts}"

def test_adversarial_surfaces_deception():
    r = run("The system never fails under any condition if operators follow the rules",
            {"audit": True})
    deception = len(r["tp"]["Labels"].get("DeceptionIndicating", []))
    assert deception > 0, "Adversarial input should surface DeceptionIndicating claims"

def test_all_partitions_have_five_fields():
    problems = [
        ("What should we deploy first?", {}),
        ("The auth system is missing rate limiting", {}),
        ("Should we use Netlify or Railway if cost matters?", {"time_pressure": True}),
    ]
    for p, ctx in problems:
        r = run(p, ctx)
        for section in REQUIRED:
            assert section in r["tp"], f"Missing {section} for: {p}"

if __name__ == "__main__":
    tests = [test_valid_partition, test_missing_section, test_empty_section,
             test_stability_3_runs, test_adversarial_surfaces_deception,
             test_all_partitions_have_five_fields]
    passed = failed = 0
    for t in tests:
        try:
            t()
            print(f"  ✅ {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed | {failed} failed")
