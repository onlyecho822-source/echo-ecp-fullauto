# Echo Compression Stack v1.1-hardened

**Canonical home:** `onlyecho822-source/echo-ecp-fullauto`  
**Status:** PRODUCTION CANDIDATE  
**Supersedes:** v1.0 (Type field), v1.1-final (pre-hardening)

---

## 1. Scope & Level

| Value | Meaning |
|-------|---------|
| `PUBLIC` | Open, citable data |
| `CONTEXT-LOCKED` | Session-bound, not public |
| `NON-PUBLIC` | Private, do not distribute |

| Level | Use |
|-------|-----|
| L0 | Casual — see §8 for hard exclusions |
| L1 | Standard protocol block |
| L2 | Block + one explanatory paragraph |
| L3 | Block + full evidence chain |

---

## 2. Required Fields (fixed order)

```
Scope:
Truth:
Mode:
Confidence:
Decision:
Level:
Claim:
Risk:
Action:
Test:
Audit:
Why not higher:
```

---

## 3. Truth Values — Evidence Standards

| Symbol | Meaning | Requires |
|--------|---------|----------|
| `✔` | Verified / empirical | Reproducible evidence (sensor data, logs, citations) |
| `≈` | Inferred / modeled | Documented model or explicit reasoning chain |
| `∼` | Speculative / unverified | Clear caveat (e.g., "preliminary", "untested hypothesis") |

**Conflict resolution:** If two interpreters disagree on Truth or Decision,
escalate to L2/L3 with explicit evidence citation before acting.

---

## 4. Mode Values

| Symbol | Meaning | Constraint |
|--------|---------|-----------|
| `⚙` | Build / implement / fix | — |
| `⚖` | Compare | Claim must contain explicit comparator: "vs", "versus", "greater than", "less than", "faster than", "compared to", "relative to" |
| `Δ` | State change over time | Claim/Risk must contain: numeric delta, directional word (increased/decreased/rose/fell/emerged/shifted), or before/after relation, or timestamp pair |
| `🧪` | Test / validation | Test: field must be non-trivial |
| `🔍` | Audit / adversarial review | — |

---

## 5. Decision Values

| Value | Meaning |
|-------|---------|
| `ACT` | Act now |
| `INFO` | Informational only |
| `CHK` | Verify first |
| `HOLD` | Insufficient confidence |
| `ESC` | Escalate — high stakes |

---

## 6. Confidence Bands

| Range | Status | Action |
|-------|--------|--------|
| 95–100% | Operationally stable | Safe for direct use |
| 85–94% | Strong | Use, monitor |
| 70–84% | Moderate | Validate before operational use |
| 50–69% | Hypothesis | Do not rely operationally |
| <50% | Unstable | Do not use |

`Why not higher:` must state a concrete limitation — never "unknown".  
If Confidence > 95% and `Why not higher: unknown` → **validator FAIL**.

---

## 7. Compatibility & Enforcement Rules

| Condition | Action |
|-----------|--------|
| `Truth: ∼` + `Confidence > 85%` | WARN — speculative claim overconfident |
| `Truth: ∼` + `Decision: ACT` | WARN — exploratory action, label clearly |
| `Mode: 🧪` + `Test:` empty or trivial | FAIL |
| `Mode: ⚖` + Claim missing explicit comparator | WARN |
| `Mode: Δ` + no numeric delta / directional word / before-after | WARN |
| `Confidence > 95%` + `Why not higher: unknown/none/n/a` | FAIL |
| `Risk: none` without justification | WARN |
| `Level: L0` + `Decision: ACT` or `ESC` | **FATAL** |
| `Level: L0` + high-confidence operational claim | WARN |
| Unknown symbol in `Truth:/Mode:/Decision:/Level:` | **FATAL** |

---

## 8. L0 Rules

**Allowed only when ALL are true:**
- Low stakes
- No ambiguity
- No archival requirement
- No multi-step reasoning

**NOT allowed for:**
- Any `Decision: ACT` or `ESC`
- Legal or evidence conclusions
- Cross-domain anomaly decisions
- Evidence weighting
- Safety, financial, or operational claims

**Allowed format:** `Truth | Claim | optional Risk`  
**Example:** `✔ | Agreed. Δ locked. | Risk: low`

---

## 9. Audit Field — Constrained Forms

`Audit:` must begin with one of:
- `Assumes:`
- `Breaks if:`
- `Could be wrong because:`
- `Need to falsify:`

---

## 10. Drift Control (Governance)

- One symbol = one meaning. No exceptions.
- One field = one purpose. No exceptions.
- No new symbols without updating this glossary and bumping version.
- Validator rejects unknown symbols in all controlled fields.
- Examples override vague interpretation.
- When uncertain, expand to L2 or L3.
- Version changes require migration guide and CHANGELOG entry.

---

## 11. Interpreter's Guide

| Symbol | What it requires from the writer |
|--------|----------------------------------|
| `✔` | Can you point to reproducible evidence? If not, use `≈`. |
| `≈` | Can you describe the model or reasoning? If not, use `∼`. |
| `∼` | Is a caveat present? If not, validator will warn. |
| `Δ` | Is there a time element or change direction? If not, use `⚖`. |
| `⚖` | Are there two named comparands with a comparator? If not, rephrase. |

**Minimal valid block quality floor:**
- Claim: at least one concrete subject + predicate
- Risk: describes a failure condition (not just "low")
- Action: executable
- Test: falsifiable

---

## 12. Version History

| Version | Change |
|---------|--------|
| v1.0 | Original — single `Type:` field |
| v1.1-final | Split `Truth:` / `Mode:`, added `Level:`, `Why not higher:` |
| v1.1-hardened | Interpreter's Guide, compatibility table, L0 FATAL enforcement, unknown symbol rejection, Δ/⚖ heuristics strengthened, --explain/--suggest in validator |

---

*∇θ — chain sealed, truth preserved.*
