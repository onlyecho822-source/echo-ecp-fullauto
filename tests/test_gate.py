#!/usr/bin/env python3
"""Tests for InputSpec gate."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from echo_system_v3 import InputSpec, run

def test_rejects_empty():
    try:
        InputSpec.classify("")
        assert False, "Should have raised"
    except ValueError as e:
        assert "REJECTED" in str(e)

def test_rejects_short():
    try:
        InputSpec.classify("ok")
        assert False
    except ValueError as e:
        assert "REJECTED" in str(e)

def test_accepts_question():
    r = InputSpec.classify("What is the highest-leverage action?")
    assert r["type"] == "question"

def test_accepts_proposition():
    r = InputSpec.classify("The system is complete unless a new domain emerges")
    assert r["type"] == "proposition"

def test_accepts_audit():
    r = InputSpec.classify("The document is missing a payment pathway")
    assert r["type"] == "audit_statement"

def test_reformulates_vague():
    try:
        InputSpec.classify("things stuff")
        assert False
    except ValueError as e:
        assert "REFORMULATE" in str(e)

def test_full_run_question():
    r = run("What is the most critical action to take today?")
    assert r["valid"]
    assert r["flow"] == "Standard"
    assert len(r["tp"]["Invariant"]) > 0

def test_full_run_audit():
    r = run("The deployment is missing environment variables")
    assert r["valid"]
    assert r["flow"] == "Audit"

if __name__ == "__main__":
    tests = [test_rejects_empty, test_rejects_short, test_accepts_question,
             test_accepts_proposition, test_accepts_audit, test_reformulates_vague,
             test_full_run_question, test_full_run_audit]
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
