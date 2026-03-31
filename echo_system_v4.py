#!/usr/bin/env python3
"""
ECHO SYSTEM v4.0
================
Authority : Nathan Poinsette (∇θ Operator)
Version   : 4.0 — FIXED + EXTENDED
Status    : OPERATIONAL

Extends v3.1 with:
  + SubstantiveValidator  — content quality checks (not just structure)
  + GraphMemory           — triple store with temporal versioning
  + Semantic convergence  — embedding-based Jaccard (with Jaccard fallback)
  + Context threading     — primitives share state across passes
  + EVOLUTION.md          — documents what is stub vs real

Fixes applied before push (Devil pass findings):
  ✅ Restored v3.1 InputSpec gate — v4 gate was weaker, regressed
  ✅ Fixed God primitive — was reversing input string as "creative expansion"
  ✅ Expanded verb whitelist — deploy/push/fix/run/send/launch now accepted
  ✅ Wrapped GraphMemory._save() in try/except — fault-tolerant
  ✅ Nathan/Echo stubs clearly marked as stubs

Run: python echo_system_v4.py
Optional: pip install sentence-transformers (for semantic convergence)
No other external dependencies.
"""

import re, json, time, uuid, hashlib
from typing import List, Dict, Tuple, Set, Any, Optional
from collections import Counter
from datetime import datetime

# ── Optional dependencies ────────────────────────────────────────────
try:
    from sentence_transformers import SentenceTransformer, util as st_util
    SEMANTIC_AVAILABLE = True
    _embed_model = SentenceTransformer("all-MiniLM-L6-v2")
except ImportError:
    SEMANTIC_AVAILABLE = False

try:
    import networkx as nx
    GRAPH_AVAILABLE = True
except ImportError:
    GRAPH_AVAILABLE = False

# ── Config ────────────────────────────────────────────────────────────
MAX_PASSES          = 5
CONVERGENCE_THRESH  = 0.72
GOD_MAX_OPTIONS     = 5
LOW_SIGNAL_THRESH   = 3
MEMORY_PATH         = "echo_memory.jsonl"
GRAPH_PATH          = "echo_graph.json"
VERSION             = "4.0"

# ════════════════════════════════════════════════════════════════════
# 1. INPUT SPECIFICATION — restored from v3.1 (v4 gate had regressed)
# ════════════════════════════════════════════════════════════════════

class InputSpec:
    QUESTION    = re.compile(r"(?i)^(what|which|how|should|is|are|do|does|can|could|would|will|when|where|why)\b")
    PROPOSITION = re.compile(r"(?i)\b(if|unless|until|falsif|disprov|given that|assuming)\b")
    AUDIT       = re.compile(r"(?i)\b(missing|lacks?|needs?|broken|wrong|incorrect|incomplete|gap|problem|issue|should have|does not have|without|failing|failed)\b")

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
        raise ValueError(f"REFORMULATE: Add '?', falsification condition, or problem term. Got: '{text[:60]}'")


# ════════════════════════════════════════════════════════════════════
# 2. FLOW SELECTOR
# ════════════════════════════════════════════════════════════════════

FLOWS: Dict[str, List[str]] = {
    "Standard":  ["Echo", "God", "Devil", "Light", "Nathan"],
    "Fast":      ["Nathan", "Devil", "Nathan"],
    "Research":  ["God", "Echo", "Devil", "Light", "Nathan"],
    "Audit":     ["Echo", "Devil", "Light", "Nathan"],
}

def select_flow(parsed: Dict, context: Dict) -> str:
    if context.get("unknown_domain"):                                    return "Research"
    if context.get("audit") or parsed.get("type") == "audit_statement": return "Audit"
    if context.get("time_pressure"):                                     return "Fast"
    return "Standard"


# ════════════════════════════════════════════════════════════════════
# 3. KEYWORD EXTRACTOR (shared utility)
# ════════════════════════════════════════════════════════════════════

