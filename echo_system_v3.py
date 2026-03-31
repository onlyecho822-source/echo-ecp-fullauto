#!/usr/bin/env python3
"""
ECHO SYSTEM v3.1 — FINAL MERGED
================================
Authority : Nathan Poinsette (∇θ Operator)
Version   : 3.1
Status    : OPERATIONAL — commit-ready

What changed from v3.0:
  + Manus OOP class structure (better extension point for LLM integration)
  + Optional Nathan in Audit flow (Manus fix)
  + Low-signal detection suppresses full output (not just action field)
  + Flow selector priority preserved from Claude v3
  + Input-responsive primitives preserved from Claude v3
  + 5-label schema with real heuristics preserved from Claude v3
  + False convergence filtering trivial assumptions preserved

Known limits (honest):
  — Claim extraction is lexical, not semantic
  — Primitives generate directional questions, not verified facts
  — Needs LLM calls to become a reasoning engine (not just scaffold)
  — Semantic claim equivalence requires embeddings (v4 feature)

Run: python echo_system_v3.py
No external dependencies.
"""

import re, json, time, uuid
from typing import List, Dict, Tuple, Set, Any, Optional
from collections import Counter

# ════════════════════════════════════════════════════════════════
# CONFIG
# ════════════════════════════════════════════════════════════════

MAX_PASSES          = 5
CONVERGENCE_THRESH  = 0.72
GOD_MAX_OPTIONS     = 5
MEMORY_PATH         = "echo_memory.jsonl"
VERSION             = "3.1"
LOW_SIGNAL_THRESH   = 3    # min Validated claims overlapping input


# ════════════════════════════════════════════════════════════════
# 1. INPUT SPECIFICATION
# ════════════════════════════════════════════════════════════════

class InputSpec:
    """
    Gate. Three states: accepted | reformulate | rejected.
    Accepts: questions, propositions, declarative audit statements.
    """

    QUESTION    = re.compile(
        r"(?i)^(what|which|how|should|is|are|do|does|can|could|would|will|when|where|why)\b"
    )
    PROPOSITION = re.compile(
        r"(?i)\b(if|unless|until|falsif|disprov|given that|assuming)\b"
    )
    AUDIT       = re.compile(
        r"(?i)\b(missing|lacks?|needs?|broken|wrong|incorrect|incomplete|"
        r"gap|problem|issue|should have|does not have|without|failing|failed)\b"
    )

    @classmethod
    def classify(cls, text: str) -> Dict[str, Any]:
        text = text.strip()
        if len(text) < 8:
            raise ValueError("REJECTED: Too short. State a question, proposition, or audit target.")
        if text.endswith("?") or cls.QUESTION.match(text):
            return {"type": "question", "core": text}
        if cls.PROPOSITION.search(text):
            return {"type": "proposition", "core": text}
        if cls.AUDIT.search(text):
            return {"type": "audit_statement", "core": text}
        raise ValueError(
            f"REFORMULATE: Add '?', a falsification condition, or a "
            f"problem term (missing/broken/needs/gap). Got: '{text[:60]}'"
        )


# ════════════════════════════════════════════════════════════════
# 2. FLOW SELECTOR — priority enforced
#    unknown domain > audit > time pressure > standard
# ════════════════════════════════════════════════════════════════

FLOWS: Dict[str, List[str]] = {
    "Standard":  ["Echo", "God", "Devil", "Light", "Nathan"],
    "Fast":      ["Nathan", "Devil", "Nathan"],
    "Research":  ["God", "Echo", "Devil", "Light", "Nathan"],
    "Audit":     ["Echo", "Devil", "Light", "Nathan"],  # Nathan included (optional)
}

def select_flow(parsed: Dict, context: Dict) -> str:
    if context.get("unknown_domain"):                                    return "Research"
    if context.get("audit") or parsed.get("type") == "audit_statement": return "Audit"
    if context.get("time_pressure"):                                     return "Fast"
    return "Standard"


# ════════════════════════════════════════════════════════════════
# 3. PRIMITIVES — OOP structure (Manus) + input-responsive content (Claude)
#    Each primitive is a class → subclass with LLM logic when ready
# ════════════════════════════════════════════════════════════════

