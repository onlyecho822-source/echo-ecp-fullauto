#!/usr/bin/env python3
"""
Echo Compression Stack v1.1-hardened Validator
Repo: onlyecho822-source/echo-ecp-fullauto

Usage:
    python validate_protocol.py <file>
    cat file.txt | python validate_protocol.py -
    python validate_protocol.py <file> --explain
    python validate_protocol.py <file> --strict-order
"""

import re, sys, argparse
from typing import List, Tuple, Dict

REQUIRED_FIELDS = [
    "Scope:", "Truth:", "Mode:", "Confidence:", "Decision:", "Level:",
    "Claim:", "Risk:", "Action:", "Test:", "Audit:", "Why not higher:"
]
CANONICAL_ORDER = REQUIRED_FIELDS

TRUTH_VALUES    = {"✔", "≈", "∼"}
MODE_VALUES     = {"⚙", "⚖", "Δ", "🧪", "🔍"}
DECISION_VALUES = {"ACT", "INFO", "CHK", "HOLD", "ESC"}
LEVEL_VALUES    = {"L0", "L1", "L2", "L3"}
AUDIT_PREFIXES  = ("Assumes:", "Breaks if:", "Could be wrong because:", "Need to falsify:")

HIGH_STAKES_KW = ["deploy", "patch", "operational", "safety", "financial",
                  "legal", "anomaly", "alert", "escalate", "critical"]


def parse_fields(text: str) -> Dict[str, str]:
    fields = {}
    for line in text.splitlines():
        for f in REQUIRED_FIELDS:
            if line.startswith(f):
                fields[f] = line[len(f):].strip()
                break
    return fields


def validate_syntax(fields: Dict[str, str]) -> List[str]:
    errors = []
    for f in REQUIRED_FIELDS:
        if f not in fields:
            errors.append(f"Missing required field: {f}")
    if "Truth:" in fields and fields["Truth:"] not in TRUTH_VALUES:
        errors.append(f"Truth: must be one of {TRUTH_VALUES} — got '{fields['Truth:']}'")
    if "Mode:" in fields and fields["Mode:"] not in MODE_VALUES:
        errors.append(f"Mode: must be one of {MODE_VALUES} — got '{fields['Mode:']}'")
    if "Decision:" in fields and fields["Decision:"] not in DECISION_VALUES:
        errors.append(f"Decision: must be one of {DECISION_VALUES} — got '{fields['Decision:']}'")
    if "Level:" in fields and fields["Level:"] not in LEVEL_VALUES:
        errors.append(f"Level: must be one of {LEVEL_VALUES} — got '{fields['Level:']}'")
    conf = fields.get("Confidence:", "")
    m = re.search(r"(\d+)%", conf)
    if not m:
        errors.append("Confidence: must be a percentage like '94%'")
    elif not (0 <= int(m.group(1)) <= 100):
        errors.append("Confidence: out of 0–100 range")
    audit = fields.get("Audit:", "")
    if audit and not any(audit.startswith(p) for p in AUDIT_PREFIXES):
        errors.append(f"Audit: must start with one of {AUDIT_PREFIXES}")
    return errors


def validate_semantic(fields: Dict[str, str], explain: bool = False) -> Tuple[List[str], List[str]]:
    warnings, suggestions = [], []

    def w(msg, fix=""):
        warnings.append(msg)
        if explain and fix:
            suggestions.append(f"  Fix: {fix}")

    # Truth ∼ + high confidence
    if fields.get("Truth:") == "∼":
        m = re.search(r"(\d+)%", fields.get("Confidence:", ""))
        if m and int(m.group(1)) > 85:
            w("Truth: ∼ with Confidence >85% — speculative claim is overconfident",
              "Lower confidence to ≤85% or upgrade Truth to ≈ with documented model.")

    # Δ — requires change evidence
    if fields.get("Mode:") == "Δ":
        combined = fields.get("Claim:", "") + " " + fields.get("Risk:", "")
        delta_patterns = [
            r"\d+\s*[→->]\s*\d+",
            r"\b(increased|decreased|rose|fell|spiked|dropped|shifted|emerged|changed from|went from|before|after)\b",
            r"\d{2}:\d{2}",
            r"\d{4}-\d{2}-\d{2}",
            r"\bover\s+\d+",
            r"\bwithin\s+\d+",
        ]
        if not any(re.search(p, combined, re.IGNORECASE) for p in delta_patterns):
            w("Mode: Δ but no change evidence in Claim/Risk (need numeric delta, directional word, or timestamps)",
              "Add e.g. 'increased from 400 to 780 km/s' or 'at 13:10–13:15 UTC'.")

    # ⚖ — requires explicit comparator
    if fields.get("Mode:") == "⚖":
        claim = fields.get("Claim:", "")
        comparators = [r" vs ", r" versus ", r" greater than", r" less than",
                       r" faster than", r" slower than", r" compared to", r" relative to"]
        if not any(re.search(c, claim.lower()) for c in comparators):
            w("Mode: ⚖ but Claim lacks explicit comparator (vs, versus, greater/less than, compared to)",
              "Rewrite Claim as 'X vs Y' or 'X greater than Y'.")

    # 🧪 — needs real test
    if fields.get("Mode:") == "🧪":
        test = fields.get("Test:", "")
        if not test or len(test) < 8 or test.lower() in ["none", "n/a", "tbd"]:
            w("Mode: 🧪 but Test: is empty or trivial",
              "Describe a concrete, falsifiable validation step.")

    # Confidence >95% + weak Why not higher
    m = re.search(r"(\d+)%", fields.get("Confidence:", ""))
    if m and int(m.group(1)) > 95:
        why = fields.get("Why not higher:", "").lower()
        if not why or why in ["unknown", "none", "n/a", ""]:
            w("Confidence >95% but Why not higher: is empty or meaningless",
              "State the specific limitation, e.g. 'single data source' or 'no external validation'.")

    # Risk: none
    if fields.get("Risk:", "").lower() in ["none", "n/a", ""]:
        w("Risk: none — if truly no risk, justify explicitly",
          "Identify at least one plausible failure condition.")

    # L0 + high-confidence operational claim
    if fields.get("Level:") == "L0":
        m = re.search(r"(\d+)%", fields.get("Confidence:", ""))
        claim = fields.get("Claim:", "").lower()
        if m and int(m.group(1)) > 85:
            if any(kw in claim for kw in HIGH_STAKES_KW):
                w("Level L0 with high-confidence operational claim — upgrade to L1 or L2",
                  "Change Level to L1 and add full protocol block.")

    return warnings, suggestions


