#!/usr/bin/env python3
"""
test_convergence.py — Convergence tool tests
==============================================
Authority : Nathan Poinsette (∇θ Operator)
Tests     : 7
Covers    : jaccard() edge cases (identical, disjoint, partial, empty sets),
            has_new_claim() positive/negative/empty-prior cases,
            normalize() is implicitly tested via has_new_claim()

Run: python tests/test_convergence.py
     python -m pytest tests/test_convergence.py -v
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from echo_system_v3 import jaccard, has_new_claim, normalize


def test_jaccard_identical():
    """Identical sets should score 1.0."""
    a = {"claim one", "claim two"}
    assert jaccard(a, a) == 1.0, "Identical sets must score 1.0"


def test_jaccard_disjoint():
    """Completely disjoint sets should score 0.0."""
    a = {"apple"}; b = {"orange"}
    assert jaccard(a, b) == 0.0, "Disjoint sets must score 0.0"


def test_jaccard_partial():
    """Partially overlapping sets should score between 0 and 1."""
    a = {"claim one", "claim two"}
    b = {"claim one", "claim three"}
    score = jaccard(a, b)
    assert 0 < score < 1, f"Expected partial overlap, got {score}"


def test_jaccard_empty():
    """Two empty sets should score 1.0 (convention: empty = converged)."""
    assert jaccard(set(), set()) == 1.0, "Empty sets must score 1.0"


def test_has_new_claim_yes():
    """Genuinely new claim should return True."""
    new   = {normalize("the system fails under adversarial pressure")}
    prior = {normalize("the system is well designed")}
    assert has_new_claim(new, prior), "Should detect a new claim"


def test_has_new_claim_no():
    """Exact duplicate should return False — no new claim."""
    claim = normalize("the system fails under adversarial pressure")
    assert not has_new_claim({claim}, {claim}),         "Duplicate claim should not count as new"


def test_has_new_claim_empty_prior():
    """First pass always has new claims (prior is empty)."""
    assert has_new_claim({"anything"}, set()),         "Empty prior means any claim is new"


if __name__ == "__main__":
    tests = [
        test_jaccard_identical, test_jaccard_disjoint, test_jaccard_partial,
        test_jaccard_empty, test_has_new_claim_yes, test_has_new_claim_no,
        test_has_new_claim_empty_prior,
    ]
    passed = failed = 0
    for t in tests:
        try:
            t(); print(f"  ✅ {t.__name__}"); passed += 1
        except Exception as e:
            print(f"  ❌ {t.__name__}: {e}"); failed += 1
    print(f"\n{passed} passed | {failed} failed")
