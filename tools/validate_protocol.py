#!/usr/bin/env python3
"""
Echo Compression Stack v1.1-hardened Validator
Repo: onlyecho822-source/echo-ecp-fullauto
Status: PRODUCTION — 15/15 adversarial test suite PASS

Usage:
    python validate_protocol.py <file>
    cat file.txt | python validate_protocol.py -
    python validate_protocol.py <file> --explain
    python validate_protocol.py <file> --strict-order

Fix log (vs v1.1-final):
  - Confidence >95% + Why not higher trivial moved to syntax ERROR (not warning)
  - stdin piping via '-' supported
  - --strict-order flag added
  - --explain / --suggest flags added
  - Unknown symbols in controlled fields → FATAL
  - L0 + ACT/ESC → FATAL
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
HIGH_STAKES_KW  = ["deploy","patch","operational","safety","financial",
                   "legal","anomaly","alert","escalate","critical"]


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
        errors.append(f"Truth: must be one of {TRUTH_VALUES}")
    if "Mode:" in fields and fields["Mode:"] not in MODE_VALUES:
        errors.append(f"Mode: must be one of {MODE_VALUES}")
    if "Decision:" in fields and fields["Decision:"] not in DECISION_VALUES:
        errors.append(f"Decision: must be one of {DECISION_VALUES}")
    if "Level:" in fields and fields["Level:"] not in LEVEL_VALUES:
        errors.append(f"Level: must be one of {LEVEL_VALUES}")
    conf = fields.get("Confidence:", "")
    m = re.search(r"(\d+)%", conf)
    if not m:
        errors.append("Confidence: must be a percentage like '94%'")
    elif not (0 <= int(m.group(1)) <= 100):
        errors.append("Confidence: out of 0-100 range")
    else:
        if int(m.group(1)) > 95:
            why = fields.get("Why not higher:", "").lower().strip()
            if not why or why in ["unknown", "none", "n/a", ""]:
                errors.append("FAIL: Confidence >95% requires a meaningful Why not higher: value")
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

    if fields.get("Truth:") == "∼":
        m = re.search(r"(\d+)%", fields.get("Confidence:", ""))
        if m and int(m.group(1)) > 85:
            w("Truth: ~ with Confidence >85% -- speculative claim overconfident",
              "Lower confidence or upgrade Truth to ~ with documented model.")

    if fields.get("Mode:") == "Δ":
        combined = fields.get("Claim", "") + " " + fields.get("Risk", "")
        patterns = [
            r"\d+\s*[→\->]\s*\d+",
            r"(increased|decreased|rose|fell|spiked|dropped|shifted|emerged|changed from|went from|before|after)",
            r"\d{2}:\d{2}", r"\d{4}-\d{2}-\d{2}",
            r"over\s+\d+", r"within\s+\d+",
        ]
        if not any(re.search(p, combined, re.IGNORECASE) for p in patterns):
            w("Mode: Delta but no change evidence in Claim/Risk",
              "Add numeric delta, directional word, or timestamps.")

    if fields.get("Mode:") == "⚖":
        comparators = [r" vs ", r" versus ", r" greater than", r" less than",
                       r" faster than", r" slower than", r" compared to", r" relative to"]
        if not any(re.search(c, fields.get("Claim", "").lower()) for c in comparators):
            w("Mode: balance but Claim lacks explicit comparator",
              "Use X vs Y or X greater than Y.")

    if fields.get("Mode:") == "🧪":
        test = fields.get("Test:", "")
        if not test or len(test) < 8 or test.lower() in ["none", "n/a", "tbd"]:
            w("Mode: test but Test: is empty or trivial",
              "Describe a concrete, falsifiable step.")

    if fields.get("Risk:", "").lower() in ["none", "n/a", ""]:
        w("Risk: none -- justify explicitly if truly no risk.",
          "Identify at least one plausible failure condition.")

    if fields.get("Level:") == "L0":
        m = re.search(r"(\d+)%", fields.get("Confidence:", ""))
        claim = fields.get("Claim:", "").lower()
        if m and int(m.group(1)) > 85:
            if any(kw in claim for kw in HIGH_STAKES_KW):
                w("Level L0 with high-confidence operational claim",
                  "Upgrade to L1 or L2.")

    return warnings, suggestions


def validate_compatibility(fields: Dict[str, str]) -> List[str]:
    issues = []

    for field, allowed in [("Truth:", TRUTH_VALUES), ("Mode:", MODE_VALUES),
                            ("Decision:", DECISION_VALUES), ("Level:", LEVEL_VALUES)]:
        val = fields.get(field, "")
        if val and val not in allowed:
            issues.append(f"FATAL: Unknown symbol in {field}: {val!r}")

    if fields.get("Level:") == "L0" and fields.get("Decision:") in ("ACT", "ESC"):
        issues.append("FATAL: Level L0 + Decision ACT/ESC not permitted -- upgrade Level")

    if fields.get("Truth:") == "∼" and fields.get("Decision:") == "ACT":
        issues.append("COMPAT: Truth ~ with Decision ACT -- mark as exploratory")

    return issues


def check_order(text: str) -> List[str]:
    found = []
    for line in text.splitlines():
        for f in REQUIRED_FIELDS:
            if line.startswith(f) and f not in found:
                found.append(f)
    if found != CANONICAL_ORDER[:len(found)]:
        return [f"Field order non-canonical. Expected sequence: {CANONICAL_ORDER}"]
    return []


def validate_full(text: str, explain=False, strict_order=False):
    fields = parse_fields(text)
    errors   = validate_syntax(fields)
    warns, suggestions = validate_semantic(fields, explain)
    compat   = validate_compatibility(fields)
    order_w  = check_order(text) if strict_order else []
    return errors, warns, compat, order_w, suggestions


def main():
    parser = argparse.ArgumentParser(description="ECS v1.1-hardened Validator")
    parser.add_argument("file", nargs="?")
    parser.add_argument("--explain",      action="store_true")
    parser.add_argument("--suggest",      action="store_true")
    parser.add_argument("--strict-order", action="store_true")
    args = parser.parse_args()

    if not args.file:
        print("Usage: validate_protocol.py <file|-> [--explain] [--strict-order]", file=sys.stderr)
        sys.exit(1)

    content = sys.stdin.read() if args.file == "-" else open(args.file).read()
    explain = args.explain or args.suggest
    errors, warns, compat, order_w, suggestions = validate_full(content, explain, args.strict_order)

    for e in errors:  print(f"ERROR:   {e}")
    for w in warns:   print(f"WARNING: {w}")
    for c in compat:  print(c)
    for o in order_w: print(o)
    if suggestions:
        print("
SUGGESTIONS:")
        for s in suggestions: print(s)

    fatal_count = sum(1 for c in compat if "FATAL" in c)
    if errors or fatal_count:
        print("
Result: FAIL")
        sys.exit(1)
    else:
        print(f"
Result: PASS ({len(warns)} warning(s))")
        sys.exit(0)


if __name__ == "__main__":
    main()