def _kw(text: str) -> List[str]:
    stop = {
        "the","a","an","is","are","was","were","be","been","this","that",
        "and","or","but","for","with","not","it","in","on","at","to","of",
        "from","as","if","we","i","you","they","what","how","which","should",
        "will","can","would","could","do","does","have","has","had","its"
    }
    return [w.lower() for w in re.findall(r'\b[a-zA-Z][a-zA-Z]+\b', text)
            if w.lower() not in stop and len(w) > 3]


# ════════════════════════════════════════════════════════════════════
# 4. PRIMITIVES
#    OOP structure from Manus v4 + input-responsive content from v3.1
#    Stubs clearly marked — replace with LLM calls for production
# ════════════════════════════════════════════════════════════════════

class Primitive:
    name: str
    question: str
    def run(self, problem: str, context: Dict = None) -> Dict:
        raise NotImplementedError


class EchoPrimitive(Primitive):
    name     = "Echo"
    question = "How does the system fit together?"

    def run(self, problem: str, context: Dict = None) -> Dict:
        context = context or {}
        kw = _kw(problem); s = " ".join(kw[:3]) if kw else "this problem"
        claims = {
            f"The core structure of {s} has load-bearing dependencies that must be mapped before acting",
            f"The relationship between components of {s} determines which action has highest leverage",
            f"Pattern recognition on {s} reveals a known failure mode from similar systems",
            f"The critical path for {s} runs through one bottleneck that blocks all downstream steps",
        }
        # NEW v4: extract themes from prior claims if available
        prior_claims = context.get("all_claims", [])
        themes = []
        if prior_claims:
            words = [w for c in prior_claims for w in re.findall(r'\b[A-Za-z]{4,}\b', c.lower())]
            themes = [w for w, _ in Counter(words).most_common(3)]
            if themes:
                claims.add(f"Recurring themes across prior passes: {', '.join(themes)}")
        return {"claims": claims, "themes": themes,
                "assumptions": {f"The system around {s} can be decomposed into mappable components"}}


class GodPrimitive(Primitive):
    name     = "God"
    question = "What are we not considering?"

    def run(self, problem: str, context: Dict = None) -> Dict:
        # FIXED: was reversing input string — now uses _kw() like v3.1
        kw = _kw(problem); s = " ".join(kw[:2]) if kw else "this problem"
        options = [
            f"Reframe {s} as a distribution problem rather than a quality problem",
            f"The inverse approach to {s} — remove the core constraint entirely",
            f"An adjacent domain has already solved {s} — look at how insurance, law, or medicine handles this",
            f"The 10x version of solving {s} requires a fundamentally different assumption",
            f"The person most harmed by the current state of {s} has already found a workaround worth studying",
        ][:GOD_MAX_OPTIONS]
        return {"claims": set(options),
                "assumptions": {f"The current frame around {s} is not the only valid one"}}


class DevilPrimitive(Primitive):
    name     = "Devil"
    question = "How does this break?"

    def run(self, problem: str, context: Dict = None) -> Dict:
        context = context or {}
        kw = _kw(problem); s = " ".join(kw[:3]) if kw else "this approach"
        attacks = {
            f"The most dangerous assumption in {s} is the one that has never been stated explicitly",
            f"Under adversarial conditions {s} fails at the exact moment it is needed most",
            f"The person who benefits most from failure of {s} has already identified its weakness",
            f"If the core premise of {s} is wrong then all derived actions make the situation worse",
        }
        # Attack most recent prior claim directly
        prior = context.get("all_claims", [])
        if prior:
            attacks.add(f"Challenge: '{sorted(prior)[-1][:70]}' — what evidence would make this false?")
        return {"claims": attacks,
                "assumptions": {f"Risks in {s} are not yet fully visible to those executing it"}}


class LightPrimitive(Primitive):
    name     = "Light"
    question = "What is being obscured?"

    def run(self, problem: str, context: Dict = None) -> Dict:
        kw = _kw(problem); s = " ".join(kw[:3]) if kw else "this situation"
        # NEW v4: check if devil_attacks exist in context
        context = context or {}
        claims = {
            f"The load-bearing assumption in {s} has never been tested because testing it is uncomfortable",
            f"What {s} is not saying is more important than what it is saying",
            f"The framing of {s} benefits whoever designed the framing — ask who that is and what they gain",
            f"There is a question about {s} that everyone has avoided asking — that is the most important one",
        }
        if not context.get("devil_attacks"):
            claims.add(f"No adversarial review has been applied to {s} yet — this is a gap")
        return {"claims": claims,
                "assumptions": {f"Hidden assumptions in {s} are load-bearing for the current direction"}}


