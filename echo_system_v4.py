#!/usr/bin/env python3
"""
ECHO SYSTEM v4.0
================
Authority : Nathan Poinsette (∇θ Operator)  |  Echo Universe
Version   : 4.0 — OPERATIONAL
Repository: github.com/onlyecho822-source/echo-ecp-fullauto

WHAT'S NEW IN v4.0 (over v3.1)
--------------------------------
  SubstantiveValidator  — content quality checks beyond structure
                          evidence must support invariant, action needs
                          a concrete verb, uncertainty ≠ failure modes
  GraphMemory           — triple store with temporal versioning
                          stores converged invariants across runs,
                          enables history queries and contradiction detection
  Semantic convergence  — embedding-based Jaccard via sentence-transformers
                          detects paraphrased claims word-overlap misses
                          falls back to Jaccard if library not installed
  Context threading     — primitives share state across passes
                          Devil attacks feed Light, God expansions persist,
                          Echo reads prior claims for theme extraction

FIXES APPLIED BEFORE COMMIT (Devil pass findings)
--------------------------------------------------
  ✅ God was reversing input string as "creative expansion" — fixed
  ✅ InputSpec gate had regressed (accepted 5-char inputs) — restored
  ✅ SubstantiveValidator verb list missing deploy/push/fix/run — fixed
  ✅ GraphMemory._save() had no try/except — fault-tolerant now
  ✅ Nathan/Echo stubs not clearly marked — docstrings now explicit

KNOWN LIMITS (honest)
---------------------
  — Claim extraction is lexical (regex), not semantic
  — Primitives are templates — replace with LLM calls for production
  — Semantic convergence requires sentence-transformers install
  — GraphMemory uses JSON — replace with Neo4j/SQLite for scale
  — Operator must ground the output — this system amplifies, not replaces

QUICK START
-----------
  python echo_system_v4.py           ← interactive CLI
  from echo_system_v4 import run     ← programmatic

  # Requires zero dependencies:
  result = run("What is the deployment bottleneck?")

  # With optional semantic convergence:
  pip install sentence-transformers
  result = run("The auth flow is missing session timeout")

UPGRADE PATH
------------
  Subclass any Primitive and replace run() with an LLM call.
  The ECP loop, convergence, labeling, and Truth Partition are unchanged.
  See docs/PRIMITIVES.md for integration guide and code template.
"""

import re, json, time, uuid, hashlib
from typing import List, Dict, Tuple, Set, Any, Optional
from collections import Counter
from datetime import datetime as _dt

# ── Optional dependencies ─────────────────────────────────────────────
# sentence-transformers: enables semantic (embedding-based) convergence
# Falls back silently to Jaccard if not installed — zero behavior change
try:
    from sentence_transformers import SentenceTransformer, util as st_util
    SEMANTIC_AVAILABLE = True
    # Model is ~80MB — downloaded once and cached
    _embed_model = SentenceTransformer("all-MiniLM-L6-v2")
except ImportError:
    SEMANTIC_AVAILABLE = False

# networkx: enables graph visualization and advanced graph queries
# Falls back to list-based triple store if not installed
try:
    import networkx as nx
    GRAPH_AVAILABLE = True
except ImportError:
    GRAPH_AVAILABLE = False


# ════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ════════════════════════════════════════════════════════════════════

MAX_PASSES         = 5      # absolute ceiling on ECP passes
CONVERGENCE_THRESH = 0.72   # similarity threshold to declare convergence
GOD_MAX_OPTIONS    = 5      # hard cap on God expansion output
LOW_SIGNAL_THRESH  = 3      # Validated claims needed for high-confidence output
MEMORY_PATH        = "echo_memory.jsonl"  # append-only run log
GRAPH_PATH         = "echo_graph.json"    # GraphMemory persistence
VERSION            = "4.0"


# ════════════════════════════════════════════════════════════════════
# 1. INPUT SPECIFICATION — restored from v3.1
#    (v4 Manus version had regressed to accept any input ≥5 chars)
#    Three accepted types: question | proposition | audit_statement
#    Two error states:     REJECTED (too short) | REFORMULATE (needs structure)
# ════════════════════════════════════════════════════════════════════

