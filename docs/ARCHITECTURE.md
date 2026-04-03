# Echo Convergence Protocol — Architecture

**Protocol**: ECS v1.1-hardened | **Authority**: echo-core

---

## Stack

- Python 3.8+
- Zero dependencies
- 21 adversarial test cases
- MIT license

---

## Components

- Five adversarial primitives (Devil Lens perspectives)
- Convergence measurement engine
- Truth Partition formatter
- Structured output validator (ECS v1.1-hardened)
- tools/validate_protocol.py

---

## Data Flow

Input → Five adversarial analyses → Convergence measurement → Truth Partition → ECS-formatted output

---

## Dependencies

**Depends on**: echo-core (ECS specification)  
**Depended on by**: art-of-proof, Agent-Zero, all repos using structured output

---

## Deployment

See `README.md` for deploy instructions.


---

## Ecosystem Connection

**Part of**: Echo Universe (45-repository sovereign AI and evidence ecosystem)  
**Operator**: Nathan Poinsette (∇θ) | onlyecho822-source  
**Ecosystem White Paper**: [`art-of-proof/docs/WHITE_PAPER_v3.md`](https://github.com/onlyecho822-source/art-of-proof/blob/main/docs/WHITE_PAPER_v3.md)  
**Governance Protocol**: ECS v1.1-hardened (`echo-core`)  
**Canonical Authority**: [`echo-core`](https://github.com/onlyecho822-source/echo-core)

*∇θ — chain sealed, truth preserved.*
