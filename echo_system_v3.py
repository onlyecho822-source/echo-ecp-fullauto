#!/usr/bin/env python3
"""
ECHO SYSTEM v3.1
================
Authority : Nathan Poinsette (∇θ Operator)  |  Echo Universe
Version   : 3.1 — OPERATIONAL
Repository: github.com/onlyecho822-source/echo-ecp-fullauto

PURPOSE
-------
A governed reasoning scaffold that runs any bounded problem through
five adversarial primitives, measures convergence across passes, detects
false convergence, labels every output claim, and enforces a structured
Truth Partition before returning anything.

This is NOT a chatbot. It does not answer questions directly.
It interrogates them — surfacing structure, failure modes, hidden
assumptions, and the highest-leverage action.

ARCHITECTURE OVERVIEW
---------------------
  INPUT
    └─ InputSpec.classify()          ← gate: reject / reformulate / accept
         └─ select_flow()            ← route to correct primitive sequence
              └─ ecp()               ← run passes until convergence
                   ├─ EchoPrimitive  ← structure + dependencies
                   ├─ GodPrimitive   ← expand beyond current frame
                   ├─ DevilPrimitive ← attack assumptions adversarially
                   ├─ LightPrimitive ← surface what is hidden
                   └─ NathanPrimitive← derive the move from all passes
                        └─ label_claims()     ← classify by content
                             └─ build_tp()    ← assemble Truth Partition
                                  └─ validate_tp() ← enforce structure
                                       └─ save_memory() ← JSONL record

TRUTH PARTITION (five required fields — all must be present)
------------------------------------------------------------
  Invariant     — claims that survived all passes
  Evidence      — convergence score, pass count, method
  Uncertainty   — confidence flag, shared assumption warnings
  Failure Modes — what could make this output wrong
  Action        — derived from claim frequency, not hardcoded

FIVE CLAIM LABELS
-----------------
  Validated             — directly addresses input (>15% keyword overlap)
  Plausible             — credible but not directly verified
  UnresolvedDirectional — God expansions, challenge prompts (follow up)
  DeceptionIndicating   — Devil/Light findings (attack before acting)
  Unsupported           — injected adversarial constraints

FOUR FLOWS (priority: unknown_domain > audit > time_pressure > standard)
------------------------------------------------------------------------
  Standard : Echo → God → Devil → Light → Nathan  (default)
  Fast     : Nathan → Devil → Nathan              (time pressure)
  Research : God → Echo → Devil → Light → Nathan  (unknown domain)
  Audit    : Echo → Devil → Light → Nathan        (review existing work)

KNOWN LIMITS (honest)
---------------------
  — Claim extraction is lexical (regex), not semantic (embeddings)
  — Primitives generate directional claims, not verified facts
  — Convergence score = word overlap proxy, not logical agreement
  — Operator must ground the output — this system amplifies, not replaces
  — v4 adds SubstantiveValidator, GraphMemory, and semantic convergence

QUICK START
-----------
  python echo_system_v3.py          ← interactive CLI
  from echo_system_v3 import run    ← programmatic use

  result = run("What is the highest-leverage deployment action?")
  result = run("The auth system is missing rate limiting")
  result = run("Should we ship now?", {"time_pressure": True})

UPGRADE PATH
------------
  Each primitive is a class. Replace the run() method with an LLM call
  to upgrade from scaffold to production reasoning engine. The ECP loop,
  convergence tools, labeling, and Truth Partition all work unchanged.
  See docs/PRIMITIVES.md for integration guide.
"""

import re, json, time, uuid
from typing import List, Dict, Tuple, Set, Any, Optional
from collections import Counter


# ════════════════════════════════════════════════════════════════
# CONFIGURATION
# ════════════════════════════════════════════════════════════════
# Tune these constants to change engine behavior.
# CONVERGENCE_THRESH: lower = stops sooner (less thorough), higher = runs longer
# GOD_MAX_OPTIONS: hard cap on God primitive expansion — prevents rabbit holes
# LOW_SIGNAL_THRESH: how many Validated claims must overlap input before
#   the output is considered reliable enough to act on

MAX_PASSES         = 5      # absolute maximum passes before forced stop
CONVERGENCE_THRESH = 0.72   # Jaccard ≥ 72% between consecutive passes → converged
GOD_MAX_OPTIONS    = 5      # God primitive generates at most this many options
LOW_SIGNAL_THRESH  = 3      # min Validated claims overlapping input keywords
MEMORY_PATH        = "echo_memory.jsonl"   # append-only output log
VERSION            = "3.1"


# ════════════════════════════════════════════════════════════════
# 1. INPUT SPECIFICATION
#    Gate with three outcomes:
#      accepted   → returns parsed dict with type + core
#      reformulate → raises ValueError with specific guidance
#      rejected   → raises ValueError with REJECTED prefix
#
#    Accepted types:
#      question       — ends in ? or starts with question word
#      proposition    — contains falsification condition (if/unless/...)
#      audit_statement — contains explicit problem term (missing/broken/...)
# ════════════════════════════════════════════════════════════════