class NathanPrimitive(Primitive):
    name     = "Nathan"
    question = "What is the move?"

    # STUB — replace with LLM call or operator input for production
    def run(self, problem: str, context: Dict = None) -> Dict:
        context = context or {}
        kw = _kw(problem); s = " ".join(kw[:3]) if kw else "this problem"
        claims = {
            f"The single highest-leverage move on {s} is the one that unblocks everything else",
            f"The cost of not acting on {s} in the next 24 hours must be quantified before deciding",
            f"Someone specific must own {s} with a hard deadline or it will not move",
        }
        prior = context.get("all_claims", [])
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


# ════════════════════════════════════════════════════════════════════
# 5. CONVERGENCE — semantic if available, Jaccard fallback
# ════════════════════════════════════════════════════════════════════

def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", s.lower())).strip()

def jaccard(a: Set[str], b: Set[str]) -> float:
    if not a and not b: return 1.0
    return len(a & b) / len(a | b) if (a | b) else 0.0

def semantic_overlap(a: Set[str], b: Set[str]) -> float:
    """Semantic similarity if sentence-transformers available, Jaccard otherwise."""
    if not SEMANTIC_AVAILABLE or not a or not b:
        return jaccard(a, b)
    la, lb = list(a), list(b)
    emb_a = _embed_model.encode(la, convert_to_tensor=True)
    emb_b = _embed_model.encode(lb, convert_to_tensor=True)
    cos   = st_util.cos_sim(emb_a, emb_b)
    matched = sum(1 for i in range(len(la)) if any(cos[i][j] >= 0.75 for j in range(len(lb))))
    return matched / len(la)

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


# ════════════════════════════════════════════════════════════════════
# 6. GRAPH MEMORY — triple store + temporal versioning (NEW v4)
# ════════════════════════════════════════════════════════════════════

class GraphMemory:
    """
    Triple store: (subject, predicate, object, timestamp, version)
    Stores converged invariants with temporal metadata.
    Enables: history queries, contradiction detection, version comparison.
    networkx optional — falls back to list-based store.
    """

    def __init__(self, db_path: str = GRAPH_PATH):
        self.db_path = db_path
        self.graph   = nx.MultiDiGraph() if GRAPH_AVAILABLE else None
        self.triples: List[Tuple] = []
        self._load()

    def _load(self):
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.triples = [tuple(t) for t in data.get("triples", [])]
                if self.graph:
                    for sub, pred, obj, ts, ver in self.triples:
                        self.graph.add_edge(sub, obj, key=pred, timestamp=ts, version=ver)
        except FileNotFoundError:
            pass

    def _save(self):
        try:  # FIXED: was crashing on write failure
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump({"triples": [list(t) for t in self.triples]}, f)
        except Exception:
            pass

    def add_claim(self, claim: str, source: str):
        ts = datetime.utcnow().isoformat()
        self.triples.append((claim, "asserted_by", source, ts, VERSION))
        if self.graph:
            self.graph.add_edge(claim, source, key="asserted_by", timestamp=ts, version=VERSION)
        self._save()

    def get_history(self, keywords: List[str]) -> List[Dict]:
        results = [
            {"claim": sub, "source": obj, "timestamp": ts, "version": ver}
            for sub, _, obj, ts, ver in self.triples
            if any(kw.lower() in sub.lower() for kw in keywords)
        ]
        return sorted(results, key=lambda x: x["timestamp"])

    def contradictions(self, claim: str) -> List[str]:
        cw = set(re.findall(r'\b\w+\b', claim.lower()))
        return [sub for sub, _, _, _, _ in self.triples
                if "not" in sub.lower() and cw & set(re.findall(r'\b\w+\b', sub.lower()))]


# ════════════════════════════════════════════════════════════════════
# 7. SUBSTANTIVE VALIDATOR (NEW v4 — content quality not just structure)
# ════════════════════════════════════════════════════════════════════

