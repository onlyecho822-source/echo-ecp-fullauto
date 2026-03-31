#!/usr/bin/env python3
"""
test_v4.py — Echo System v4.0 specific tests
==============================================
Authority : Nathan Poinsette (∇θ Operator)
Tests     : 14
Covers    : SubstantiveValidator (valid, missing verb, deploy accepted),
            GraphMemory (add+query, fault tolerance, contradictions),
            semantic_overlap (identical, empty, disjoint),
            God fix (no string reversal),
            InputSpec gate regression (v4 gate was weaker — now fixed),
            full pipeline run

Run: python tests/test_v4.py
     python -m pytest tests/test_v4.py -v
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from echo_system_v4 import (
    SubstantiveValidator, GraphMemory, semantic_overlap,
    InputSpec, run, REQUIRED
)


# ── SubstantiveValidator ─────────────────────────────────────────────

def test_substantive_valid():
    """A well-formed partition with evidence+invariant overlap and verb should pass."""
    tp = {
        "Invariant":     ["Deploy art-of-proof system to staging"],
        "Evidence":      ["Deploy art-of-proof tests passing in CI"],
        "Uncertainty":   ["Unknown production load behavior"],
        "Failure Modes": ["Missing env vars on Railway"],
        "Action":        ["Deploy the system to Netlify and Railway now"],
        "Labels": {},
    }
    ok, issues = SubstantiveValidator.validate(tp)
    assert ok, f"Expected valid, got: {issues}"


def test_substantive_missing_verb():
    """Action without a concrete verb should fail SubstantiveValidator."""
    tp = {
        "Invariant":     ["System works"],
        "Evidence":      ["System works"],
        "Uncertainty":   ["Unknown"],
        "Failure Modes": ["Failure"],
        "Action":        ["The thing should happen somehow"],
        "Labels": {},
    }
    ok, issues = SubstantiveValidator.validate(tp)
    assert not ok, "Should fail — no verb"
    assert any("verb" in i.lower() for i in issues),         f"Issue should mention verb, got: {issues}"


def test_substantive_deploy_verb_accepted():
    """
    'deploy' was missing from Manus v4 verb list — regression test.
    Valid deployment actions should NOT be flagged as lacking a verb.
    """
    tp = {
        "Invariant":     ["Deploy the art-of-proof system"],
        "Evidence":      ["Deploy evidence: tests passing"],
        "Uncertainty":   ["Unknown production behavior"],
        "Failure Modes": ["Billing exhaustion"],
        "Action":        ["Deploy art-of-proof to production environment"],
        "Labels": {},
    }
    ok, issues = SubstantiveValidator.validate(tp)
    assert ok, f"'deploy' should be accepted as a concrete verb. Issues: {issues}"


# ── GraphMemory ──────────────────────────────────────────────────────

def test_graph_add_and_query():
    """Claims added to GraphMemory should be queryable by keyword."""
    mem = GraphMemory("_test_graph.json")
    mem.add_claim("System is robust under concurrent load", "test_source")
    history = mem.get_history(["robust"])
    assert len(history) >= 1, "Should find the stored claim"
    assert history[0]["claim"] == "System is robust under concurrent load"
    if os.path.exists("_test_graph.json"): os.remove("_test_graph.json")


def test_graph_fault_tolerant():
    """
    GraphMemory._save() should not crash on unwritable path.
    FIXED in v4: was crashing without try/except.
    """
    mem = GraphMemory("/nonexistent/path/graph.json")
    mem.add_claim("test claim", "test")  # should not raise


def test_graph_contradictions():
    """Claims containing 'not' with shared keywords should be detected as contradictions."""
    mem = GraphMemory("_test_graph2.json")
    mem.add_claim("The system is not reliable under load", "test")
    contras = mem.contradictions("The system is reliable")
    assert len(contras) >= 1, "Should detect contradiction"
    if os.path.exists("_test_graph2.json"): os.remove("_test_graph2.json")


# ── Semantic overlap ─────────────────────────────────────────────────

def test_semantic_identical():
    """Identical claim sets should score >= 0.99."""
    a = {"the system deploys correctly to production"}
    assert semantic_overlap(a, a) >= 0.99, "Identical sets must score near 1.0"


def test_semantic_empty():
    """Two empty sets should score 1.0 (convergence convention)."""
    assert semantic_overlap(set(), set()) == 1.0


def test_semantic_disjoint():
    """Completely unrelated claim sets should score below 0.5."""
    a = {"apple fruit red delicious orchard"}
    b = {"deploy system production environment"}
    assert semantic_overlap(a, b) < 0.5, "Unrelated sets should score low"


# ── God fix — no string reversal ─────────────────────────────────────

def test_god_no_string_reversal():
    """
    God was reversing the input string as a placeholder for creativity.
    FIXED in v4. This test verifies the fix holds.
    Reversed input would produce strings like '?foorp-fo-tra yolped...'
    """
    from echo_system_v4 import GodPrimitive
    g = GodPrimitive()
    out = g.run("What is the best deployment strategy for production?")
    for claim in out["claims"]:
        assert "?ygetarts" not in claim,             f"God is reversing input string: {claim}"
        assert "tnemyolped" not in claim,             f"God is reversing input string: {claim}"


# ── InputSpec gate regression ─────────────────────────────────────────

def test_gate_rejects_short():
    """
    v4 Manus gate was accepting 5-char inputs like 'vague'.
    This regression test verifies the v3.1 gate was restored.
    """
    for bad in ["vague", "ok", "hi", "do it"]:
        try:
            InputSpec.classify(bad)
            assert False, f"Should have rejected: {bad!r}"
        except ValueError as e:
            assert "REJECTED" in str(e) or "REFORMULATE" in str(e),                 f"Expected REJECTED/REFORMULATE for {bad!r}, got: {e}"


def test_gate_accepts_question():
    """Standard question should be accepted with type='question'."""
    r = InputSpec.classify("What is the deployment status today?")
    assert r["type"] == "question"


def test_gate_accepts_audit():
    """Audit statement with problem term should be accepted."""
    r = InputSpec.classify("The system is missing environment variables")
    assert r["type"] == "audit_statement"


# ── Full pipeline ────────────────────────────────────────────────────

def test_full_run_v4():
    """Full v4 pipeline should produce a valid result with all five fields."""
    r = run("What should we deploy first given limited capacity?", {})
    assert r["valid"] is not None, "valid field must be present"
    for section in REQUIRED:
        assert section in r["tp"], f"Missing required section: {section}"
    assert "semantic" in r, "v4 result must include semantic flag"


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
            t(); print(f"  ✅ {t.__name__}"); passed += 1
        except Exception as e:
            print(f"  ❌ {t.__name__}: {e}"); failed += 1
    print(f"\n{passed} passed | {failed} failed")