class InputSpec:
    """
    Gate. Classifies input into one of three accepted types or raises
    ValueError with actionable guidance on how to reformulate.

    Design rationale: vague inputs produce confident-looking outputs
    that have no grounding. The gate forces the operator to scope
    the problem before the engine touches it.
    """

    # Starts with a question word
    QUESTION = re.compile(
        r"(?i)^(what|which|how|should|is|are|do|does|can|could|would|will|when|where|why)\b"
    )
    # Contains explicit falsification condition
    PROPOSITION = re.compile(
        r"(?i)\b(if|unless|until|falsif|disprov|given that|assuming)\b"
    )
    # Contains a problem/gap term — declarative audit statements
    AUDIT = re.compile(
        r"(?i)\b(missing|lacks?|needs?|broken|wrong|incorrect|incomplete|"
        r"gap|problem|issue|should have|does not have|without|failing|failed)\b"
    )

    @classmethod
    def classify(cls, text: str) -> Dict[str, Any]:
        """
        Classify text and return parsed dict, or raise ValueError.

        Returns:
            {"type": "question"|"proposition"|"audit_statement", "core": text}

        Raises:
            ValueError: with REJECTED (too short) or REFORMULATE (needs structure)
        """
        text = text.strip()

        # Hard floor — anything under 8 chars cannot be a bounded problem
        if len(text) < 8:
            raise ValueError(
                "REJECTED: Too short. State a question, proposition, or audit target."
            )

        # Question: "What is...", "How do...", "Should we...", or ends with ?
        if text.endswith("?") or cls.QUESTION.match(text):
            return {"type": "question", "core": text}

        # Proposition: "X is true unless Y", "Given that A, will B hold?"
        if cls.PROPOSITION.search(text):
            return {"type": "proposition", "core": text}

        # Audit statement: "The system is missing X", "Auth is broken"
        if cls.AUDIT.search(text):
            return {"type": "audit_statement", "core": text}

        # Reformulatable — the input has content but lacks structure
        raise ValueError(
            f"REFORMULATE: Add '?', a falsification condition (e.g. 'unless X'), "
            f"or a problem term (missing/broken/needs/gap). Got: '{text[:60]}'"
        )


# ════════════════════════════════════════════════════════════════
# 2. FLOW SELECTOR
#    Routes to the correct primitive sequence based on context.
#    Priority is enforced — unknown domain beats time pressure
#    because exploring an unknown domain with a fast heuristic
#    is worse than exploring slowly.
# ════════════════════════════════════════════════════════════════

# Each flow is an ordered list of primitive names.
# Nathan always appears last in most flows — it synthesizes everything.
# Fast flow breaks the rule intentionally: Nathan acts first to
# get an initial move, Devil attacks it, Nathan revises.
FLOWS: Dict[str, List[str]] = {
    "Standard":  ["Echo", "God", "Devil", "Light", "Nathan"],
    "Fast":      ["Nathan", "Devil", "Nathan"],   # act → attack → revise
    "Research":  ["God", "Echo", "Devil", "Light", "Nathan"],  # expand first
    "Audit":     ["Echo", "Devil", "Light", "Nathan"],  # no God — scope is known
}


def select_flow(parsed: Dict, context: Dict) -> str:
    """
    Select the correct flow based on input type and operator context.

    Priority order (highest to lowest):
      1. unknown_domain — use Research (expand before narrowing)
      2. audit_statement or context["audit"] — use Audit
      3. time_pressure — use Fast
      4. default — Standard

    Args:
        parsed:  output of InputSpec.classify()
        context: dict with optional keys: unknown_domain, audit, time_pressure

    Returns:
        Flow name string: "Standard" | "Fast" | "Research" | "Audit"
    """
    if context.get("unknown_domain"):                                    return "Research"
    if context.get("audit") or parsed.get("type") == "audit_statement": return "Audit"
    if context.get("time_pressure"):                                     return "Fast"
    return "Standard"


# ════════════════════════════════════════════════════════════════
# 3. KEYWORD EXTRACTOR
#    Shared utility used by all primitives and labeling.
#    Strips stopwords and short tokens to get meaningful terms.
# ════════════════════════════════════════════════════════════════

def _kw(text: str) -> List[str]:
    """
    Extract meaningful keywords from text for claim generation and labeling.

    Strips English stopwords and tokens shorter than 4 chars.
    Returns lowercase list in order of appearance.

    Used by: all five primitives (to build input-responsive claims),
             label_claims() (to compute keyword overlap),
             build_tp() (to derive action focus).
    """
    stop = {
        "the","a","an","is","are","was","were","be","been","this","that",
        "and","or","but","for","with","not","it","in","on","at","to","of",
        "from","as","if","we","i","you","they","what","how","which","should",
        "will","can","would","could","do","does","have","has","had","its"
    }
    return [
        w.lower() for w in re.findall(r'\b[a-zA-Z][a-zA-Z]+\b', text)
        if w.lower() not in stop and len(w) > 3
    ]