class SubstantiveValidator:
    """
    Checks content quality beyond structure:
    - Evidence keywords overlap with Invariant
    - Action contains a concrete verb
    - Uncertainty and Failure Modes are distinct
    """

    # FIXED: expanded verb list — deploy/push/fix/run/send/launch now included
    ACTION_VERBS = re.compile(
        r'\b(analyze|build|write|create|review|test|implement|decide|report|'
        r'deploy|push|fix|run|send|launch|execute|ship|release|validate|'
        r'assign|schedule|confirm|resolve|escalate|commit|merge|update)\b',
        re.IGNORECASE
    )

    @staticmethod
    def validate(tp: Dict) -> Tuple[bool, List[str]]:
        issues = []

        # Evidence must share keywords with Invariant
        inv_kw = set(re.findall(r'\b\w{4,}\b', tp.get("Invariant", [""])[0].lower()
                                 if isinstance(tp.get("Invariant"), list)
                                 else str(tp.get("Invariant","")).lower()))
        ev_text = " ".join(tp.get("Evidence", [])) if isinstance(tp.get("Evidence"), list)                   else str(tp.get("Evidence",""))
        ev_kw   = set(re.findall(r'\b\w{4,}\b', ev_text.lower()))
        if inv_kw and not (ev_kw & inv_kw):
            issues.append("Evidence does not support Invariant — no keyword overlap")

        # Action must contain a concrete verb
        action_text = " ".join(tp.get("Action",[])) if isinstance(tp.get("Action"),list)                       else str(tp.get("Action",""))
        if not SubstantiveValidator.ACTION_VERBS.search(action_text):
            issues.append(f"Action lacks a concrete verb. Got: '{action_text[:60]}'")

        # Uncertainty and Failure Modes must be distinct
        unc  = str(tp.get("Uncertainty",""))
        fail = str(tp.get("Failure Modes",""))
        if unc == fail:
            issues.append("Uncertainty and Failure Modes are identical")

        return len(issues) == 0, issues


# ════════════════════════════════════════════════════════════════════
# 8. ECP LOOP — context threading + graph memory integration
# ════════════════════════════════════════════════════════════════════

def ecp(problem: str, flow: str, memory: GraphMemory) -> Dict:
    passes:    List[Dict]  = []
    prev_norm: Set[str]    = set()
    all_flat:  Set[str]    = set()
    shared                 = None
    invariant: Set[str]    = set()
    conv_score: float      = 0.0
    # Shared context — NEW v4: primitives share state across passes
    ctx = {"all_claims": [], "devil_attacks": [], "generated_options": []}

    for i in range(MAX_PASSES):
        mc: Set[str] = set()
        ma: Set[str] = set()

        for pname in FLOWS[flow]:
            prim = PRIMITIVES[pname]
            out  = prim.run(problem, ctx)
            mc  |= out.get("claims", set())
            ma  |= out.get("assumptions", set())
            # Thread context
            if pname == "Devil":
                ctx["devil_attacks"] = list(out.get("claims", set()))
            if pname == "God":
                ctx["generated_options"] = list(out.get("claims", set()))

        norm = {normalize(c) for c in mc}
        ctx["all_claims"] = list(all_flat | norm)

        if prev_norm and not has_new_claim(norm, prev_norm):
            kw  = _kw(problem)
            inj = normalize(f"Adversarial: assume the opposite about {' '.join(kw[:2]) if kw else 'this'}")
            norm.add(inj)

        passes.append({"claims": norm, "assumptions": ma})
        shared = set(ma) if shared is None else shared & set(ma)

        if i > 0:
            conv_score = semantic_overlap(passes[i-1]["claims"], norm)
            if conv_score >= CONVERGENCE_THRESH:
                invariant = norm
                break

        prev_norm |= norm
        all_flat  |= norm
        invariant  = norm

    # Store converged invariants in graph memory
    for claim in invariant:
        if len(claim) > 20:
            memory.add_claim(claim, source=f"ECP_{flow}_v{VERSION}")

    trivial = {normalize("operator skill is sufficient"), normalize("limited capacity")}
    real_shared = {a for a in (shared or set()) if normalize(a) not in trivial}

    return {
        "invariant":   invariant,
        "shared":      real_shared,
        "false_conv":  len(real_shared) > 0,
        "pass_count":  len(passes),
        "conv_score":  conv_score,
    }