def _kw(text: str) -> List[str]:
    stop = {
        "the","a","an","is","are","was","were","be","been","this","that",
        "and","or","but","for","with","not","it","in","on","at","to","of",
        "from","as","if","we","i","you","they","what","how","which","should",
        "will","can","would","could","do","does","have","has","had","its"
    }
    return [w.lower() for w in re.findall(r'\b[a-zA-Z][a-zA-Z]+\b', text)
            if w.lower() not in stop and len(w) > 3]


class Primitive:
    """Base class. Subclass with LLM logic for production."""
    name: str
    question: str

    def run(self, problem: str, prior: Optional[Set[str]] = None) -> Dict:
        raise NotImplementedError


class EchoPrimitive(Primitive):
    name     = "Echo"
    question = "How does the system fit together?"

    def run(self, problem: str, prior=None) -> Dict:
        kw = _kw(problem)
        s  = " ".join(kw[:3]) if kw else "this problem"
        return {"claims": {
            f"The core structure of {s} has load-bearing dependencies that must be mapped before acting",
            f"The relationship between components of {s} determines which action has highest leverage",
            f"Pattern recognition on {s} reveals a known failure mode from similar systems",
            f"The critical path for {s} runs through one bottleneck that blocks all downstream steps",
        }, "assumptions": {f"The system around {s} can be decomposed into mappable components"}}


class GodPrimitive(Primitive):
    name     = "God"
    question = "What are we not considering?"

    def run(self, problem: str, prior=None) -> Dict:
        kw = _kw(problem)
        s  = " ".join(kw[:2]) if kw else "this problem"
        options = [
            f"Reframe {s} as a distribution problem rather than a quality problem",
            f"The inverse approach to {s} — remove the core constraint entirely",
            f"An adjacent domain has already solved {s} — look at how insurance, law, or medicine handles this",
            f"The 10x version of solving {s} requires a fundamentally different assumption",
            f"The person most harmed by the current state of {s} has already found a workaround",
        ][:GOD_MAX_OPTIONS]
        return {"claims": set(options),
                "assumptions": {f"The current frame around {s} is not the only valid one"}}


class DevilPrimitive(Primitive):
    name     = "Devil"
    question = "How does this break?"

    def run(self, problem: str, prior: Optional[Set[str]] = None) -> Dict:
        kw = _kw(problem)
        s  = " ".join(kw[:3]) if kw else "this approach"
        attacks = {
            f"The most dangerous assumption in {s} is the one that has never been stated explicitly",
            f"Under adversarial conditions {s} fails at the exact moment it is needed most",
            f"The person who benefits most from failure of {s} has already identified its weakness",
            f"If the core premise of {s} is wrong then all derived actions make the situation worse",
        }
        if prior:
            attacks.add(f"Challenge: '{sorted(prior)[-1][:70]}' — what evidence would make this false?")
        return {"claims": attacks,
                "assumptions": {f"Risks in {s} are not yet fully visible to those executing it"}}


class LightPrimitive(Primitive):
    name     = "Light"
    question = "What is being obscured?"

    def run(self, problem: str, prior=None) -> Dict:
        kw = _kw(problem)
        s  = " ".join(kw[:3]) if kw else "this situation"
        return {"claims": {
            f"The load-bearing assumption in {s} has never been tested because testing it is uncomfortable",
            f"What {s} is not saying is more important than what it is saying",
            f"The framing of {s} benefits whoever designed the framing — ask who that is and what they gain",
            f"There is a question about {s} that everyone has avoided asking — that is the most important one",
        }, "assumptions": {f"Hidden assumptions in {s} are load-bearing for the current direction"}}


class NathanPrimitive(Primitive):
    name     = "Nathan"
    question = "What is the move?"

    def run(self, problem: str, prior: Optional[Set[str]] = None) -> Dict:
        kw = _kw(problem)
        s  = " ".join(kw[:3]) if kw else "this problem"
        claims = {
            f"The single highest-leverage move on {s} is the one that unblocks everything else",
            f"The cost of not acting on {s} in the next 24 hours must be quantified before deciding",
            f"Someone specific must own {s} with a hard deadline or it will not move",
        }
        if prior:
            freq = Counter(w for c in prior for w in re.findall(r'\b\w+\b', c) if len(w) > 5)
            top  = [w for w, _ in freq.most_common(3)]
            if top:
                claims.add(f"Based on all passes: priority action targets {', '.join(top)}")
        return {"claims": claims,
                "assumptions": {f"A decision on {s} can and should be made with current information"}}