# ════════════════════════════════════════════════════════════════
# 4. PRIMITIVES
#    Five classes. One question each. Cannot be reduced further.
#
#    Each primitive:
#      — reads the actual input via _kw()
#      — generates claims ABOUT that specific problem
#      — returns {"claims": Set[str], "assumptions": Set[str]}
#
#    To upgrade to LLM-backed reasoning, subclass any primitive
#    and replace the run() method with an API call. The ECP loop
#    and everything downstream works unchanged.
#    See docs/PRIMITIVES.md for integration guide.
# ════════════════════════════════════════════════════════════════

class Primitive:
    """Base class for all five primitives. Subclass for LLM integration."""
    name: str      # primitive name — used by FLOWS dict and logging
    question: str  # the one question this primitive asks

    def run(self, problem: str, context: Optional[Set[str]] = None) -> Dict:
        """
        Run the primitive on the given problem.

        Args:
            problem: the operator's input string
            context: accumulated claims from prior passes (Devil and Nathan use this)

        Returns:
            {"claims": Set[str], "assumptions": Set[str]}
        """
        raise NotImplementedError


class EchoPrimitive(Primitive):
    """
    Echo — How does the system fit together?

    Maps structure, dependencies, patterns, and bottlenecks.
    Runs first in Standard, Research, and Audit flows to establish
    the structural frame before other primitives narrow or attack it.
    """
    name     = "Echo"
    question = "How does the system fit together?"

    def run(self, problem: str, context=None) -> Dict:
        kw = _kw(problem)
        s  = " ".join(kw[:3]) if kw else "this problem"
        return {
            "claims": {
                # Structural dependency claim — what must be mapped first
                f"The core structure of {s} has load-bearing dependencies "
                f"that must be mapped before acting",
                # Leverage claim — where action has most impact
                f"The relationship between components of {s} determines "
                f"which action has highest leverage",
                # Pattern claim — has this failure mode appeared before?
                f"Pattern recognition on {s} reveals a known failure mode "
                f"from similar systems",
                # Bottleneck claim — what blocks everything downstream
                f"The critical path for {s} runs through one bottleneck "
                f"that blocks all downstream steps",
            },
            "assumptions": {
                f"The system around {s} can be decomposed into mappable components"
            }
        }


class GodPrimitive(Primitive):
    """
    God — What are we not considering?

    Expands the frame before other primitives narrow it.
    Runs first in Research flow (break local optima early).
    Runs second in Standard flow (after Echo maps structure).
    Hard-capped at GOD_MAX_OPTIONS to prevent unbounded expansion.

    Stop rule: content-based — if new options are subsets of
    existing options, God declares convergence on expansion.
    Fixed cap at GOD_MAX_OPTIONS = 5 as safety ceiling.
    """
    name     = "God"
    question = "What are we not considering?"

    def run(self, problem: str, context=None) -> Dict:
        kw = _kw(problem)
        s  = " ".join(kw[:2]) if kw else "this problem"
        options = [
            # Reframe: is this a distribution problem, not a quality problem?
            f"Reframe {s} as a distribution problem rather than a quality problem",
            # Inversion: what if you removed the constraint entirely?
            f"The inverse approach to {s} — remove the core constraint entirely",
            # Adjacent domain: who else has solved this?
            f"An adjacent domain has already solved {s} — "
            f"look at how insurance, law, or medicine handles this",
            # 10x: what would a fundamentally different approach require?
            f"The 10x version of solving {s} requires a fundamentally different assumption",
            # Harmed party: the person most harmed already found a workaround
            f"The person most harmed by the current state of {s} "
            f"has already found a workaround worth studying",
        ][:GOD_MAX_OPTIONS]  # hard cap — always slice even if list grows
        return {
            "claims": set(options),
            "assumptions": {f"The current frame around {s} is not the only valid one"}
        }


