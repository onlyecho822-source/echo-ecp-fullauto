#!/usr/bin/env python3
"""
EXAMPLE: Basic usage of echo-ecp-fullauto
==========================================
Shows the three most common entry points.
Run from the repo root: python examples/basic_usage.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from echo_system_v4 import run, render, InputSpec

print("=" * 60)
print("echo-ecp-fullauto — Basic Usage Examples")
print("=" * 60)

# ── Example 1: Question (Standard flow) ──────────────────────────────
print("\n[1] Question — Standard flow")
print("-" * 40)

result = run("What is the highest-leverage action to reduce deployment time?")
print(f"Flow: {result['flow']} | Passes: {result['pass_count']} | Valid: {result['valid']}")
print(f"Convergence: {result['conv_score']:.0%} | False-conv: {result['false_conv']}")
print(f"\nTop 3 invariant claims:")
for claim in result["tp"]["Invariant"][:3]:
    print(f"  · {claim[:90]}")
print(f"\nAction:")
for a in result["tp"]["Action"]:
    print(f"  → {a[:90]}")

# ── Example 2: Audit statement (Audit flow) ──────────────────────────
print("\n\n[2] Audit statement — Audit flow")
print("-" * 40)

result = run("The authentication system is missing rate limiting and session timeout")
print(f"Flow: {result['flow']} | Passes: {result['pass_count']}")
print(f"\nLabel distribution:")
for label, claims in result["tp"]["Labels"].items():
    if claims:
        print(f"  {label:<24} {len(claims)} claims")

# ── Example 3: Time-pressure question (Fast flow) ────────────────────
print("\n\n[3] Time-pressure question — Fast flow")
print("-" * 40)

result = run(
    "Should we ship the current build or wait for the security audit?",
    {"time_pressure": True}
)
print(f"Flow: {result['flow']} | Passes: {result['pass_count']}")
print(f"\nDeceptionIndicating claims (challenge these before deciding):")
for c in result["tp"]["Labels"].get("DeceptionIndicating", [])[:3]:
    print(f"  🔴 {c[:90]}")

# ── Example 4: Full rendered output ──────────────────────────────────
print("\n\n[4] Full rendered Truth Partition")
print("-" * 40)

result = run(
    "The onboarding flow is missing email verification and has no error state handling",
    {"audit": True}
)
print(render(result))

# ── Example 5: Gate rejection ─────────────────────────────────────────
print("\n\n[5] Gate — rejection and reformulation")
print("-" * 40)

bad_inputs = [
    "vague",
    "things need fixing",
    "I dunno what to do",
]
for text in bad_inputs:
    try:
        InputSpec.classify(text)
        print(f"  ACCEPTED: {text}")
    except ValueError as e:
        print(f"  REJECTED: {text!r:<35} → {str(e)[:60]}")

print("\n" + "=" * 60)
print("Run echo_system_v4.py for interactive mode.")
print("=" * 60)