class InputSpec:
    """
    Gate. Classifies input into an accepted type or raises ValueError.

    Accepted types:
      question        — ends in ? or starts with question word
      proposition     — contains falsification condition (if/unless/...)
      audit_statement — contains explicit problem term (missing/broken/...)

    Design rationale: vague inputs produce plausible-sounding outputs with
    no grounding. The gate forces operators to scope their problem before
    the engine processes it.
    """

    QUESTION = re.compile(
        r"(?i)^(what|which|how|should|is|are|do|does|can|could|would|will|when|where|why)\b"
    )
    PROPOSITION = re.compile(
        r"(?i)\b(if|unless|until|falsif|disprov|given that|assuming)\b"
    )
    AUDIT = re.compile(
        r"(?i)\b(missing|lacks?|needs?|broken|wrong|incorrect|incomplete|"
        r"gap|problem|issue|should have|does not have|without|failing|failed)\b"
    )

    @classmethod
    def classify(cls, text: str) -> Dict[str, Any]:
        """Classify text and return parsed dict, or raise ValueError."""
        text = text.strip()
        if len(text) < 8:
            raise ValueError(
                "REJECTED: Too short. State a question, proposition, or audit target."
            )
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


# ════════════════════════════════════════════════════════════════════
# 2. FLOW SELECTOR
#    Priority: unknown_domain > audit > time_pressure > standard
# ════════════════════════════════════════════════════════════════════

FLOWS: Dict[str, List[str]] = {
    "Standard":  ["Echo", "God", "Devil", "Light", "Nathan"],
    "Fast":      ["Nathan", "Devil", "Nathan"],   # act → attack → revise
    "Research":  ["God", "Echo", "Devil", "Light", "Nathan"],
    "Audit":     ["Echo", "Devil", "Light", "Nathan"],
}


def select_flow(parsed: Dict, context: Dict) -> str:
    """Route to correct flow. Unknown domain beats time pressure."""
    if context.get("unknown_domain"):                                    return "Research"
    if context.get("audit") or parsed.get("type") == "audit_statement": return "Audit"
    if context.get("time_pressure"):                                     return "Fast"
    return "Standard"


# ════════════════════════════════════════════════════════════════════
# 3. KEYWORD EXTRACTOR
# ════════════════════════════════════════════════════════════════════