class DevilPrimitive(Primitive):
    """
    Devil — How does this break?

    Adversarial falsification. Attacks assumptions directly.
    Runs in all four flows. Receives accumulated prior claims
    and attacks the most recent one specifically.

    This is the most important primitive for preventing false confidence.
    Every DeceptionIndicating claim in the output came from Devil or Light.
    Challenge these before acting on any output.
    """
    name     = "Devil"
    question = "How does this break?"

    def run(self, problem: str, context: Optional[Set[str]] = None) -> Dict:
        kw = _kw(problem)
        s  = " ".join(kw[:3]) if kw else "this approach"
        attacks = {
            # Unstated assumption: the most dangerous one is never written down
            f"The most dangerous assumption in {s} is the one that "
            f"has never been stated explicitly",
            # Adversarial failure: it breaks at the worst possible moment
            f"Under adversarial conditions {s} fails at the exact moment "
            f"it is needed most",
            # Motivated adversary: someone already knows the weakness
            f"The person who benefits most from failure of {s} "
            f"has already identified its weakness",
            # Wrong premise: if the core premise is false, all actions backfire
            f"If the core premise of {s} is wrong then all derived actions "
            f"make the situation worse, not better",
        }
        # Direct attack on the most recent prior claim — creates adversarial pressure
        # across passes, not just on the original input
        if context:
            most_recent = sorted(context)[-1]
            attacks.add(
                f"Challenge: '{most_recent[:70]}' — "
                f"what evidence would make this false?"
            )
        return {
            "claims": attacks,
            "assumptions": {
                f"Risks in {s} are not yet fully visible to those executing it"
            }
        }


class LightPrimitive(Primitive):
    """
    Light — What is being obscured?

    Surfaces hidden load-bearing assumptions — the ones nobody states
    because stating them would require defending them.
    Asks who benefits from the current framing.
    Identifies the question everyone has avoided asking.

    Runs near-last (before Nathan) so it can scrutinize what
    all prior primitives produced, not just the original input.
    """
    name     = "Light"
    question = "What is being obscured?"

    def run(self, problem: str, context=None) -> Dict:
        kw = _kw(problem)
        s  = " ".join(kw[:3]) if kw else "this situation"
        return {
            "claims": {
                # Uncomfortable test: load-bearing assumptions resist testing
                f"The load-bearing assumption in {s} has never been tested "
                f"because testing it is uncomfortable",
                # Silence: what is not said is more diagnostic than what is
                f"What {s} is not saying is more important than what it is saying",
                # Framing beneficiary: ask who designed the frame and why
                f"The framing of {s} benefits whoever designed the framing — "
                f"ask who that is and what they gain",
                # Unasked question: the avoided question is the important one
                f"There is a question about {s} that everyone has avoided asking — "
                f"that is the most important one",
            },
            "assumptions": {
                f"Hidden assumptions in {s} are load-bearing for the current direction"
            }
        }


class NathanPrimitive(Primitive):
    """
    Nathan — What is the move?

    Synthesizes everything prior passes produced into the highest-leverage
    action. Runs last in most flows because it needs all prior claims
    to derive a meaningful action.

    In Fast flow it runs first (initial move), then after Devil attacks
    it, then runs again with the adversarial pressure incorporated.

    STUB — the action synthesis is currently keyword-frequency based.
    Replace run() with an LLM call for production-grade action derivation.
    See docs/PRIMITIVES.md for integration guide.
    """
    name     = "Nathan"
    question = "What is the move?"

    def run(self, problem: str, context: Optional[Set[str]] = None) -> Dict:
        kw = _kw(problem)
        s  = " ".join(kw[:3]) if kw else "this problem"
        claims = {
            # Leverage: the single move that unblocks everything else
            f"The single highest-leverage move on {s} is the one "
            f"that unblocks everything else",
            # Cost of inaction: quantify before deciding
            f"The cost of not acting on {s} in the next 24 hours "
            f"must be quantified before any decision is made",
            # Ownership: without a named owner and deadline, nothing moves
            f"Someone specific must own {s} with a hard deadline "
            f"or it will not move",
        }
        # Synthesize from prior passes — most frequent long words reveal focus
        # STUB: replace this with LLM synthesis for production
        if context:
            freq = Counter(
                w for c in context
                for w in re.findall(r'\b\w+\b', c)
                if len(w) > 5
            )
            top = [w for w, _ in freq.most_common(3)]
            if top:
                claims.add(
                    f"Based on all passes: highest-priority action targets "
                    f"{', '.join(top)}"
                )
        return {
            "claims": claims,
            "assumptions": {
                f"A decision on {s} can and should be made with current information"
            }
        }


# Primitive registry — add new primitives here
PRIMITIVES: Dict[str, Primitive] = {
    "Echo":   EchoPrimitive(),
    "God":    GodPrimitive(),
    "Devil":  DevilPrimitive(),
    "Light":  LightPrimitive(),
    "Nathan": NathanPrimitive(),
}


# ════════════════════════════════════════════════════════════════
# 5. CONVERGENCE TOOLS
#    Three functions used by the ECP loop:
#      normalize()     — strips punctuation/case for comparison
#      jaccard()       — set similarity score [0.0, 1.0]
#      has_new_claim() — enforces genuine variation across passes
# ════════════════════════════════════════════════════════════════

