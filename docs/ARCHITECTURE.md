# ARCHITECTURE — Echo Convergence Protocol v3.1

**Authority:** Nathan Poinsette (∇θ Operator)
**Date:** 2026-03-31

---

## Design invariants

These survived every review pass and cannot be changed without
running ECP against the existing architecture:

1. Five primitives — Nathan, Echo, Devil, Light, God
2. Four flows — compositions of primitives, not separate modes
3. Truth Partition — five required fields, no exceptions
4. ECP as meta-method — governs iteration, sits above primitives
5. Input gate — three states: accepted, reformulate, rejected

---

## Component responsibilities

| Component | Responsibility | What it does NOT do |
|-----------|---------------|---------------------|
| InputSpec | Gate inputs | Route to flow |
| FlowSelector | Route to flow | Execute primitives |
| Primitives | Generate claims | Verify claims |
| ECP loop | Measure convergence | Interpret meaning |
| Labeling | Classify claims | Validate claims |
| Truth Partition | Structure output | Ground output in facts |
| Validator | Enforce structure | Enforce quality |
| Memory | Store structured fields | Store prose |

---

## Convergence mechanics

**Unit:** Normalized claim strings (lowercase, punctuation stripped)
**Metric:** Jaccard similarity on claim sets between consecutive passes
**Threshold:** 0.72 — stop when passes are 72%+ similar
**Variation rule:** Each pass must add ≥1 claim not in prior passes
**False convergence:** After all passes, scan for terms present in
every pass but never challenged. Flag as shared unchallenged assumption.

---

## Label taxonomy

| Label | Trigger condition |
|-------|------------------|
| Validated | Claim word-set overlaps input keywords >15% |
| Plausible | Does not meet Validated threshold |
| UnresolvedDirectional | Contains: reframe, inverse, adjacent, 10x, workaround, challenge: |
| DeceptionIndicating | Contains: fails, wrong, false, dangerous, hidden, avoid, weakness |
| Unsupported | Contains: adversarial constraint |

---

## Low-signal detection

Fires when: Validated claim count < LOW_SIGNAL_THRESH (default: 3)
Effect: Marks ALL output sections as LOW-CONFIDENCE
Action field: Instructs operator to reformulate before acting
Intent: Prevent confident-looking output on vague inputs

---

## Known limits

- Claim extraction: lexical (regex), not semantic (embeddings)
- Primitive content: template-generated, not LLM-reasoned
- Convergence: word overlap proxy for semantic agreement
- Operator dependence: system amplifies operator, does not replace them

---

## Extension points

Each primitive is a class. To upgrade to LLM-based reasoning:

```python
class DevilPrimitive(Primitive):
    def run(self, problem: str, prior=None) -> Dict:
        # Replace template logic with LLM call:
        response = llm.complete(
            system="You are Devil. Find every way this breaks.",
            user=problem
        )
        return {"claims": extract_claims(response), "assumptions": set()}
```

The ECP loop, convergence tools, labeling, and Truth Partition
all work unchanged with LLM-backed primitives.

---

*∇θ — 2026-03-31T04:34:33Z*