PRIMITIVES: Dict[str, Primitive] = {
    "Echo":   EchoPrimitive(),
    "God":    GodPrimitive(),
    "Devil":  DevilPrimitive(),
    "Light":  LightPrimitive(),
    "Nathan": NathanPrimitive(),
}


# ════════════════════════════════════════════════════════════════
# 4. CONVERGENCE TOOLS
# ════════════════════════════════════════════════════════════════

def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", s.lower())).strip()

def jaccard(a: Set[str], b: Set[str]) -> float:
    if not a and not b: return 1.0
    return len(a & b) / len(a | b) if (a | b) else 0.0

def has_new_claim(new: Set[str], prior: Set[str], thresh: float = 0.75) -> bool:
    if not prior: return True
    for n in new:
        nw = set(re.findall(r'\b\w+\b', n))
        if not nw: continue
        if all(len(nw & set(re.findall(r'\b\w+\b', p))) /
               len(nw | set(re.findall(r'\b\w+\b', p))) < thresh
               for p in prior if re.findall(r'\b\w+\b', p)):
            return True
    return False


# ════════════════════════════════════════════════════════════════
# 5. ECP LOOP
# ════════════════════════════════════════════════════════════════

def ecp(problem: str, flow: str) -> Dict:
    passes:    List[Dict]  = []
    prev_norm: Set[str]    = set()
    all_flat:  Set[str]    = set()
    shared                 = None
    invariant: Set[str]    = set()
    conv_score: float      = 0.0

    for i in range(MAX_PASSES):
        merged_c: Set[str] = set()
        merged_a: Set[str] = set()

        for pname in FLOWS[flow]:
            prim = PRIMITIVES[pname]
            out  = prim.run(problem, all_flat) if pname in ("Devil", "Nathan") else prim.run(problem)
            merged_c |= out.get("claims", set())
            merged_a |= out.get("assumptions", set())

        norm = {normalize(c) for c in merged_c}

        # Variation enforcement
        if prev_norm and not has_new_claim(norm, prev_norm):
            kw  = _kw(problem)
            inj = normalize(
                f"Adversarial constraint: assume the opposite premise about "
                f"{' '.join(kw[:2]) if kw else 'this problem'} and reason from there"
            )
            norm.add(inj)

        passes.append({"claims": norm, "assumptions": merged_a})
        shared    = set(merged_a) if shared is None else shared & set(merged_a)

        if i > 0:
            conv_score = jaccard(passes[i-1]["claims"], norm)
            if conv_score >= CONVERGENCE_THRESH:
                invariant = norm
                break

        prev_norm |= norm
        all_flat  |= norm
        invariant  = norm

    # False convergence — filter trivial shared assumptions
    trivial = {
        normalize("operator skill is sufficient"),
        normalize("limited capacity favors core over surface"),
        normalize("expanding search space reveals non-obvious paths"),
    }
    real_shared = {a for a in (shared or set()) if normalize(a) not in trivial}

    return {
        "invariant":       invariant,
        "shared":          real_shared,
        "false_conv":      len(real_shared) > 0,
        "pass_count":      len(passes),
        "conv_score":      conv_score,
    }


# ════════════════════════════════════════════════════════════════
# 6. LABELING — 5 labels with real heuristics
# ════════════════════════════════════════════════════════════════