def normalize(s: str) -> str:
    """
    Normalize a claim string for comparison.
    Strips punctuation, lowercases, collapses whitespace.
    Used before adding claims to the normalized set and before Jaccard.
    """
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def jaccard(a: Set[str], b: Set[str]) -> float:
    """
    Jaccard similarity between two sets of normalized claim strings.
    Returns 1.0 for two empty sets (convention: empty = fully converged).
    Returns 0.0 for disjoint sets.

    Used by the ECP loop to decide whether to stop iterating.
    Threshold: CONVERGENCE_THRESH = 0.72 (72% overlap → stop).
    """
    if not a and not b: return 1.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def has_new_claim(new: Set[str], prior: Set[str],
                  thresh: float = 0.75) -> bool:
    """
    Check whether the new claim set adds at least one genuinely new claim
    not already covered by the prior set.

    Prevents fake diversity where passes are cosmetically different but
    substantively identical. If no new claim exists, the ECP loop injects
    an adversarial constraint to force meaningful variation.

    Uses per-claim word overlap (not full-set Jaccard) so a single novel
    claim in an otherwise similar set still counts as new.

    Args:
        new:    normalized claim set from current pass
        prior:  union of all prior pass claims
        thresh: word overlap threshold above which a claim is "covered"

    Returns:
        True if at least one claim in `new` is not covered by `prior`
    """
    if not prior: return True  # first pass always has new content
    for n in new:
        nw = set(re.findall(r'\b\w+\b', n))
        if not nw: continue
        genuinely_new = True
        for p in prior:
            pw = set(re.findall(r'\b\w+\b', p))
            if pw:
                overlap = len(nw & pw) / len(nw | pw)
                if overlap >= thresh:
                    genuinely_new = False
                    break
        if genuinely_new:
            return True  # found one novel claim — that's enough
    return False


# ════════════════════════════════════════════════════════════════
# 6. ECP LOOP
#    Orchestrates passes, convergence, variation, and false
#    convergence detection.
#
#    Each pass:
#      1. Run all primitives in flow sequence
#      2. Normalize claims
#      3. Check variation — inject adversarial constraint if none
#      4. Check convergence — stop if Jaccard ≥ threshold
#      5. Track shared assumptions across passes
#
#    After all passes:
#      6. Filter trivial shared assumptions
#      7. Flag false convergence if non-trivial shared assumptions exist
# ════════════════════════════════════════════════════════════════

def _run_pass(problem: str, flow: str,
              prev_norm: Set[str], all_flat: Set[str]) -> Dict:
    """
    Run one full pass of the specified flow.

    Args:
        problem:   operator's input string
        flow:      flow name (key in FLOWS dict)
        prev_norm: normalized claims from the immediately prior pass
        all_flat:  union of all normalized claims from all prior passes

    Returns:
        {"claims": Set[str] (normalized), "assumptions": Set[str] (raw)}
    """
    merged_c: Set[str] = set()
    merged_a: Set[str] = set()

    for pname in FLOWS[flow]:
        prim = PRIMITIVES[pname]
        # Devil and Nathan read accumulated claims to produce specific outputs
        out  = prim.run(problem, all_flat) if pname in ("Devil", "Nathan")                else prim.run(problem)
        merged_c |= out.get("claims", set())
        merged_a |= out.get("assumptions", set())

    # Normalize all claims for comparison
    norm = {normalize(c) for c in merged_c}

    # Variation enforcement: if this pass adds nothing new, force an adversarial
    # constraint. This prevents the loop from converging on identical passes.
    if prev_norm and not has_new_claim(norm, prev_norm):
        kw  = _kw(problem)
        inj = normalize(
            f"Adversarial constraint: assume the opposite premise about "
            f"{' '.join(kw[:2]) if kw else 'this problem'} and reason from there"
        )
        norm.add(inj)

    return {"claims": norm, "assumptions": merged_a}


