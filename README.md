# Shift Intent Left

[![Paper DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22855795.svg)](https://doi.org/10.5281/zenodo.22855795)
[![Software DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22856519.svg)](https://doi.org/10.5281/zenodo.22856519)
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

The LaTeX source is not tracked here; Zenodo holds the canonical version of record.

## This repository

```text
src/sil/                          reference enforcement point (Python)
  admissibility.py                adm(a, I): the six conditions C1-C6
  drift.py                        Intent Drift, prefix series, artifact drift
  trace.py                        hash-chained, tamper-evident action trace
  gateway.py                      the mediating PEP: enforce / observe modes
schema/intent-contract.schema.json   JSON Schema for an Intent Contract
tools/validate_contract.py        schema + invariant validator
examples/                         valid contracts, and invalid/ ones that break an invariant on purpose
tests/                            57 tests, including the paper's own worked example
docs/                             project log, roadmap, H2 protocol, positioning, spec notes
```

## Quick start

```bash
git clone https://github.com/AnimeshShaw/Shift-Intent-Left.git
cd Shift-Intent-Left
pip install -e ".[dev]"

python tools/validate_contract.py examples/dependency-upgrade.yaml
python -m pytest -q
```

### Mediate an agent's actions

```python
from sil import Action, Gateway, TraceWriter, intent_drift, load_contract, read_trace

contract = load_contract("examples/dependency-upgrade.yaml")
gateway = Gateway(contract, TraceWriter("run.jsonl"), mode="enforce")

gateway.mediate(Action("shell", "execute", "pytest tests/payments"))   # allowed
gateway.mediate(Action("shell", "read", ".env"))                        # blocked: C1, C2, C5
gateway.mediate(Action("http", "connect", "paste.example.net"))         # blocked: C1, C4

records = [r for r in read_trace("run.jsonl") if r["type"] == "action"]
print(intent_drift((r["weight"], r["adm"]) for r in records))           # 13/14 = 0.9286
```

Every attempted action is recorded with its decision, including blocked ones; drift is measured
over **attempts**, so an agent that probes for secrets and is refused is still a detectable signal.

## The Intent Contract

`schema/intent-contract.schema.json` encodes the contract tuple from the paper:

```text
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

## Status

This is a **conceptual and architectural contribution** with a tested reference implementation. It
reports no empirical results yet; it specifies the experiments that would confirm or refute its
claims. The first empirical study (Hypothesis H2: is Intent Drift a usable detection signal under
indirect prompt injection?) is being **pre-registered before any data is collected**; see
[`docs/H2-PILOT-PROTOCOL.md`](docs/H2-PILOT-PROTOCOL.md) and [`docs/ROADMAP.md`](docs/ROADMAP.md).

What the code is and is not: the reference gateway mediates the calls routed through it. Complete
mediation of a real agent needs OS-level isolation beneath it, and the action trace is
tamper-*evident*, not tamper-proof. See [`docs/SPEC-NOTES.md`](docs/SPEC-NOTES.md).

Corrections, counter-arguments and replication attempts are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

## Citing

The **concept DOIs** below always resolve to the newest version, so citations stay current.

- **Paper:** [`10.5281/zenodo.22855795`](https://doi.org/10.5281/zenodo.22855795) (v1.0.0: [`10.5281/zenodo.22855796`](https://doi.org/10.5281/zenodo.22855796))
- **Software:** [`10.5281/zenodo.22856519`](https://doi.org/10.5281/zenodo.22856519) (v1.0.0: [`10.5281/zenodo.22856520`](https://doi.org/10.5281/zenodo.22856520))

```bibtex
@misc{shaw2026shiftintentleft,
  author    = {Shaw, Animesh},
  title     = {Shift Intent Left: Intent Contracts, Agency Budgets, and Drift
               Verification for Securing the Agentic Software Development Lifecycle},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.22855795},
  url       = {https://doi.org/10.5281/zenodo.22855795}
}
```

Author ORCID: [0009-0004-4308-5929](https://orcid.org/0009-0004-4308-5929)

## Licence

- Paper and documentation: [CC BY 4.0](LICENSE)
- Schema, examples and code: [MIT](LICENSE-CODE)