def validate_compatibility(fields: Dict[str, str]) -> List[str]:
    issues = []

    def fatal(msg): issues.append(f"FATAL: {msg}")
    def compat(msg): issues.append(f"COMPAT: {msg}")

    # Unknown symbols in controlled fields
    for field, allowed in [("Truth:", TRUTH_VALUES), ("Mode:", MODE_VALUES),
                            ("Decision:", DECISION_VALUES), ("Level:", LEVEL_VALUES)]:
        val = fields.get(field, "")
        if val and val not in allowed:
            fatal(f"Unknown symbol '{val}' in {field}. Allowed: {allowed}")

    # L0 + ACT/ESC
    if fields.get("Level:") == "L0" and fields.get("Decision:") in ("ACT", "ESC"):
        fatal("Level L0 with Decision ACT or ESC is not permitted. Upgrade Level to L1+.")

    # Truth ∼ + ACT
    if fields.get("Truth:") == "∼" and fields.get("Decision:") == "ACT":
        compat("Truth: ∼ with Decision: ACT — mark explicitly as exploratory action.")

    return issues


def check_order(fields: Dict[str, str], text: str) -> List[str]:
    warnings = []
    found_order = []
    for line in text.splitlines():
        for f in REQUIRED_FIELDS:
            if line.startswith(f) and f not in found_order:
                found_order.append(f)
    if found_order != CANONICAL_ORDER[:len(found_order)]:
        warnings.append(f"WARN: Field order non-canonical. Expected: {CANONICAL_ORDER}")
    return warnings


def validate(text: str, explain=False, strict_order=False):
    fields = parse_fields(text)
    errors   = validate_syntax(fields)
    warns, suggestions = validate_semantic(fields, explain)
    compat   = validate_compatibility(fields)
    order_w  = check_order(fields, text) if strict_order else []
    return errors, warns, compat, order_w, suggestions


def main():
    parser = argparse.ArgumentParser(description="Echo Compression Stack v1.1-hardened Validator")
    parser.add_argument("file", nargs="?", help="File path or '-' for stdin")
    parser.add_argument("--explain", action="store_true", help="Show fix suggestions")
    parser.add_argument("--suggest", action="store_true", help="Alias for --explain")
    parser.add_argument("--strict-order", action="store_true", help="Warn on non-canonical field order")
    args = parser.parse_args()

    if not args.file:
        print("Usage: validate_protocol.py <file> [--explain] [--strict-order]", file=sys.stderr)
        sys.exit(1)
    content = sys.stdin.read() if args.file == "-" else open(args.file).read()

    explain = args.explain or args.suggest
    errors, warns, compat, order_w, suggestions = validate(content, explain, args.strict_order)

    for e in errors:          print(f"ERROR:   {e}")
    for w in warns:           print(f"WARNING: {w}")
    for c in compat:          print(c)
    for o in order_w:         print(o)
    if suggestions:
        print("\nSUGGESTIONS:")
        for s in suggestions: print(s)

    fatal_count = sum(1 for c in compat if c.startswith("FATAL"))
    if errors or fatal_count:
        print("\nResult: FAIL")
        sys.exit(1)
    else:
        print(f"\nResult: PASS ({len(warns)} warning(s), {len(compat)} compat note(s))")
        sys.exit(0)


if __name__ == "__main__":
    main()
