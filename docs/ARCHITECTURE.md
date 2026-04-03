# echo-ecp-fullauto — Architecture

**Pattern**: Five adversarial agents → convergence detector → Truth Partition output

---

## Core Loop

```python
def run_ecp(claim, max_iterations=10):
    perspectives = [devil, steelman, empiricist, systems, pragmatist]
    history = []
    
    for i in range(max_iterations):
        round_outputs = [p.analyze(claim, history) for p in perspectives]
        if convergence_detected(round_outputs, history):
            break
        history.append(round_outputs)
    
    return TruthPartition(
        verified=extract_empirical(history),
        inferred=extract_inferred(history),
        speculative=extract_speculative(history)
    )
```

---

## Zero Dependencies

No pip packages. No API calls. No environment variables. The entire engine runs on Python standard library.

This is intentional: zero dependencies = zero attack surface, zero configuration, zero cost, maximum portability.

---

## Test Suite

21 tests covering:
- Each adversarial primitive independently
- Convergence detection at various iteration counts
- Truth Partition structure validation
- ECS output format compliance
- Edge cases: empty input, contradictory evidence, single-source claims

*∇θ — chain sealed, truth preserved.*