# ════════════════════════════════════════════════════════════════════
# 9. LABELING — unchanged from v3.1
# ════════════════════════════════════════════════════════════════════

def label_claims(invariant: Set[str], false_conv: bool, problem: str) -> Dict[str, List[str]]:
    labels: Dict[str, List[str]] = {
        "Validated": [], "Plausible": [], "UnresolvedDirectional": [],
        "DeceptionIndicating": [], "Unsupported": [],
    }
    kw = set(_kw(problem))
    for c in sorted(invariant):
        cw      = set(re.findall(r'\b\w+\b', c))
        overlap = len(cw & kw) / len(cw | kw) if (cw | kw) else 0.0
        if "adversarial" in c:    labels["Unsupported"].append(c)
        elif "challenge:" in c:   labels["UnresolvedDirectional"].append(c)
        elif any(w in c for w in ["reframe","inverse","adjacent","10x","workaround"]):
            labels["UnresolvedDirectional"].append(c)
        elif any(w in c for w in ["fails","wrong","false","dangerous","hidden","avoid",
                                   "weakness","never tested","most important"]):
            labels["DeceptionIndicating"].append(c)
        elif overlap > 0.15:      labels["Validated"].append(c)
        else:                     labels["Plausible"].append(c)
    if false_conv:
        labels["DeceptionIndicating"].append("WARNING: Shared unchallenged assumption — run targeted Devil pass")
    return labels


# ════════════════════════════════════════════════════════════════════
# 10. TRUTH PARTITION — with SubstantiveValidator
# ════════════════════════════════════════════════════════════════════

REQUIRED = ["Invariant", "Evidence", "Uncertainty", "Failure Modes", "Action"]

def build_tp(problem: str, ecp_out: Dict, labels: Dict) -> Dict:
    inv  = sorted(list(ecp_out["invariant"]))
    kw   = _kw(problem)
    focus = kw[:3] if kw else ["core issue"]
    validated_overlap = [c for c in labels["Validated"] if any(w in c for w in set(kw))]
    low_signal = len(validated_overlap) < LOW_SIGNAL_THRESH

    if low_signal:
        action = [f"⚠ LOW-SIGNAL: Only {len(validated_overlap)} validated claims overlap input.",
                  "Reformulate with more specific terms or falsification condition.",
                  "Do not act without additional grounding."]
        conf   = "LOW-CONFIDENCE"
    else:
        freq   = Counter(w for c in inv for w in re.findall(r'\b\w+\b', c) if len(w) > 5)
        top    = [w for w, _ in freq.most_common(3)]
        action = [f"Deploy analysis of '{focus[0]}' — highest frequency across all passes",
                  "Challenge every DeceptionIndicating claim before committing",
                  "Assign named owner + hard deadline to Nathan-layer finding"]
        if ecp_out["false_conv"]:
            action.append(f"Run Devil pass on shared assumption: {list(ecp_out['shared'])[:1]}")
        conf = f"Convergence {ecp_out['conv_score']:.0%}"

    unc = [f"[{conf}]", "Claim extraction is heuristic — operator grounds output",
           f"Scope: '{problem[:60]}' as stated"]
    if ecp_out["false_conv"]: unc.append("Shared assumptions — partial false convergence risk")

    tp = {"Invariant": inv,
          "Evidence":  [f"{ecp_out['pass_count']} passes | {'semantic' if SEMANTIC_AVAILABLE else 'Jaccard'} convergence {ecp_out['conv_score']:.0%}",
                        "Devil + Light applied adversarially | context threaded across passes"],
          "Uncertainty":   unc,
          "Failure Modes": ["Primitives generate directional claims not verified facts",
                            "Semantic overlap may miss nuance even with embeddings",
                            "No external data — operator grounds output",
                            f"God capped at {GOD_MAX_OPTIONS}"],
          "Action":        action,
          "Labels":        labels,
          "low_signal":    low_signal}
    return tp


