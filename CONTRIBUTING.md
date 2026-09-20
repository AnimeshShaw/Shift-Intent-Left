# Contributing

Shift Intent Left is a research project. Corrections, counter-arguments and
replication attempts are as welcome as code.

## What is most useful

1. **Refutation.** The paper states four hypotheses with explicit refutation
   criteria. Evidence that any of them is wrong is the single most valuable
   contribution you can make. Open an issue with your data.
2. **Contract patterns.** Real Intent Contracts for task classes not yet covered
   (test generation, migration, incident triage). Add them under `examples/`.
3. **Invariant checks.** The validator enforces four invariants that JSON Schema
   cannot express. If you find another that a real enforcement point needs,
   propose it.
4. **Enforcement implementations.** A tool gateway that evaluates admissibility
   against a contract is the obvious next artifact. Prototypes welcome.

## Before opening a pull request

```bash
pip install -r requirements.txt
python tools/validate_contract.py examples/*.yaml          # must pass
python tools/validate_contract.py examples/invalid/*.yaml  # must fail
```

CI runs exactly these checks.

## Adding an example contract

- Valid contracts go in `examples/`, invalid demonstrations in `examples/invalid/`.
- Every invalid example must carry a comment naming the invariant it violates.
- Keep contracts realistic. A contract nobody would actually approve teaches nothing.

## Terminology

Please use the terms as the paper defines them: an **Intent Contract** is the
signed declaration, an **Agency Budget** is the authority component within it,
**admissibility** is the per-action decision, and **Intent Drift** is the
severity-weighted measure of divergence. Consistent vocabulary is part of the
point of the project.
