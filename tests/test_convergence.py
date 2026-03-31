#!/usr/bin/env python3
"""Tests for convergence tools."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from echo_system_v3 import jaccard, has_new_claim, normalize

def test_jaccard_identical():
    a = {"claim one", "claim two"}
    assert jaccard(a, a) == 1.0

def test_jaccard_disjoint():
    a = {"apple"}; b = {"orange"}
    assert jaccard(a, b) == 0.0

def test_jaccard_partial():
    a = {"claim one", "claim two"}
    b = {"claim one", "claim three"}
    score = jaccard(a, b)
    assert 0 < score < 1

def test_jaccard_empty():
    assert jaccard(set(), set()) == 1.0

def test_has_new_claim_yes():
    new   = {normalize("the system fails under adversarial pressure")}
    prior = {normalize("the system is well designed")}
    assert has_new_claim(new, prior)

def test_has_new_claim_no():
    claim = normalize("the system fails under adversarial pressure")
    assert not has_new_claim({claim}, {claim})

def test_has_new_claim_empty_prior():
    assert has_new_claim({"anything"}, set())

if __name__ == "__main__":
    tests = [test_jaccard_identical, test_jaccard_disjoint, test_jaccard_partial,
             test_jaccard_empty, test_has_new_claim_yes, test_has_new_claim_no,
             test_has_new_claim_empty_prior]
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