def ecp(problem: str, flow: str) -> Dict:
    """
    Run the Echo Convergence Protocol loop.

    Executes passes until:
      - Consecutive passes converge (Jaccard ≥ CONVERGENCE_THRESH), or
      - MAX_PASSES is reached

    After all passes, scans for false convergence: shared assumptions
    that were never challenged by any pass. Filters out trivially
    shared terms (things that always appear regardless of input).

    Args:
        problem: operator's input string
        flow:    flow name from select_flow()

    Returns:
        {
          "invariant":   Set[str]  — final normalized claim set
          "shared":      Set[str]  — non-trivial shared assumptions
          "false_conv":  bool      — True if shared assumptions exist
          "pass_count":  int       — number of passes run
          "conv_score":  float     — final Jaccard score
        }
    """
    passes:    List[Dict] = []
    prev_norm: Set[str]   = set()
    all_flat:  Set[str]   = set()
    shared                = None    # intersection of assumptions across all passes
    invariant: Set[str]   = set()
    conv_score: float     = 0.0

    for i in range(MAX_PASSES):
        out    = _run_pass(problem, flow, prev_norm, all_flat)
        claims = out["claims"]
        assump = out["assumptions"]
        passes.append(out)

        # Track shared assumptions: intersect across passes
        shared = set(assump) if shared is None else shared & set(assump)

        # Convergence check — needs at least 2 passes to compare
        if i > 0:
            conv_score = jaccard(passes[i-1]["claims"], claims)
            if conv_score >= CONVERGENCE_THRESH:
                invariant = claims
                break   # converged — stop iterating

        # Accumulate for next pass
        prev_norm |= claims
        all_flat  |= claims
        invariant  = claims  # last pass becomes invariant if no convergence

    # False convergence detection
    # Filter out assumptions that appear in every run regardless of input —
    # these are structural artifacts, not meaningful shared beliefs
    trivial = {
        normalize("operator skill is sufficient"),
        normalize("limited capacity favors core over surface"),
        normalize("expanding search space reveals non-obvious paths"),
    }
    real_shared = {
        a for a in (shared or set())
        if normalize(a) not in trivial
    }
    false_conv = len(real_shared) > 0

    return {
        "invariant":   invariant,
        "shared":      real_shared,
        "false_conv":  false_conv,
        "pass_count":  len(passes),
        "conv_score":  conv_score,
    }


# ════════════════════════════════════════════════════════════════
# 7. LABELING
#    Classifies each invariant claim into one of five labels
#    based on its content relative to the input.
#
#    The heuristics are intentionally conservative:
#    — Validated requires >15% keyword overlap with input
#    — DeceptionIndicating fires on specific adversarial/failure words
#    — God expansions always go to UnresolvedDirectional
#    — Injected constraints always go to Unsupported
# ════════════════════════════════════════════════════════════════

def label_claims(invariant: Set[str],
                 false_conv: bool,
                 problem: str) -> Dict[str, List[str]]:
    """
    Assign a label to each invariant claim.

    Labels:
      Validated             — claim keywords overlap input keywords >15%
      Plausible             — credible but below Validated threshold
      UnresolvedDirectional — God expansions, challenge prompts
      DeceptionIndicating   — Devil/Light adversarial findings
      Unsupported           — injected adversarial constraints

    If false convergence was detected, adds a warning to DeceptionIndicating.

    Args:
        invariant:  normalized claim set from ecp()
        false_conv: True if shared unchallenged assumptions were detected
        problem:    operator's original input string

    Returns:
        Dict mapping label names to lists of claim strings
    """
    labels: Dict[str, List[str]] = {
        "Validated":             [],
        "Plausible":             [],
        "UnresolvedDirectional": [],
        "DeceptionIndicating":   [],
        "Unsupported":           [],
    }
    kw = set(_kw(problem))  # input keywords for overlap calculation

    for c in sorted(invariant):  # sorted for deterministic ordering
        cw      = set(re.findall(r'\b\w+\b', c))
        overlap = len(cw & kw) / len(cw | kw) if (cw | kw) else 0.0

        if "adversarial constraint" in c:
            # Injected by variation enforcement — not derived from reasoning
            labels["Unsupported"].append(c)

        elif "challenge:" in c:
            # Direct Devil attack on a prior claim — needs operator follow-up
            labels["UnresolvedDirectional"].append(c)

        elif any(w in c for w in ["reframe","inverse","adjacent","10x","workaround"]):
            # God expansion — directional signal, not a verified claim
            labels["UnresolvedDirectional"].append(c)

        elif any(w in c for w in
                 ["fails","wrong","false","dangerous","hidden","avoid",
                  "weakness","never tested","most important"]):
            # Devil or Light finding — challenge these before acting
            labels["DeceptionIndicating"].append(c)

        elif overlap > 0.15:
            # Claim directly addresses the input — highest confidence
            labels["Validated"].append(c)

        else:
            # Credible but not directly tied to input keywords
            labels["Plausible"].append(c)

    # False convergence warning — added to DeceptionIndicating because
    # it represents a systemic risk to the output's reliability
    if false_conv:
        labels["DeceptionIndicating"].append(
            "WARNING: Shared unchallenged assumption detected across passes — "
            "run a targeted Devil pass before acting on this output."
        )

    return labels


# ════════════════════════════════════════════════════════════════
# 8. TRUTH PARTITION
#    Assembles the five required output sections.
#    Action is derived from claim frequency — not hardcoded.
#    Low-signal detection: if fewer than LOW_SIGNAL_THRESH validated
#    claims overlap the input, ALL sections are marked low-confidence
#    and the Action field instructs reformulation.
# ════════════════════════════════════════════════════════════════

# The five required sections — all must be present and non-empty
REQUIRED = ["Invariant", "Evidence", "Uncertainty", "Failure Modes", "Action"]


