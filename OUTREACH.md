# OUTREACH — Who should use this and why

**Date:** 2026-03-31

---

## The problem this solves

Most reasoning tools produce confident-sounding outputs.
They do not tell you when they are wrong.
They do not surface what they are not considering.
They do not flag when convergence is false.

echo-ecp-fullauto does the opposite.
It is designed to find the gaps, not hide them.

---

## Who this is for

### Researchers and academics
Running a problem through five adversarial perspectives
and measuring convergence is the kind of structured analysis
that peer review demands. The Truth Partition format maps
directly to how good papers structure claims, evidence,
uncertainty, failure modes, and conclusions.

Use case: run your hypothesis through the Research flow
before writing the paper. The DeceptionIndicating claims
are the objections reviewers will raise.

### Developers and engineers
Every architectural decision has assumptions that will break
under load. The Devil primitive finds them. The Light primitive
finds the ones you were not aware you were making.

Use case: before committing to a design, run it through the
Audit flow. The output gives you a structured list of what
needs to be validated before shipping.

### Strategy and product teams
The Standard flow is built for complex decisions with unclear
right answers. It surfaces what you are not considering (God),
attacks your core assumptions (Devil), and derives the
highest-leverage action from everything it found (Nathan).

Use case: before a major product decision, run the framing
through the engine. The UnresolvedDirectional claims are the
things worth a second meeting.

### AI/ML practitioners
This is a working implementation of a multi-primitive
reasoning architecture with convergence detection and
false convergence prevention. The code is clean, tested,
and designed for LLM integration at the primitive level.

Use case: study the architecture. Use it as a foundation
for a production reasoning system. The extension points
are documented in `docs/PRIMITIVES.md`.

---

## What makes this different

| Property | Most tools | echo-ecp-fullauto |
|----------|-----------|-------------------|
| Confidence signaling | Outputs sound certain | Labels uncertainty explicitly |
| Assumption handling | Hidden | Surfaced and flagged |
| Convergence | Not measured | Measured + false conv detected |
| Output structure | Free-form | Five required fields, validated |
| Stub transparency | Mixed with real behavior | All stubs clearly marked |
| Test coverage | Varies | 21 tests, 3 validation criteria |

---

## How to reach us

GitHub: `github.com/onlyecho822-source/echo-ecp-fullauto`
Issues: open an issue for bugs, questions, or contribution proposals
Built by: Nathan Poinsette — Echo Universe ecosystem

---

## If you use this

Star the repo. Open an issue with your use case.
The most useful contributions right now are real-world
edge cases that expose heuristic limits.

---

*∇θ — 2026-03-31*