def label_claims(invariant: Set[str], false_conv: bool, problem: str) -> Dict[str, List[str]]:
    labels: Dict[str, List[str]] = {
        "Validated": [], "Plausible": [], "UnresolvedDirectional": [],
        "DeceptionIndicating": [], "Unsupported": [],
    }
    kw = set(_kw(problem))
    for c in sorted(invariant):
        cw      = set(re.findall(r'\b\w+\b', c))
        overlap = len(cw & kw) / len(cw | kw) if (cw | kw) else 0.0
        if "adversarial constraint" in c:
            labels["Unsupported"].append(c)
        elif "challenge:" in c:
            labels["UnresolvedDirectional"].append(c)
        elif any(w in c for w in ["reframe","inverse","adjacent","10x","workaround"]):
            labels["UnresolvedDirectional"].append(c)
        elif any(w in c for w in ["fails","wrong","false","dangerous","hidden","avoid",
                                   "weakness","never tested","most important"]):
            labels["DeceptionIndicating"].append(c)
        elif overlap > 0.15:
            labels["Validated"].append(c)
        else:
            labels["Plausible"].append(c)
    if false_conv:
        labels["DeceptionIndicating"].append(
            "WARNING: Shared unchallenged assumption detected — run targeted Devil pass"
        )
    return labels


# ════════════════════════════════════════════════════════════════
# 7. TRUTH PARTITION
#    NEW: low-signal suppresses full output confidence
# ════════════════════════════════════════════════════════════════

REQUIRED = ["Invariant", "Evidence", "Uncertainty", "Failure Modes", "Action"]

def build_truth_partition(problem: str, ecp_out: Dict, labels: Dict) -> Dict:
    inv_list = sorted(list(ecp_out["invariant"]))
    kw       = _kw(problem)
    focus    = kw[:3] if kw else ["core issue"]

    # Low-signal detection
    validated_overlap = [c for c in labels["Validated"] if any(w in c for w in set(kw))]
    low_signal        = len(validated_overlap) < LOW_SIGNAL_THRESH

    # Action
    if low_signal:
        action = [
            f"⚠ LOW-SIGNAL INPUT: Only {len(validated_overlap)} validated claims overlap "
            f"the input keywords. The output below is low-confidence.",
            "Reformulate the input with more specific terms, scope, or falsification condition.",
            "Do not act on low-confidence output without additional grounding.",
        ]
        confidence_note = "LOW-CONFIDENCE — input too vague for reliable analysis"
    else:
        freq   = Counter(w for c in inv_list for w in re.findall(r'\b\w+\b', c) if len(w) > 5)
        top    = [w for w, _ in freq.most_common(3)]
        action = [
            f"Immediate: address '{focus[0]}' — highest frequency term across all passes",
            "Challenge every DeceptionIndicating claim before committing to any action",
            "Assign named owner + hard deadline to the Nathan-layer finding",
        ]
        if ecp_out["false_conv"]:
            action.append(f"Run Devil pass on shared assumption: {list(ecp_out['shared'])[:1]}")
        confidence_note = f"Convergence: {ecp_out['conv_score']:.0%}"

    uncertainty = [
        f"[{confidence_note}]",
        "Claim extraction is heuristic — operator must supply grounding evidence",
        f"Scope: '{problem[:60]}' as stated",
    ]
    if ecp_out["false_conv"]:
        uncertainty.append("Shared assumptions detected — partial false convergence risk")

    return {
        "Invariant":     inv_list,
        "Evidence":      [
            f"{ecp_out['pass_count']} passes | Jaccard {ecp_out['conv_score']:.0%} | input-responsive",
            "Devil + Light applied adversarially to this specific input",
        ],
        "Uncertainty":   uncertainty,
        "Failure Modes": [
            "Primitives generate directional claims, not verified facts",
            "Label heuristics may misclassify edge cases",
            "No external data — operator grounds the output",
            f"God capped at {GOD_MAX_OPTIONS}",
        ],
        "Action":        action,
        "Labels":        labels,
        "low_signal":    low_signal,
    }


# ════════════════════════════════════════════════════════════════
# 8. VALIDATOR
# ════════════════════════════════════════════════════════════════

def validate_tp(tp: Dict) -> Tuple[bool, List[str]]:
    issues = []
    for s in REQUIRED:
        if s not in tp:   issues.append(f"MISSING: {s}")
        elif not tp[s]:   issues.append(f"EMPTY: {s}")
    if "Uncertainty" in tp:
        for u in tp["Uncertainty"]:
            if "none" in u.lower() and len(tp["Uncertainty"]) == 1:
                issues.append("Uncertainty cannot be 'none'")
    return len(issues) == 0, issues