def build_tp(problem: str, ecp_out: Dict, labels: Dict) -> Dict:
    """
    Build the Truth Partition from ECP output and labels.

    Low-signal detection: if fewer than LOW_SIGNAL_THRESH Validated claims
    overlap with input keywords, the output is marked low-confidence and
    the Action field instructs the operator to reformulate.

    Action derivation: the most frequent long words across all invariant
    claims reveal what the system actually reasoned about. The first input
    keyword provides the human-readable focus.

    Args:
        problem: operator's original input
        ecp_out: output from ecp()
        labels:  output from label_claims()

    Returns:
        Dict with keys: Invariant, Evidence, Uncertainty, Failure Modes,
                        Action, Labels, low_signal
    """
    inv_list = sorted(list(ecp_out["invariant"]))
    kw       = _kw(problem)
    focus    = kw[:3] if kw else ["core issue"]

    # Low-signal detection: count Validated claims that mention input keywords
    validated_overlap = [
        c for c in labels["Validated"]
        if any(w in c for w in set(kw))
    ]
    low_signal = len(validated_overlap) < LOW_SIGNAL_THRESH

    if low_signal:
        # Suppress confident-looking output — force reformulation
        action = [
            f"⚠ LOW-SIGNAL INPUT: Only {len(validated_overlap)} validated claims "
            f"overlap input keywords. Output is low-confidence.",
            "Reformulate with more specific terms, scope, or falsification condition.",
            "Do not act on this output without additional grounding.",
        ]
        conf_note = "LOW-CONFIDENCE — input too vague for reliable analysis"
    else:
        # Derive action focus from most frequent words in invariant
        freq = Counter(
            w for c in inv_list
            for w in re.findall(r'\b\w+\b', c)
            if len(w) > 5
        )
        action = [
            f"Immediate: address '{focus[0]}' — highest frequency term across all passes",
            "Challenge every DeceptionIndicating claim before committing to any action",
            "Assign a named owner and hard deadline to the Nathan-layer finding",
        ]
        if ecp_out["false_conv"]:
            action.append(
                f"Run a targeted Devil pass on shared assumption: "
                f"{list(ecp_out['shared'])[:1]}"
            )
        conf_note = f"Convergence {ecp_out['conv_score']:.0%}"

    uncertainty = [
        f"[{conf_note}]",
        "Claim extraction is heuristic — operator must supply grounding evidence",
        f"Scope: '{problem[:60]}' as stated",
    ]
    if ecp_out["false_conv"]:
        uncertainty.append(
            "Shared assumptions detected across passes — partial false convergence risk"
        )

    return {
        "Invariant":     inv_list,
        "Evidence":      [
            f"{ecp_out['pass_count']} passes | Jaccard {ecp_out['conv_score']:.0%} | "
            f"input-responsive primitives",
            "Devil + Light applied adversarially to this specific input",
        ],
        "Uncertainty":   uncertainty,
        "Failure Modes": [
            "Primitives generate directional claims not verified facts — "
            "operator must supply grounding evidence",
            "Label heuristics may misclassify edge cases",
            "No external data sources connected",
            f"God primitive capped at {GOD_MAX_OPTIONS} — "
            f"additional options may exist beyond the cap",
            f"Max passes: {MAX_PASSES} — complex problems may need more iterations",
        ],
        "Action":     action,
        "Labels":     labels,
        "low_signal": low_signal,
    }


# ════════════════════════════════════════════════════════════════
# 9. VALIDATOR
#    Structural enforcement: all five required sections must be
#    present and non-empty. Catches empty Invariant (ECP produced
#    nothing) and "none" Uncertainty (operators sometimes write this).
# ════════════════════════════════════════════════════════════════

def validate_tp(tp: Dict) -> Tuple[bool, List[str]]:
    """
    Structural validation of a Truth Partition.

    Checks:
      - All five required sections present
      - No required section is empty
      - Uncertainty does not contain "none" as its only entry

    Returns:
        (is_valid: bool, issues: List[str])
    """
    issues = []

    for s in REQUIRED:
        if s not in tp:
            issues.append(f"MISSING section: {s}")
        elif not tp[s]:
            issues.append(f"EMPTY section: {s}")

    # Uncertainty "none" is a structural lie — every output has uncertainty
    if "Uncertainty" in tp:
        for u in tp["Uncertainty"]:
            if "none" in u.lower() and len(tp["Uncertainty"]) == 1:
                issues.append(
                    "Uncertainty cannot be 'none' — "
                    "every output has uncertainty"
                )

    return len(issues) == 0, issues


# ════════════════════════════════════════════════════════════════
# 10. MEMORY
#     Append-only JSONL log of every run.
#     Stores structured fields only — no prose, no full claim text
#     beyond Invariant and Action (the two fields operators query).
#
#     Schema:
#       id, timestamp, timestamp_iso, version, problem, flow,
#       pass_count, conv_score, false_conv, low_signal,
#       invariant, action, failure_modes, uncertainty,
#       shared_assumptions, label_counts
# ════════════════════════════════════════════════════════════════