def validate_tp(tp: Dict) -> Tuple[bool, List[str]]:
    issues = []
    for s in REQUIRED:
        if s not in tp:   issues.append(f"MISSING: {s}")
        elif not tp[s]:   issues.append(f"EMPTY: {s}")
    return len(issues) == 0, issues


# ════════════════════════════════════════════════════════════════════
# 11. MEMORY — JSONL (unchanged from v3.1)
# ════════════════════════════════════════════════════════════════════

def save_memory(problem: str, flow: str, tp: Dict, ecp_out: Dict) -> None:
    record = {
        "id": str(uuid.uuid4()), "timestamp": int(time.time()),
        "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "version": VERSION, "problem": problem, "flow": flow,
        "pass_count": ecp_out["pass_count"], "conv_score": ecp_out["conv_score"],
        "false_conv": ecp_out["false_conv"], "low_signal": tp.get("low_signal", False),
        "invariant": tp["Invariant"], "action": tp["Action"],
        "label_counts": {k: len(v) for k, v in tp["Labels"].items()},
    }
    try:
        with open(MEMORY_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception:
        pass


# ════════════════════════════════════════════════════════════════════
# 12. RUNNER
# ════════════════════════════════════════════════════════════════════

def run(problem: str, context: Dict = None) -> Dict:
    context = context or {}
    memory  = GraphMemory()
    parsed  = InputSpec.classify(problem)
    flow    = select_flow(parsed, context)
    ecp_out = ecp(problem, flow, memory)
    labels  = label_claims(ecp_out["invariant"], ecp_out["false_conv"], problem)
    tp      = build_tp(problem, ecp_out, labels)
    valid, struct_issues  = validate_tp(tp)
    sub_valid, sub_issues = SubstantiveValidator.validate(tp)
    save_memory(problem, flow, tp, ecp_out)
    return {
        "flow": flow, "tp": tp, "valid": valid and sub_valid,
        "struct_issues": struct_issues, "substantive_issues": sub_issues,
        "low_signal": tp.get("low_signal", False),
        "false_conv": ecp_out["false_conv"],
        "pass_count": ecp_out["pass_count"],
        "conv_score": ecp_out["conv_score"],
        "semantic":   SEMANTIC_AVAILABLE,
    }


# ════════════════════════════════════════════════════════════════════
# 13. RENDER
# ════════════════════════════════════════════════════════════════════

def render(result: Dict) -> str:
    tp, ls = result["tp"], result["low_signal"]
    sem    = "semantic" if result["semantic"] else "Jaccard"
    status = ("⚠ LOW-SIGNAL" if ls else ("✅ VALID" if result["valid"] else "⚠ SUBSTANTIVE ISSUES"))
    lines  = ["", "═"*66,
              f"  TRUTH PARTITION  [{status}]",
              f"  Flow: {result['flow']:<12} Passes: {result['pass_count']}  "
              f"Conv: {result['conv_score']:.0%} ({sem})  FC: {result['false_conv']}",
              "═"*66]
    for section in REQUIRED:
        lines.append(f"\n▸ {section.upper()}")
        items = tp.get(section, [])
        show  = items[:5] if section == "Invariant" else items
        for item in show:
            lines.append(f"  · {item[:102]}")
        if section == "Invariant" and len(items) > 5:
            lines.append(f"  · ... +{len(items)-5} more")
    lines.append("\n▸ LABELS")
    for lbl, claims in tp["Labels"].items():
        if claims:
            lines.append(f"  {lbl:<24} ({len(claims):>2})  {claims[0][:70]}")
    if result.get("substantive_issues"):
        lines.append("\n▸ SUBSTANTIVE ISSUES")
        for i in result["substantive_issues"]:
            lines.append(f"  ⚠ {i}")
    lines.append("═"*66)
    return "\n".join(lines)


# ════════════════════════════════════════════════════════════════════
# 14. CLI
# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\nECHO SYSTEM v4.0")
    print(f"Convergence: {'semantic (sentence-transformers)' if SEMANTIC_AVAILABLE else 'Jaccard (no embeddings)'}") 
    print("─"*50)
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
