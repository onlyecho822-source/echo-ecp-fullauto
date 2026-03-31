#!/usr/bin/env python3
"""Tests for Echo System v4.0 additions."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from echo_system_v4 import (
    SubstantiveValidator, GraphMemory, semantic_overlap,
    InputSpec, run, REQUIRED
)

# ── SubstantiveValidator ─────────────────────────────────────────────
def test_substantive_valid():
    tp = {"Invariant": ["Deploy art-of-proof system"],
          "Evidence":  ["Deploy art-of-proof tests passing"],
          "Uncertainty":   ["Unknown production behavior"],
          "Failure Modes": ["Missing env vars"],
          "Action":        ["Deploy the system to Netlify now"],
          "Labels": {}}
    ok, issues = SubstantiveValidator.validate(tp)
    assert ok, f"Expected valid, got: {issues}"

def test_substantive_missing_verb():
    tp = {"Invariant": ["System works"],
          "Evidence":  ["System works"],
          "Uncertainty":   ["Unknown"],
          "Failure Modes": ["Failure"],
          "Action":        ["The thing should happen somehow"],
          "Labels": {}}
    ok, issues = SubstantiveValidator.validate(tp)
    assert not ok
    assert any("verb" in i.lower() for i in issues)

def test_substantive_deploy_verb_accepted():
    """deploy was missing from v4 Manus verb list — fixed in v4.0"""
    tp = {"Invariant": ["Deploy system"],
          "Evidence":  ["Deploy evidence ready"],
          "Uncertainty":   ["Unknown"],
          "Failure Modes": ["Billing"],
          "Action":        ["Deploy art-of-proof to production"],
          "Labels": {}}
    ok, issues = SubstantiveValidator.validate(tp)
    assert ok, f"deploy should be accepted. Issues: {issues}"

# ── GraphMemory ──────────────────────────────────────────────────────
def test_graph_add_and_query():
    mem = GraphMemory("_test_graph.json")
    mem.add_claim("System is robust under load", "test_source")
    history = mem.get_history(["robust"])
    assert len(history) >= 1
    assert history[0]["claim"] == "System is robust under load"
    os.remove("_test_graph.json") if os.path.exists("_test_graph.json") else None

def test_graph_fault_tolerant():
    """_save should not crash even with bad path"""
    mem = GraphMemory("/nonexistent/path/graph.json")
    mem.add_claim("test claim", "test")  # should not raise

def test_graph_contradictions():
    mem = GraphMemory("_test_graph2.json")
    mem.add_claim("The system is not reliable", "test")
    contradictions = mem.contradictions("The system is reliable")
    assert len(contradictions) >= 1
    os.remove("_test_graph2.json") if os.path.exists("_test_graph2.json") else None

# ── Semantic overlap (Jaccard fallback) ──────────────────────────────
def test_semantic_identical():
    a = {"the system deploys correctly"}
    assert semantic_overlap(a, a) >= 0.99

def test_semantic_empty():
    assert semantic_overlap(set(), set()) == 1.0

def test_semantic_disjoint():
    a = {"apple fruit red"}; b = {"deploy system now"}
    assert semantic_overlap(a, b) < 0.5

# ── God fixed — no string reversal ───────────────────────────────────
def test_god_no_string_reversal():
    from echo_system_v4 import GodPrimitive
    g = GodPrimitive()
    out = g.run("What is the best deployment strategy?")
    for claim in out["claims"]:
        assert "..." not in claim or "perspective" not in claim,             f"God still using placeholder: {claim}"
        # reversed string would contain reversed words
        assert "?ygetarts" not in claim, f"God reversed input string: {claim}"

# ── InputSpec gate restored ───────────────────────────────────────────
def test_gate_rejects_short():
    try:
        InputSpec.classify("vague")
        assert False, "Should reject"
    except ValueError as e:
        assert "REJECTED" in str(e) or "REFORMULATE" in str(e)

def test_gate_accepts_question():
    r = InputSpec.classify("What is the deployment status?")
    assert r["type"] == "question"

def test_gate_accepts_audit():
    r = InputSpec.classify("The system is missing environment variables")
    assert r["type"] == "audit_statement"

# ── Full run ─────────────────────────────────────────────────────────
def test_full_run_v4():
    r = run("What should we deploy first?", {})
    assert r["valid"] is not None
    for s in REQUIRED:
        assert s in r["tp"], f"Missing {s}"

if __name__ == "__main__":
    tests = [
        test_substantive_valid, test_substantive_missing_verb,
        test_substantive_deploy_verb_accepted,
        test_graph_add_and_query, test_graph_fault_tolerant,
        test_graph_contradictions,
        test_semantic_identical, test_semantic_empty, test_semantic_disjoint,
        test_god_no_string_reversal,
        test_gate_rejects_short, test_gate_accepts_question, test_gate_accepts_audit,
        test_full_run_v4,
    ]
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