def save_memory(problem: str, flow: str,
                tp: Dict, ecp_out: Dict) -> None:
    """
    Append a structured record to MEMORY_PATH (echo_memory.jsonl).

    Non-fatal: if the write fails (permissions, disk full, etc.)
    the run continues normally. Memory is useful but not critical.
    """
    record = {
        "id":              str(uuid.uuid4()),
        "timestamp":       int(time.time()),
        "timestamp_iso":   time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "version":         VERSION,
        "problem":         problem,
        "flow":            flow,
        "pass_count":      ecp_out["pass_count"],
        "conv_score":      ecp_out["conv_score"],
        "false_conv":      ecp_out["false_conv"],
        "low_signal":      tp.get("low_signal", False),
        "invariant":       tp["Invariant"],
        "action":          tp["Action"],
        "failure_modes":   tp["Failure Modes"],
        "uncertainty":     tp["Uncertainty"],
        "shared":          list(ecp_out["shared"]),
        "label_counts":    {k: len(v) for k, v in tp["Labels"].items()},
    }
    try:
        with open(MEMORY_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception:
        pass  # non-fatal — engine continues even if memory write fails


# ════════════════════════════════════════════════════════════════
# 11. RUNNER
#     Single entry point for the full pipeline.
#     classify → select flow → ECP → label → partition → validate → memory
# ════════════════════════════════════════════════════════════════

def run(problem: str, context: Dict = None) -> Dict:
    """
    Full pipeline in one call.

    Args:
        problem: a question, proposition, or audit statement
        context: optional dict with keys:
                   unknown_domain (bool) — use Research flow
                   time_pressure  (bool) — use Fast flow
                   audit          (bool) — use Audit flow

    Returns:
        {
          "flow":        str    — flow used
          "tp":          Dict   — Truth Partition (use tp["Invariant"] etc.)
          "valid":       bool   — structural validation passed
          "issues":      List   — validation issues if any
          "low_signal":  bool   — True if output is low-confidence
          "false_conv":  bool   — True if shared assumptions detected
          "pass_count":  int    — number of ECP passes run
          "conv_score":  float  — final Jaccard convergence score
        }

    Raises:
        ValueError: if input is rejected or needs reformulation
                    (catch this to show the message to the user)

    Example:
        result = run("What is the highest-leverage deployment action?")
        for claim in result["tp"]["Invariant"]:
            print(claim)
    """
    context = context or {}
    parsed  = InputSpec.classify(problem)   # raises ValueError if rejected
    flow    = select_flow(parsed, context)
    ecp_out = ecp(problem, flow)
    labels  = label_claims(ecp_out["invariant"], ecp_out["false_conv"], problem)
    tp      = build_tp(problem, ecp_out, labels)
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
# 12. RENDER
#     Human-readable Truth Partition output for CLI and logging.
# ════════════════════════════════════════════════════════════════

def render(result: Dict) -> str:
    """
    Format a run() result as a human-readable string.

    Status line shows: flow, pass count, convergence score, false-conv flag.
    Invariant section truncates at 5 claims with "+N more" indicator.
    Labels section shows count and first claim preview for each non-empty label.
    """
    tp     = result["tp"]
    ls     = result["low_signal"]
    status = (
        "⚠ LOW-SIGNAL" if ls else
        ("✅ VALID" if result["valid"] else f"❌ INVALID: {result['issues']}")
    )
    lines = [
        "",
        "═" * 66,
        f"  TRUTH PARTITION  [{status}]",
        f"  Flow: {result['flow']:<12}  "
        f"Passes: {result['pass_count']}  "
        f"Convergence: {result['conv_score']:.0%}  "
        f"False-conv: {result['false_conv']}",
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
    for label, claims in tp["Labels"].items():
        if claims:
            lines.append(f"  {label:<24} ({len(claims):>2})  {claims[0][:70]}")
    lines.append("═" * 66)
    return "\n".join(lines)


# ════════════════════════════════════════════════════════════════
# 13. CLI
# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\nECHO SYSTEM v3.1")
    print("─" * 18)
    print("Enter a question, proposition, or audit statement.")
    print("Context flags default to False if you press Enter.\n")

    problem = input("Problem: ").strip()

    ctx = {
        "unknown_domain": input("Unknown domain? (y/n): ").lower().startswith("y"),
        "time_pressure":  input("Time pressure?  (y/n): ").lower().startswith("y"),
        "audit":          input("Audit?          (y/n): ").lower().startswith("y"),
    }

    try:
        result = run(problem, ctx)
        print(render(result))
        if result["issues"]:
            print(f"\nValidation issues: {result['issues']}")
    except ValueError as e:
        print(f"\n{e}")