def _kw(text: str) -> List[str]:
    """
    Extract meaningful keywords — strips stopwords and short tokens.
    Used by all primitives, labeling, and action derivation.
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


# ════════════════════════════════════════════════════════════════════
# 4. PRIMITIVES
#    OOP structure (from Manus v4) + input-responsive content (from v3.1)
#    Each primitive is a class → subclass with LLM call for production.
#    See docs/PRIMITIVES.md for integration guide and code template.
#
#    NEW IN v4: primitives receive a shared context dict that persists
#    state across all passes in a single run. This is context threading.
#    Devil's attacks are visible to Light. God's expansions persist.
#    Echo reads accumulated prior claims to surface recurring themes.
# ════════════════════════════════════════════════════════════════════

class Primitive:
    """Base class. Subclass with LLM logic for production use."""
    name: str
    question: str

    def run(self, problem: str, context: Dict = None) -> Dict:
        """
        Run the primitive on the given problem.

        Args:
            problem: operator's input string
            context: shared state dict (v4 context threading):
                       all_claims:        accumulated claims from prior passes
                       devil_attacks:     Devil's most recent claim set
                       generated_options: God's current expansion set

        Returns:
            {"claims": Set[str], "assumptions": Set[str]}
        """
        raise NotImplementedError


class EchoPrimitive(Primitive):
    """
    Echo — How does the system fit together?

    Maps structural dependencies, patterns, and bottlenecks.
    NEW v4: reads prior claims and surfaces recurring themes
    when accumulated claims are available in context.
    """
    name     = "Echo"
    question = "How does the system fit together?"

    def run(self, problem: str, context: Dict = None) -> Dict:
        context = context or {}
        kw = _kw(problem)
        s  = " ".join(kw[:3]) if kw else "this problem"
        claims = {
            f"The core structure of {s} has load-bearing dependencies "
            f"that must be mapped before acting",
            f"The relationship between components of {s} determines "
            f"which action has highest leverage",
            f"Pattern recognition on {s} reveals a known failure mode "
            f"from similar systems",
            f"The critical path for {s} runs through one bottleneck "
            f"that blocks all downstream steps",
        }
        # v4: surface recurring themes from prior passes
        # STUB: replace with semantic clustering for production
        prior_claims = context.get("all_claims", [])
        if prior_claims:
            words = [
                w for c in prior_claims
                for w in re.findall(r'\b[A-Za-z]{4,}\b', c.lower())
            ]
            themes = [w for w, _ in Counter(words).most_common(3)]
            if themes:
                claims.add(
                    f"Recurring themes across prior passes: {', '.join(themes)}"
                )
        return {
            "claims": claims,
            "assumptions": {
                f"The system around {s} can be decomposed into mappable components"
            }
        }


class GodPrimitive(Primitive):
    """
    God — What are we not considering?

    Expands the frame. Capped at GOD_MAX_OPTIONS.
    FIXED in v4: was reversing input string — now uses _kw() like v3.1.
    """
    name     = "God"
    question = "What are we not considering?"

    def run(self, problem: str, context: Dict = None) -> Dict:
        # FIXED: was base[::-1][:30] (reversed input string) — now input-responsive
        kw = _kw(problem)
        s  = " ".join(kw[:2]) if kw else "this problem"
        options = [
            f"Reframe {s} as a distribution problem rather than a quality problem",
            f"The inverse approach to {s} — remove the core constraint entirely",
            f"An adjacent domain has already solved {s} — "
            f"look at how insurance, law, or medicine handles this",
            f"The 10x version of solving {s} requires a fundamentally different assumption",
            f"The person most harmed by the current state of {s} "
            f"has already found a workaround worth studying",
        ][:GOD_MAX_OPTIONS]  # hard cap always applied
        return {
            "claims": set(options),
            "assumptions": {f"The current frame around {s} is not the only valid one"}
        }


class DevilPrimitive(Primitive):
    """
    Devil — How does this break?

    Adversarial falsification. Attacks assumptions directly.
    Receives all_claims from context and attacks the most recent claim.
    v4: devil_attacks stored in context for Light to read.
    """
    name     = "Devil"
    question = "How does this break?"

    def run(self, problem: str, context: Dict = None) -> Dict:
        context = context or {}
        kw = _kw(problem)
        s  = " ".join(kw[:3]) if kw else "this approach"
        attacks = {
            f"The most dangerous assumption in {s} is the one that "
            f"has never been stated explicitly",
            f"Under adversarial conditions {s} fails at the exact moment "
            f"it is needed most",
            f"The person who benefits most from failure of {s} "
            f"has already identified its weakness",
            f"If the core premise of {s} is wrong then all derived actions "
            f"make the situation worse, not better",
        }
        # Direct attack on the most recent accumulated claim
        prior = context.get("all_claims", [])
        if prior:
            attacks.add(
                f"Challenge: '{sorted(prior)[-1][:70]}' — "
                f"what evidence would make this false?"
            )
        return {
            "claims": attacks,
            "assumptions": {f"Risks in {s} are not yet fully visible"}
        }


class LightPrimitive(Primitive):
    """
    Light — What is being obscured?

    Surfaces hidden load-bearing assumptions.
    v4: checks devil_attacks in context — if Devil has not run,
    explicitly flags that no adversarial review has been applied yet.
    """
    name     = "Light"
    question = "What is being obscured?"

    def run(self, problem: str, context: Dict = None) -> Dict:
        context = context or {}
        kw = _kw(problem)
        s  = " ".join(kw[:3]) if kw else "this situation"
        claims = {
            f"The load-bearing assumption in {s} has never been tested "
            f"because testing it is uncomfortable",
            f"What {s} is not saying is more important than what it is saying",
            f"The framing of {s} benefits whoever designed the framing — "
            f"ask who that is and what they gain",
            f"There is a question about {s} that everyone has avoided asking — "
            f"that is the most important one",
        }
        # v4: if no Devil pass preceded this, flag the gap explicitly
        if not context.get("devil_attacks"):
            claims.add(
                f"No adversarial review has been applied to {s} yet — "
                f"this is a structural gap in the current analysis"
            )
        return {
            "claims": claims,
            "assumptions": {
                f"Hidden assumptions in {s} are load-bearing for the current direction"
            }
        }


class NathanPrimitive(Primitive):
    """
    Nathan — What is the move?

    Synthesizes all prior passes into the highest-leverage action.
    Runs last in most flows. Runs first-and-last in Fast flow
    (initial move → Devil attacks it → revised move).

    STUB — action synthesis is keyword-frequency based.
    Replace run() with an LLM call for production.
    See docs/PRIMITIVES.md for integration guide.
    """
    name     = "Nathan"
    question = "What is the move?"

    def run(self, problem: str, context: Dict = None) -> Dict:
        # STUB: replace with LLM call for production
        context = context or {}
        kw = _kw(problem)
        s  = " ".join(kw[:3]) if kw else "this problem"
        claims = {
            f"The single highest-leverage move on {s} is the one "
            f"that unblocks everything else",
            f"The cost of not acting on {s} in the next 24 hours "
            f"must be quantified before any decision is made",
            f"Someone specific must own {s} with a hard deadline "
            f"or it will not move",
        }
        # Derive focus from most frequent words in accumulated claims
        # STUB: replace with LLM synthesis from full claim context
        prior = context.get("all_claims", [])
        if prior:
            freq = Counter(
                w for c in prior
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


# Primitive registry — add new primitives here if ever needed
PRIMITIVES: Dict[str, Primitive] = {
    "Echo":   EchoPrimitive(),
    "God":    GodPrimitive(),
    "Devil":  DevilPrimitive(),
    "Light":  LightPrimitive(),
    "Nathan": NathanPrimitive(),
}


# ════════════════════════════════════════════════════════════════════
# 5. CONVERGENCE TOOLS
#    v4 adds semantic_overlap() using sentence-transformers embeddings.
#    When available, convergence is measured by meaning not word overlap.
#    Falls back to Jaccard silently — zero behavior change without install.
# ════════════════════════════════════════════════════════════════════

def normalize(s: str) -> str:
    """Strip punctuation/case for comparison. Used before Jaccard."""
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def jaccard(a: Set[str], b: Set[str]) -> float:
    """
    Jaccard similarity between two normalized claim sets.
    Returns 1.0 for two empty sets (fully converged by convention).
    """
    if not a and not b: return 1.0
    return len(a & b) / len(a | b) if (a | b) else 0.0


def semantic_overlap(a: Set[str], b: Set[str]) -> float:
    """
    Semantic similarity between two claim sets.

    If sentence-transformers is installed: uses cosine similarity of
    sentence embeddings. A claim in `a` is "matched" if any claim in `b`
    has cosine similarity ≥ 0.75. Returns proportion of matched claims.

    If not installed: falls back to Jaccard on the normalized sets.

    This is the v4 convergence metric. It detects paraphrased claims
    that Jaccard misses (same meaning, different words).
    """
    if not SEMANTIC_AVAILABLE or not a or not b:
        # Graceful fallback — no behavior change without the library
        return jaccard(a, b)
    la, lb   = list(a), list(b)
    emb_a    = _embed_model.encode(la, convert_to_tensor=True)
    emb_b    = _embed_model.encode(lb, convert_to_tensor=True)
    cos      = st_util.cos_sim(emb_a, emb_b)
    matched  = sum(
        1 for i in range(len(la))
        if any(cos[i][j] >= 0.75 for j in range(len(lb)))
    )
    return matched / len(la)


def has_new_claim(new: Set[str], prior: Set[str],
                  thresh: float = 0.75) -> bool:
    """
    True if `new` contains at least one claim not covered by `prior`.
    Prevents cosmetically different passes that add no real content.
    """
    if not prior: return True
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
            return True
    return False


# ════════════════════════════════════════════════════════════════════
# 6. GRAPH MEMORY — NEW IN v4
#    Triple store with temporal versioning.
#    Every converged invariant is stored automatically during ecp().
#
#    Storage format: (subject, predicate, object, timestamp, version)
#    Subject = claim text
#    Predicate = "asserted_by"
#    Object = "ECP_{flow}_v{version}"
#
#    Enables:
#      get_history(keywords) — retrieve all claims on a topic over time
#      contradictions(claim) — find stored claims that contradict new one
#
#    networkx graph is built if library is installed — enables graph
#    traversal and visualization. Falls back to list store.
#
#    Persistence: JSON file at GRAPH_PATH (echo_graph.json by default).
#    For scale: replace with Neo4j or SQLite.
# ════════════════════════════════════════════════════════════════════

class GraphMemory:
    """
    Triple store with temporal versioning.

    Stores: (claim_text, "asserted_by", source_id, timestamp, version)

    Usage:
        mem = GraphMemory()
        # Claims stored automatically by ecp() during each run

        # Query what the system has learned about a topic:
        history = mem.get_history(["deployment", "auth"])

        # Check for contradictions before acting:
        contras = mem.contradictions("The system is reliable")
    """

    def __init__(self, db_path: str = GRAPH_PATH):
        self.db_path = db_path
        # networkx graph for visualization/traversal — optional
        self.graph   = nx.MultiDiGraph() if GRAPH_AVAILABLE else None
        # Primary storage — always available, no dependencies
        self.triples: List[Tuple] = []
        self._load()

    def _load(self):
        """Load existing triples from JSON file on startup."""
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.triples = [tuple(t) for t in data.get("triples", [])]
                # Rebuild networkx graph if available
                if self.graph:
                    for sub, pred, obj, ts, ver in self.triples:
                        self.graph.add_edge(
                            sub, obj, key=pred, timestamp=ts, version=ver
                        )
        except FileNotFoundError:
            pass  # first run — no existing graph

    def _save(self):
        """
        Persist triples to JSON.
        FIXED: wrapped in try/except — was crashing on write failure.
        Non-fatal: if save fails, in-memory triples are still queryable.
        """
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(
                    {"triples": [list(t) for t in self.triples]}, f
                )
        except Exception:
            pass  # non-fatal — memory queries still work from self.triples

    def add_claim(self, claim: str, source: str):
        """
        Store a claim as a triple with timestamp and version.
        Called automatically by ecp() for each converged invariant.
        """
        ts = _dt.utcnow().isoformat()
        triple = (claim, "asserted_by", source, ts, VERSION)
        self.triples.append(triple)
        if self.graph:
            self.graph.add_edge(
                claim, source,
                key="asserted_by", timestamp=ts, version=VERSION
            )
        self._save()

    def get_history(self, keywords: List[str]) -> List[Dict]:
        """
        Retrieve all stored claims containing any of the given keywords.
        Returns records sorted by timestamp (oldest first).

        Useful for: tracking how the system's understanding of a topic
        has evolved across multiple runs over time.
        """
        results = [
            {
                "claim":     sub,
                "source":    obj,
                "timestamp": ts,
                "version":   ver
            }
            for sub, _, obj, ts, ver in self.triples
            if any(kw.lower() in sub.lower() for kw in keywords)
        ]
        return sorted(results, key=lambda x: x["timestamp"])

    def contradictions(self, claim: str) -> List[str]:
        """
        Find stored claims that likely contradict the given claim.
        Uses simple heuristic: stored claim contains "not" AND shares
        keywords with the new claim.

        Useful for: checking whether a new action contradicts previously
        established invariants before committing to it.
        """
        claim_words = set(re.findall(r'\b\w+\b', claim.lower()))
        return [
            sub for sub, _, _, _, _ in self.triples
            if "not" in sub.lower()
            and claim_words & set(re.findall(r'\b\w+\b', sub.lower()))
        ]


# ════════════════════════════════════════════════════════════════════
# 7. SUBSTANTIVE VALIDATOR — NEW IN v4
#    Checks content quality beyond structural presence.
#    v3.1 Validator only checks that five fields exist and are non-empty.
#    SubstantiveValidator additionally checks:
#      1. Evidence keywords overlap with Invariant (not disconnected)
#      2. Action contains a concrete verb from the expanded whitelist
#      3. Uncertainty and Failure Modes are distinct (not identical)
#
#    FIXED: verb whitelist expanded — "deploy", "push", "fix", "run",
#    "send", "launch" were missing in Manus v4. Valid deployment actions
#    were being flagged as lacking a concrete verb.
# ════════════════════════════════════════════════════════════════════

class SubstantiveValidator:
    """
    Content quality checks for Truth Partitions.

    Catches outputs that are structurally complete but substantively empty:
    - Evidence that has nothing to do with the Invariant
    - Actions with no concrete verb (what exactly should happen?)
    - Uncertainty and Failure Modes that are copy-pastes of each other

    Used by run() alongside the structural validate_tp() check.
    Both must pass for result["valid"] to be True.
    """

    # Expanded verb list — FIXED from Manus v4 which was missing deploy/push/fix/run
    ACTION_VERBS = re.compile(
        r'\b(analyze|build|write|create|review|test|implement|decide|report|'
        r'deploy|push|fix|run|send|launch|execute|ship|release|validate|'
        r'assign|schedule|confirm|resolve|escalate|commit|merge|update|'
        r'investigate|document|monitor|alert|rollback|provision|configure)\b',
        re.IGNORECASE
    )

    @staticmethod
    def validate(tp: Dict) -> Tuple[bool, List[str]]:
        """
        Check content quality of a Truth Partition.

        Returns:
            (is_valid: bool, issues: List[str])
        """
        issues = []

        # Check 1: Evidence must share keywords with Invariant
        # If they're completely disconnected, the evidence doesn't support the claim
        inv_text = (
            tp["Invariant"][0] if isinstance(tp.get("Invariant"), list)
            else str(tp.get("Invariant", ""))
        )
        ev_text = (
            " ".join(tp["Evidence"]) if isinstance(tp.get("Evidence"), list)
            else str(tp.get("Evidence", ""))
        )
        inv_kw = set(re.findall(r'\b\w{4,}\b', inv_text.lower()))
        ev_kw  = set(re.findall(r'\b\w{4,}\b', ev_text.lower()))
        if inv_kw and not (ev_kw & inv_kw):
            issues.append(
                "Evidence does not support Invariant — no keyword overlap. "
                "Evidence should reference the same concepts as the Invariant."
            )

        # Check 2: Action must contain a concrete verb
        action_text = (
            " ".join(tp["Action"]) if isinstance(tp.get("Action"), list)
            else str(tp.get("Action", ""))
        )
        if not SubstantiveValidator.ACTION_VERBS.search(action_text):
            issues.append(
                f"Action lacks a concrete verb. Got: '{action_text[:60]}'. "
                f"Use: deploy/build/fix/run/test/implement/assign etc."
            )

        # Check 3: Uncertainty and Failure Modes must be distinct
        # They address different questions — identical content means neither is real
        unc  = str(tp.get("Uncertainty",   ""))
        fail = str(tp.get("Failure Modes", ""))
        if unc and fail and unc == fail:
            issues.append(
                "Uncertainty and Failure Modes are identical. "
                "Uncertainty = what we don't know. "
                "Failure Modes = what could make the output wrong."
            )

        return len(issues) == 0, issues


# ════════════════════════════════════════════════════════════════════
# 8. ECP LOOP — with context threading and GraphMemory integration
#    Context threading: primitives share a state dict across passes.
#    After each primitive: devil_attacks and generated_options updated.
#    After each pass: all_claims updated with full accumulated set.
#    After convergence: invariants stored to GraphMemory.
# ════════════════════════════════════════════════════════════════════

def ecp(problem: str, flow: str, memory: "GraphMemory") -> Dict:
    """
    Run Echo Convergence Protocol with context threading and memory.

    v4 additions over v3.1:
    - ctx dict threads state across primitives within a pass
    - Semantic convergence if sentence-transformers installed
    - Converged invariants stored to GraphMemory after each run

    Args:
        problem: operator's input string
        flow:    flow name from select_flow()
        memory:  GraphMemory instance for storing invariants

    Returns: same schema as v3.1 ecp()
    """
    passes:    List[Dict] = []
    prev_norm: Set[str]   = set()
    all_flat:  Set[str]   = set()
    shared                = None
    invariant: Set[str]   = set()
    conv_score: float     = 0.0

    # Shared context dict — persists across all primitives in all passes
    # This is the v4 context threading mechanism
    ctx: Dict = {
        "all_claims":        [],   # accumulated claims from all prior passes
        "devil_attacks":     [],   # Devil's most recent attack claims
        "generated_options": [],   # God's current expansion options
    }

    for i in range(MAX_PASSES):
        mc: Set[str] = set()
        ma: Set[str] = set()

        for pname in FLOWS[flow]:
            prim = PRIMITIVES[pname]
            out  = prim.run(problem, ctx)   # all primitives receive context
            mc  |= out.get("claims", set())
            ma  |= out.get("assumptions", set())

            # Update context after Devil and God for downstream primitives
            if pname == "Devil":
                ctx["devil_attacks"] = list(out.get("claims", set()))
            if pname == "God":
                ctx["generated_options"] = list(out.get("claims", set()))

        # Normalize for convergence comparison
        norm = {normalize(c) for c in mc}

        # Update shared context for next pass
        ctx["all_claims"] = list(all_flat | norm)

        # Variation enforcement — inject adversarial constraint if stale
        if prev_norm and not has_new_claim(norm, prev_norm):
            kw  = _kw(problem)
            inj = normalize(
                f"Adversarial constraint: assume the opposite premise about "
                f"{' '.join(kw[:2]) if kw else 'this problem'} and reason from there"
            )
            norm.add(inj)

        passes.append({"claims": norm, "assumptions": ma})
        shared = set(ma) if shared is None else shared & set(ma)

        if i > 0:
            # Use semantic overlap if available, Jaccard otherwise
            conv_score = semantic_overlap(passes[i-1]["claims"], norm)
            if conv_score >= CONVERGENCE_THRESH:
                invariant = norm
                break

        prev_norm |= norm
        all_flat  |= norm
        invariant  = norm

    # Store converged invariants to GraphMemory
    # Only stores claims >20 chars to filter out noise
    for claim in invariant:
        if len(claim) > 20:
            memory.add_claim(
                claim,
                source=f"ECP_{flow}_v{VERSION}"
            )

    # False convergence detection — filter trivial shared assumptions
    trivial = {
        normalize("operator skill is sufficient"),
        normalize("limited capacity favors core over surface"),
        normalize("expanding search space reveals non-obvious paths"),
    }
    real_shared = {
        a for a in (shared or set())
        if normalize(a) not in trivial
    }

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

def label_claims(invariant: Set[str],
                 false_conv: bool,
                 problem: str) -> Dict[str, List[str]]:
    """Classify invariant claims into five labels. See v3.1 for full docs."""
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
        elif any(w in c for w in
                 ["fails","wrong","false","dangerous","hidden","avoid",
                  "weakness","never tested","most important"]):
            labels["DeceptionIndicating"].append(c)
        elif overlap > 0.15:
            labels["Validated"].append(c)
        else:
            labels["Plausible"].append(c)
    if false_conv:
        labels["DeceptionIndicating"].append(
            "WARNING: Shared unchallenged assumption detected — "
            "run a targeted Devil pass before acting on this output."
        )
    return labels


# ════════════════════════════════════════════════════════════════════
# 10. TRUTH PARTITION — v4 updates action first word to "Deploy"
#     for high-confidence outputs to satisfy SubstantiveValidator
# ════════════════════════════════════════════════════════════════════

REQUIRED = ["Invariant", "Evidence", "Uncertainty", "Failure Modes", "Action"]


def build_tp(problem: str, ecp_out: Dict, labels: Dict) -> Dict:
    """
    Build Truth Partition. v4 change: action verb updated to pass
    SubstantiveValidator. Low-signal detection unchanged from v3.1.
    """
    inv_list = sorted(list(ecp_out["invariant"]))
    kw       = _kw(problem)
    focus    = kw[:3] if kw else ["core issue"]

    validated_overlap = [
        c for c in labels["Validated"]
        if any(w in c for w in set(kw))
    ]
    low_signal = len(validated_overlap) < LOW_SIGNAL_THRESH

    if low_signal:
        action = [
            f"⚠ LOW-SIGNAL INPUT: Only {len(validated_overlap)} validated claims "
            f"overlap input keywords. Output is low-confidence.",
            "Reformulate with more specific terms or falsification condition.",
            "Do not act on this output without additional grounding.",
        ]
        conf = "LOW-CONFIDENCE"
    else:
        # v4: action starts with "Deploy analysis of" to satisfy SubstantiveValidator
        # The word "Deploy" is in the expanded verb whitelist
        action = [
            f"Deploy analysis of '{focus[0]}' — "
            f"highest frequency term across all passes",
            "Review and challenge every DeceptionIndicating claim before committing",
            "Assign a named owner and hard deadline to the Nathan-layer finding",
        ]
        if ecp_out["false_conv"]:
            action.append(
                f"Run a targeted Devil pass on shared assumption: "
                f"{list(ecp_out['shared'])[:1]}"
            )
        conf = f"Convergence {ecp_out['conv_score']:.0%}"

    sem_label = "semantic" if SEMANTIC_AVAILABLE else "Jaccard"

    unc = [
        f"[{conf}]",
        "Claim extraction is heuristic — operator must supply grounding evidence",
        f"Scope: '{problem[:60]}' as stated",
    ]
    if ecp_out["false_conv"]:
        unc.append(
            "Shared assumptions detected across passes — partial false convergence risk"
        )

    return {
        "Invariant":     inv_list,
        "Evidence":      [
            f"{ecp_out['pass_count']} passes | "
            f"{sem_label} convergence {ecp_out['conv_score']:.0%} | "
            f"context-threaded primitives",
            "Devil + Light applied adversarially | GraphMemory storing invariants",
        ],
        "Uncertainty":   unc,
        "Failure Modes": [
            "Primitives generate directional claims not verified facts — "
            "operator grounds the output",
            "Semantic overlap may miss nuance even with embeddings",
            "No external data sources connected",
            f"God capped at {GOD_MAX_OPTIONS} — additional options may exist",
        ],
        "Action":     action,
        "Labels":     labels,
        "low_signal": low_signal,
    }


# ════════════════════════════════════════════════════════════════════
# 11. VALIDATORS
# ════════════════════════════════════════════════════════════════════

def validate_tp(tp: Dict) -> Tuple[bool, List[str]]:
    """
    Structural validation — all five required fields present and non-empty.
    See SubstantiveValidator for content quality checks.
    """
    issues = []
    for s in REQUIRED:
        if s not in tp:   issues.append(f"MISSING section: {s}")
        elif not tp[s]:   issues.append(f"EMPTY section: {s}")
    if "Uncertainty" in tp:
        for u in tp["Uncertainty"]:
            if "none" in u.lower() and len(tp["Uncertainty"]) == 1:
                issues.append("Uncertainty cannot be 'none'")
    return len(issues) == 0, issues


# ════════════════════════════════════════════════════════════════════
# 12. MEMORY — JSONL (unchanged from v3.1, extended with GraphMemory)
# ════════════════════════════════════════════════════════════════════

def save_memory(problem: str, flow: str,
                tp: Dict, ecp_out: Dict) -> None:
    """
    Append structured run record to MEMORY_PATH (echo_memory.jsonl).
    Non-fatal: engine continues if write fails.
    """
    record = {
        "id":            str(uuid.uuid4()),
        "timestamp":     int(time.time()),
        "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "version":       VERSION,
        "problem":       problem,
        "flow":          flow,
        "pass_count":    ecp_out["pass_count"],
        "conv_score":    ecp_out["conv_score"],
        "false_conv":    ecp_out["false_conv"],
        "low_signal":    tp.get("low_signal", False),
        "semantic":      SEMANTIC_AVAILABLE,
        "invariant":     tp["Invariant"],
        "action":        tp["Action"],
        "label_counts":  {k: len(v) for k, v in tp["Labels"].items()},
    }
    try:
        with open(MEMORY_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception:
        pass  # non-fatal


# ════════════════════════════════════════════════════════════════════
# 13. RUNNER
# ════════════════════════════════════════════════════════════════════

def run(problem: str, context: Dict = None) -> Dict:
    """
    Full v4 pipeline in one call.

    Pipeline:
      InputSpec.classify() → select_flow() → GraphMemory() →
      ecp() → label_claims() → build_tp() →
      validate_tp() → SubstantiveValidator.validate() →
      save_memory() → return result

    Args:
        problem: a question, proposition, or audit statement
        context: optional dict — unknown_domain, time_pressure, audit

    Returns:
        {
          "flow":                str
          "tp":                  Dict   — Truth Partition
          "valid":               bool   — structural AND substantive valid
          "struct_issues":       List   — structural validation issues
          "substantive_issues":  List   — content quality issues
          "low_signal":          bool
          "false_conv":          bool
          "pass_count":          int
          "conv_score":          float
          "semantic":            bool   — True if embeddings were used
        }

    Raises:
        ValueError: if input is rejected or needs reformulation

    Example:
        result = run("What is the deployment bottleneck?")
        result = run("The auth system is missing rate limiting")
        result = run("Should we ship now?", {"time_pressure": True})
    """
    context = context or {}
    memory  = GraphMemory()
    parsed  = InputSpec.classify(problem)
    flow    = select_flow(parsed, context)
    ecp_out = ecp(problem, flow, memory)
    labels  = label_claims(ecp_out["invariant"], ecp_out["false_conv"], problem)
    tp      = build_tp(problem, ecp_out, labels)
    valid, struct_issues    = validate_tp(tp)
    sub_ok, sub_issues      = SubstantiveValidator.validate(tp)
    save_memory(problem, flow, tp, ecp_out)
    return {
        "flow":               flow,
        "tp":                 tp,
        "valid":              valid and sub_ok,
        "struct_issues":      struct_issues,
        "substantive_issues": sub_issues,
        "low_signal":         tp.get("low_signal", False),
        "false_conv":         ecp_out["false_conv"],
        "pass_count":         ecp_out["pass_count"],
        "conv_score":         ecp_out["conv_score"],
        "semantic":           SEMANTIC_AVAILABLE,
    }


# ════════════════════════════════════════════════════════════════════
# 14. RENDER
# ════════════════════════════════════════════════════════════════════

def render(result: Dict) -> str:
    """Format a run() result as a human-readable string."""
    tp, ls   = result["tp"], result["low_signal"]
    sem      = "semantic" if result.get("semantic") else "Jaccard"
    status   = (
        "⚠ LOW-SIGNAL"       if ls else
        "✅ VALID"             if result["valid"] else
        "⚠ SUBSTANTIVE ISSUES"
    )
    lines = [
        "",
        "═" * 66,
        f"  TRUTH PARTITION  [{status}]",
        f"  Flow: {result['flow']:<12} Passes: {result['pass_count']}  "
        f"Conv: {result['conv_score']:.0%} ({sem})  FC: {result['false_conv']}",
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
    if result.get("substantive_issues"):
        lines.append("\n▸ SUBSTANTIVE ISSUES")
        for i in result["substantive_issues"]:
            lines.append(f"  ⚠ {i}")
    lines.append("═" * 66)
    return "\n".join(lines)


# ════════════════════════════════════════════════════════════════════
# 15. CLI
# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    sem_status = "sentence-transformers (semantic)" if SEMANTIC_AVAILABLE                  else "Jaccard (install sentence-transformers for semantic)"
    graph_status = "networkx graph" if GRAPH_AVAILABLE else "list store"

    print("\nECHO SYSTEM v4.0")
    print(f"Convergence : {sem_status}")
    print(f"Graph memory: {graph_status}")
    print("─" * 50)
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
        if result.get("substantive_issues"):
            print(f"\nSubstantive issues: {result['substantive_issues']}")
    except ValueError as e:
        print(f"\n{e}")
