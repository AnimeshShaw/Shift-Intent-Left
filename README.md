# Shift Intent Left

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22855795.svg)](https://doi.org/10.5281/zenodo.22855795)
[![validate](https://github.com/AnimeshShaw/Shift-Intent-Left/actions/workflows/validate.yml/badge.svg)](https://github.com/AnimeshShaw/Shift-Intent-Left/actions/workflows/validate.yml)
[![License: CC BY 4.0](https://img.shields.io/badge/Paper-CC%20BY%204.0-blue.svg)](LICENSE)
[![License: MIT](https://img.shields.io/badge/Code-MIT-green.svg)](LICENSE-CODE)

**Securing the agentic software development lifecycle by making *intent* the first securable artifact.**

Shift left moved security toward the earliest artifact of the SDLC: source code. Autonomous coding
agents break that premise. An agent with a shell, a package manager, credentials and tool connectors
takes security-relevant actions — installing dependencies, reading secrets, calling external services —
**before any diff exists** for a scanner or reviewer to inspect. Its behaviour is steered by
natural-language context that conventional pipelines neither version nor verify.

**Shift Intent Left (SIL)** treats the declared intent as a signed, bounded, verifiable object:
declared before execution, compiled into enforceable authority, protected from contaminated context,
checked against the action trace afterwards, and improved from observed drift.

> **Shift left asks** *"what is in the code?"* as early as possible.
> **Shift Intent Left asks** *"what was the agent authorised to do?"* — before it acts.

---

## The paper

**[Read the preprint on Zenodo →](https://doi.org/10.5281/zenodo.22855795)**

| | |
|---|---|
| **Formal model** | Intent Contracts, Agency Budgets, an admissibility predicate, a severity-weighted Intent Drift metric, and a refinement order for delegation |
| **Lifecycle** | Five stages — Declare, Budget, Sanitise, Verify, Learn — with a reference architecture |
| **Threat model** | Four adversary classes (including the *under-specified principal*), explicit trust boundaries, four adversary goals |
| **Alignment** | NIST SSDF, OWASP Top 10 for LLM Applications, OWASP Top 10 for Agentic Applications (ASI01–ASI10), NIST AI RMF, Zero Trust, in-toto/SLSA |
| **Research agenda** | Four falsifiable hypotheses, each with a full experimental design and refutation criteria |
| **Appendices** | Notation primer, the delegation proof step by step, a fully worked example, common questions |

The appendices assume no background in formal methods and explain every symbol used.
The LaTeX source is not tracked here; Zenodo holds the canonical version of record.

## This repository

```
schema/
  intent-contract.schema.json   # JSON Schema for an Intent Contract
examples/
  dependency-upgrade.yaml       # medium-tier: the worked example from the paper
  iac-change.yaml               # high-tier: infrastructure change
  invalid/                      # contracts that violate an invariant, on purpose
tools/
  validate_contract.py          # schema + invariant validator
```

## Quick start

```bash
git clone https://github.com/AnimeshShaw/Shift-Intent-Left.git
cd Shift-Intent-Left
pip install -r requirements.txt

python tools/validate_contract.py examples/dependency-upgrade.yaml
```

```
OK   examples/dependency-upgrade.yaml

1/1 contract(s) valid
```

## The Intent Contract

`schema/intent-contract.schema.json` encodes the contract tuple from the paper:

```
I = (G, S, Θ, Δ, E, W, Π, X, β, σ)
```

| Field | Symbol | Meaning |
|---|---|---|
| `goal` | *G* | What the agent should achieve (natural language, not machine-checkable) |
| `scope.read` | *S* | What it may read |
| `scope.write` | *W* | What it may modify |
| `scope.protected` | *Π* | What it must never modify, overriding `write` |
| `scope.data_classes` | *Δ* | Which classifications of data it may touch |
| `tools` | *Θ* | Permitted tool/operation pairs |
| `egress` | *E* | Permitted network destinations, deny-by-default |
| `exit_criteria` | *X* | Machine-checkable definition of done |
| `budget` | *β* | Credentials, step ceiling, human-confirmation predicates, risk tier |
| `approval` | *σ* | Who approved it |

### Invariants beyond the schema

JSON Schema cannot express these, so `tools/validate_contract.py` checks them:

| | Invariant | Why |
|---|---|---|
| **I1** | `write` ⊆ `read` | An agent must not modify what it cannot read |
| **I2** | `protected` overrides `write` | A protected path is never writable, however broad `write` is |
| **I3** | Egress is deny-by-default | A wildcard destination defeats the exfiltration control |
| **I4** | Credentials are bounded | Every credential carries a finite TTL |

See `examples/invalid/` for contracts that trip them.

## Status

This is a **conceptual and architectural contribution**. It reports no empirical results; it specifies
the experiments that would confirm or refute its claims. The four hypotheses in the paper are stated
so they can be shown wrong, and each has stated refutation criteria.

Planned next: an empirical evaluation of Hypothesis H2 (Intent Drift as a detection signal under
indirect prompt injection), to be published as a new version of the Zenodo record.

Corrections, counter-arguments and replication attempts are all welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

## Citing

Cite the **concept DOI** below. It always resolves to the newest version, so citations stay current when a revised version is published.

- Concept DOI (all versions): [`10.5281/zenodo.22855795`](https://doi.org/10.5281/zenodo.22855795)
- Version DOI (v1.0.0 only): [`10.5281/zenodo.22855796`](https://doi.org/10.5281/zenodo.22855796)


```bibtex
@misc{shaw2026shiftintentleft,
  author       = {Shaw, Animesh},
  title        = {Shift Intent Left: Intent Contracts, Agency Budgets, and Drift
                  Verification for Securing the Agentic Software Development Lifecycle},
  year         = {2026},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.22855795},
  url          = {https://doi.org/10.5281/zenodo.22855795}
}
```

Author ORCID: [0009-0004-4308-5929](https://orcid.org/0009-0004-4308-5929)

## Licence

- Paper and documentation: [CC BY 4.0](LICENSE)
- Schema, examples and tooling: [MIT](LICENSE-CODE)
