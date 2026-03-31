# PRIMITIVES — Reference

**Authority:** Nathan Poinsette (∇θ Operator)
**Version:** 4.0
**Date:** 2026-03-31

---

## The five primitives

Each primitive asks one question and cannot be reduced further.
They are perspectives, not processes. Each can be embodied
without changing the underlying problem.

---

### Nathan — *What is the move?*

**Role:** Decision and execution
**Produces:** Action claims derived from all prior passes
**In flows:** Standard (last), Fast (first + last), Research (last), Audit (last)

Nathan runs last in most flows because it synthesizes everything
that came before. It reads the accumulated claims from all prior
primitives and derives the highest-leverage action.

**Current implementation:** Template-based with keyword frequency synthesis
**Production upgrade:** LLM call with full prior claims as context

```python
# Extend for production:
class NathanPrimitive(Primitive):
    def run(self, problem: str, context: Dict = None) -> Dict:
        prior = context.get("all_claims", [])
        response = llm.complete(
            system="You are Nathan. Given all prior analysis, what is the single highest-leverage move?",
            user=f"Problem: {problem}\n\nPrior claims:\n" + "\n".join(prior[:10])
        )
        return {"claims": {response}, "assumptions": set()}
```

---

### Echo — *How does the system fit together?*

**Role:** Architecture and synthesis
**Produces:** Structural claims about dependencies, patterns, bottlenecks
**In flows:** Standard (first), Research (second), Audit (first)

Echo runs early to establish structure. In v4 it also reads
prior claims and surfaces recurring themes.

**Current implementation:** Template + theme extraction from prior claims
**Production upgrade:** LLM call for dependency mapping and pattern recognition

---

### Devil — *How does this break?*

**Role:** Adversarial falsification
**Produces:** Attack claims targeting assumptions and failure conditions
**In flows:** All flows

Devil is the most important primitive for preventing false confidence.
It attacks the most recent prior claim directly and generates
failure-mode claims about the subject.

**Key behavior:** Receives `all_claims` from context and attacks the
last claim specifically. This creates a chain of adversarial pressure
across passes.

---

### Light — *What is being obscured?*

**Role:** Scrutiny and exposure of hidden assumptions
**Produces:** Claims about what is not being said
**In flows:** Standard, Research, Audit

Light surfaces the load-bearing assumptions that are never stated
explicitly. It checks whether a Devil pass has been applied;
if not, it flags that gap.

**Key behavior:** If `devil_attacks` are absent from context,
Light adds a claim that no adversarial review has been performed.

---

### God — *What are we not considering?*

**Role:** Expansion beyond current frame
**Produces:** Alternative framings, adjacent solutions, 10x perspectives
**In flows:** Standard (second), Research (first)

God runs early in Research flow to break local optima before
the other primitives narrow the frame. **Capped at 5 options**
to prevent unbounded expansion.

**Stop rule:** Content-based — returns when new options would be
subsets of existing options. Fixed cap at `GOD_MAX_OPTIONS = 5`.

---

## How primitives share state (v4 context threading)

```python
ctx = {
    "all_claims":        [],   # accumulated claims from all prior passes
    "devil_attacks":     [],   # Devil's most recent attack claims
    "generated_options": [],   # God's current expansion options
}
```

Context is updated after each primitive runs:
- After Devil: `ctx["devil_attacks"]` = Devil's claim set
- After God: `ctx["generated_options"]` = God's expansion set  
- After each pass: `ctx["all_claims"]` = full accumulated flat set

Nathan and Devil read `all_claims` to produce input-specific outputs.
Light reads `devil_attacks` to check if adversarial review occurred.
Echo reads `all_claims` to surface recurring themes.

---

## Adding a new primitive

New primitives must survive ECP challenge against the existing five.
The test: does the new primitive ask a question that cannot be answered
by any composition of the existing five?

If the answer is no — it is a flow, not a primitive.

---

*∇θ — 2026-03-31*