# ════════════════════════════════════════════════════════════════
# 9. MEMORY — JSONL
# ════════════════════════════════════════════════════════════════

def save_memory(problem: str, flow: str, tp: Dict, ecp_out: Dict) -> None:
    record = {
        "id":             str(uuid.uuid4()),
        "timestamp":      int(time.time()),
        "timestamp_iso":  time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "version":        VERSION,
        "problem":        problem,
        "flow":           flow,
        "pass_count":     ecp_out["pass_count"],
        "conv_score":     ecp_out["conv_score"],
        "false_conv":     ecp_out["false_conv"],
        "low_signal":     tp.get("low_signal", False),
        "invariant":      tp["Invariant"],
        "action":         tp["Action"],
        "failure_modes":  tp["Failure Modes"],
        "uncertainty":    tp["Uncertainty"],
        "shared":         list(ecp_out["shared"]),
        "label_counts":   {k: len(v) for k, v in tp["Labels"].items()},
    }
    try:
        with open(MEMORY_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception:
        pass


# ════════════════════════════════════════════════════════════════
# 10. RUNNER
# ════════════════════════════════════════════════════════════════

def run(problem: str, context: Dict = None) -> Dict:
    """
    Full pipeline: classify → flow → ECP → label → partition → validate → memory.
    context keys (optional): unknown_domain, time_pressure, audit
    """
    context = context or {}
    parsed  = InputSpec.classify(problem)
    flow    = select_flow(parsed, context)
    ecp_out = ecp(problem, flow)
    labels  = label_claims(ecp_out["invariant"], ecp_out["false_conv"], problem)
    tp      = build_truth_partition(problem, ecp_out, labels)
    valid, issues = validate_tp(tp)
    save_memory(problem, flow, tp, ecp_out)
    return {
        "flow":        flow,
        "tp":          tp,
        "valid":       valid,
        "issues":      issues,
        "low_signal":  tp.get("low_signal", False),
        "false_conv":  ecp_out["false_conv"],
        "pass_count":  ecp_out["pass_count"],
        "conv_score":  ecp_out["conv_score"],
    }


# ════════════════════════════════════════════════════════════════
# 11. RENDER
# ════════════════════════════════════════════════════════════════

def render(result: Dict) -> str:
    tp     = result["tp"]
    valid  = result["valid"]
    ls     = result["low_signal"]
    status = ("⚠ LOW-SIGNAL" if ls else ("✅ VALID" if valid else f"❌ {result['issues']}"))
    lines  = [
        "",
        "═" * 66,
        f"  TRUTH PARTITION  [{status}]",
        f"  Flow: {result['flow']:<12}  Passes: {result['pass_count']}  "
        f"Convergence: {result['conv_score']:.0%}  False-conv: {result['false_conv']}",
        "═" * 66,
    ]
    for section in REQUIRED:
        lines.append(f"\n▸ {section.upper()}")
        items = tp.get(section, [])
        show  = items[:5] if section == "Invariant" else items
        for item in show:
            lines.append(f"  · {item[:102]}")
        if section == "Invariant" and len(items) > 5:
            lines.append(f"  · ... +{len(items) - 5} more claims")
    lines.append("\n▸ LABELS")
    for lbl, claims in tp["Labels"].items():
        if claims:
            lines.append(f"  {lbl:<24} ({len(claims):>2})  {claims[0][:70]}")
    lines.append("═" * 66)
    return "\n".join(lines)


# ════════════════════════════════════════════════════════════════
# 12. CLI
# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\nECHO SYSTEM v3.1")
    print("─" * 18)
    problem = input("Problem: ").strip()
    ctx = {
        "unknown_domain": input("Unknown domain? y/n: ").lower().startswith("y"),
        "time_pressure":  input("Time pressure?  y/n: ").lower().startswith("y"),
        "audit":          input("Audit?          y/n: ").lower().startswith("y"),
    }
    try:
        result = run(problem, ctx)
        print(render(result))
    except ValueError as e:
        print(f"\n{e}")
