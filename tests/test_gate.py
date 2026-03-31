#!/usr/bin/env python3
"""
test_gate.py — InputSpec gate tests
=====================================
Authority : Nathan Poinsette (∇θ Operator)
Tests     : 8
Covers    : rejection (too short), reformulation (no structure),
            acceptance (question / proposition / audit_statement),
            full pipeline run through gate for question and audit

Run: python tests/test_gate.py
     python -m pytest tests/test_gate.py -v  (requires pytest)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from echo_system_v3 import InputSpec, run


def test_rejects_empty():
    """Empty string must be rejected with REJECTED prefix."""
    try:
        InputSpec.classify("")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "REJECTED" in str(e), f"Expected REJECTED, got: {e}"


def test_rejects_short():
    """Inputs under 8 chars must be rejected."""
    try:
        InputSpec.classify("ok")
        assert False, "Should have raised"
    except ValueError as e:
        assert "REJECTED" in str(e)


def test_accepts_question():
    """Input starting with a question word must be accepted as question."""
    r = InputSpec.classify("What is the highest-leverage action?")
    assert r["type"] == "question", f"Expected question, got {r['type']}"


def test_accepts_proposition():
    """Input with falsification condition must be accepted as proposition."""
    r = InputSpec.classify("The system is complete unless a new domain emerges")
    assert r["type"] == "proposition", f"Expected proposition, got {r['type']}"


def test_accepts_audit():
    """Input with problem term must be accepted as audit_statement."""
    r = InputSpec.classify("The document is missing a payment pathway")
    assert r["type"] == "audit_statement", f"Expected audit_statement, got {r['type']}"


def test_reformulates_vague():
    """Multi-word input with no structure must get REFORMULATE, not REJECTED."""
    try:
        InputSpec.classify("things stuff")
        assert False, "Should have raised"
    except ValueError as e:
        assert "REFORMULATE" in str(e), f"Expected REFORMULATE, got: {e}"


def test_full_run_question():
    """Full pipeline: question input should produce valid Standard output."""
    r = run("What is the most critical action to take today?")
    assert r["valid"], f"Expected valid output, issues: {r['issues']}"
    assert r["flow"] == "Standard", f"Expected Standard flow, got {r['flow']}"
    assert len(r["tp"]["Invariant"]) > 0, "Invariant should not be empty"


def test_full_run_audit():
    """Full pipeline: audit input should route to Audit flow."""
    r = run("The deployment is missing environment variables")
    assert r["valid"], f"Expected valid output, issues: {r['issues']}"
    assert r["flow"] == "Audit", f"Expected Audit flow, got {r['flow']}"


if __name__ == "__main__":
    tests = [
        test_rejects_empty, test_rejects_short, test_accepts_question,
        test_accepts_proposition, test_accepts_audit, test_reformulates_vague,
        test_full_run_question, test_full_run_audit,
    ]
    passed = failed = 0
    for t in tests:
        try:
            t(); print(f"  ✅ {t.__name__}"); passed += 1
        except Exception as e:
            print(f"  ❌ {t.__name__}: {e}"); failed += 1
    print(f"\n{passed} passed | {failed} failed")
