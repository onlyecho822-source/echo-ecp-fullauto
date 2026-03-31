#!/usr/bin/env python3
"""
EXAMPLE: Advanced usage — GraphMemory, SubstantiveValidator, batch
===================================================================
Run from the repo root: python examples/advanced_usage.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from echo_system_v4 import (
    run, render, GraphMemory, SubstantiveValidator, REQUIRED
)

print("=" * 60)
print("echo-ecp-fullauto — Advanced Usage Examples")
print("=" * 60)

# ── GraphMemory: query history across runs ────────────────────────────
print("\n[1] GraphMemory — store and query invariants over time")
print("-" * 40)

mem = GraphMemory("example_graph.json")

# Run three related problems — memory accumulates across them
problems = [
    "What is the highest-leverage deployment action right now?",
    "The deployment pipeline is missing automated rollback",
    "Should we prioritize deployment speed or deployment safety?",
]
for p in problems:
    result = run(p)
    # Each run stores converged invariants to GraphMemory automatically
    print(f"  Ran: {p[:60]}")

# Query what the system has learned about "deployment"
history = mem.get_history(["deployment", "deploy"])
print(f"\n  Claims stored about deployment: {len(history)}")
for record in history[:3]:
    print(f"  [{record['version']}] {record['claim'][:80]}")

# Check for contradictions
new_claim = "Deployment speed is the only priority"
contras = mem.contradictions(new_claim)
print(f"\n  Contradictions found for '{new_claim[:40]}':")
for c in contras[:2]:
    print(f"  ⚡ {c[:80]}")

# Cleanup
if os.path.exists("example_graph.json"):
    os.remove("example_graph.json")

# ── SubstantiveValidator: check your own Truth Partitions ────────────
print("\n\n[2] SubstantiveValidator — quality check on custom partitions")
print("-" * 40)

partitions = [
    {
        "label": "Good partition",
        "tp": {
            "Invariant": ["The deploy pipeline fails under concurrent load"],
            "Evidence":  ["Deploy pipeline tested under concurrent load — 3 failures in 10 runs"],
            "Uncertainty":   ["Not tested beyond 10 concurrent users"],
            "Failure Modes": ["Race condition in lock acquisition — not yet diagnosed"],
            "Action":        ["Deploy a load test to staging environment this week"],
            "Labels": {},
        }
    },
    {
        "label": "Bad partition — vague action, no evidence overlap",
        "tp": {
            "Invariant": ["The system has quality issues"],
            "Evidence":  ["Things went wrong"],
            "Uncertainty":   ["Unknown"],
            "Failure Modes": ["Unknown"],
            "Action":        ["Do something about it"],
            "Labels": {},
        }
    },
]

for item in partitions:
    ok, issues = SubstantiveValidator.validate(item["tp"])
    status = "✅ VALID" if ok else f"❌ INVALID ({len(issues)} issues)"
    print(f"  {item['label']}: {status}")
    for issue in issues:
        print(f"    · {issue}")

# ── Batch processing ──────────────────────────────────────────────────
print("\n\n[3] Batch processing — run multiple problems, compare")
print("-" * 40)

batch = [
    ("What is the core bottleneck in our release process?", {}),
    ("The release checklist is missing security sign-off", {}),
    ("Should we automate releases if automation introduces new failure modes?", {}),
]

results = []
for problem, ctx in batch:
    r = run(problem, ctx)
    results.append(r)
    label_summary = {k: len(v) for k, v in r["tp"]["Labels"].items() if v}
    print(f"  [{r['flow']:<10}] {problem[:55]}")
    print(f"    Labels: {label_summary}")

# Find which problem produced the most DeceptionIndicating claims
most_adversarial = max(results,
    key=lambda r: len(r["tp"]["Labels"].get("DeceptionIndicating", [])))
print(f"\n  Most adversarial: {batch[results.index(most_adversarial)][0][:60]}")
print(f"  DeceptionIndicating count: {len(most_adversarial['tp']['Labels'].get('DeceptionIndicating', []))}")

print("\n" + "=" * 60)
print("See docs/PRIMITIVES.md for LLM integration guide.")
print("=" * 60)
