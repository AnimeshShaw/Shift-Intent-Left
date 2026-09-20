# Documentation

| Document | Read it when you want to know |
|---|---|
| [`PROJECT_LOG.md`](PROJECT_LOG.md) | What has been done so far, and the reasoning behind each decision |
| [`ROADMAP.md`](ROADMAP.md) | What comes next, in what order, and what each step must produce |
| [`H2-PILOT-PROTOCOL.md`](H2-PILOT-PROTOCOL.md) | The pre-registration draft for the first empirical study (Hypothesis H2) |
| [`POSITIONING.md`](POSITIONING.md) | How Shift Intent Left differs from runtime guardrails, agent governance planes and agent-identity products, and where that argument is weak |
| [`SPEC-NOTES.md`](SPEC-NOTES.md) | Ambiguities and inconsistencies in the paper that implementing it exposed |
| [`PUBLISHING.md`](PUBLISHING.md) | How the paper and code are versioned, cited and published on Zenodo and GitHub |

## Where the paper is

The paper is **not** in this repository. Zenodo holds the paper of record:

**Concept DOI (always the latest version):** [10.5281/zenodo.22855795](https://doi.org/10.5281/zenodo.22855795)

## Code layout

```
src/sil/            reference enforcement point
  contract.py       the Intent Contract (immutable), digest
  model.py          Action and Decision
  globs.py          path normalisation and glob matching
  admissibility.py  adm(a, I): conditions C1-C6
  drift.py          Intent Drift, prefix series, artifact drift, weightings
  trace.py          hash-chained tamper-evident trace
  gateway.py        the mediating PEP: enforce / observe modes, step ceiling
schema/             JSON Schema for the Intent Contract
tools/              contract validator (schema + invariants)
examples/           valid and deliberately invalid contracts
tests/              57 tests, including reproduction of the paper's worked example
```

```bash
pip install -e ".[dev]"
python -m pytest -q
python tools/validate_contract.py examples/*.yaml
```
