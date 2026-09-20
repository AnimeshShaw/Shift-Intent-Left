# Project log

A record of what has been done and why. Dates are 2026.

## Identifiers

| | |
|---|---|
| Author | Animesh Shaw, Independent Researcher |
| ORCID | [0009-0004-4308-5929](https://orcid.org/0009-0004-4308-5929) |
| Repository | https://github.com/AnimeshShaw/Shift-Intent-Left |
| **Paper**: concept DOI (always the latest version) | `10.5281/zenodo.22855795` |
| **Paper**: v1.0.0 version DOI | `10.5281/zenodo.22855796`: https://zenodo.org/records/22855796 |
| **Software**: concept DOI (always the latest release) | `10.5281/zenodo.22856519` |
| **Software**: v1.0.0 version DOI | `10.5281/zenodo.22856520` |
| Published | 2026-09-20 |

## Timeline

### 1. The paper (drafted, reviewed, published)

The manuscript introduces **Shift Intent Left (SIL)**: in an agentic SDLC the earliest securable
artifact is no longer code but the *intent* handed to an agent. It contributes a principle, a
formal model (Intent Contracts, Agency Budgets, admissibility, Intent Drift, refinement), a
five-stage lifecycle (Declare, Budget, Sanitise, Verify, Learn), a threat model, an alignment with
existing frameworks, and four falsifiable hypotheses.

**Editorial and formatting work.** Consistent title and terminology; ORCID and affiliation
(Independent Researcher); removal of placeholder text; theorem styles; caption spacing; ragged-right
table columns to stop bad hyphenation; a listing fix; tables and figures checked visually after
compilation.

**Reference verification.** All 39 references were checked against primary sources. Real
corrections found:

* *Progent* had been retitled ("Securing AI Agents with Privilege Control").
* *AgentSpec* is now published at **ICSE 2026**, not only arXiv.
* One OWASP entry conflated two separate documents; it was split into *Agentic AI: Threats and
  Mitigations* (Feb 2025) and the *OWASP Top 10 for Agentic Applications for 2026* (Dec 2025).
* Four sources cited to organisations had named authors.
* Every "et al." in the bibliography was expanded to full author lists; dates and URLs added.
* The bibliography was reordered alphabetically by displayed author.

**Content improvements.**

* The paper was mapped to **OWASP ASI01-ASI10**.
* A dedicated **Shift Intent Left Principle** section, with three tenets and a comparison with
  shift left.
* **Threat model** rebuilt: explicit trust boundaries, adversary goals G1-G4, per-adversary
  capabilities and limits, and a diagram.
* **Formal model** rewritten so every symbol is explained after each formula, with a notation
  table, worked admissibility decisions, and a numeric drift example.
* **Research agenda**: full experimental designs for **all four** hypotheses (previously only H1),
  a shared infrastructure section, and refutation criteria for H4.
* A limitation stated explicitly: **step ceilings do not compose** across a delegation tree.
* A missing definition (`Ops`) and the risk-tier ordering were added.

### 2. Decision: one document, not two

A standalone "formal model explained" companion was written and then **merged into the paper as
Appendices A-E**.

*Why:* after the rewrite the two documents overlapped substantially. Two Zenodo records sharing a
large fraction of text look like salami-slicing, split citations across two DOIs, and weaken a
priority claim. One complete record is stronger. The standalone files were archived, not deleted.

### 3. Publication

* **Zenodo** preprint published as v1.0.0 (CC BY 4.0), with the GitHub repository linked as
  *is supplemented by → Software*.
* **GitHub** repository created and pushed. Zenodo's GitHub integration enabled; release `v1.0.0`
  archived as the software record.
* **Concept vs version DOIs.** Zenodo mints both for every record. The concept DOI is the one to
  cite: it always resolves to the newest version. Repository metadata uses the concept DOIs.

### 4. Repository hygiene decisions

* **The paper is deliberately not in the repository.** The repository holds only the machine-
  checkable artifacts. `paper/` and `paper-v2/` are gitignored; Zenodo holds the paper of record.
* **Git history was rebuilt from scratch** before the first push, because the paper had already
  been committed locally and gitignoring it afterwards would have left it in history.
* **`paper/` is frozen** and verified byte-identical to the published PDF (`md5 41464fca…`). All
  further paper work happens in `paper-v2/`.
* **No AI attribution** in commits, release notes, or any repository artifact (standing rule).
* `.gitattributes` forces LF for scripts so `build.sh` does not break on Linux/macOS.

### 5. Code

| Component | What it is |
|---|---|
| `schema/intent-contract.schema.json` | JSON Schema for the contract tuple `I = (G, S, Θ, Δ, E, W, Π, X, β, σ)` |
| `tools/validate_contract.py` | Schema validation plus four invariants JSON Schema cannot express: **I1** `write ⊆ read`, **I2** `protected` overrides `write`, **I3** egress deny-by-default, **I4** bounded credential TTLs |
| `examples/` | medium-tier dependency upgrade, high-tier IaC change, and `invalid/` contracts that each violate an invariant on purpose |
| `src/sil/` | **Reference enforcement point**: typed admissibility (C1-C6), severity-weighted Intent Drift with prefix series, artifact drift, hash-chained tamper-evident trace, and the mediating `Gateway` with `enforce` and `observe` modes and a step ceiling |
| `tests/` | 57 tests, including reproduction of the paper's own worked example (`D = 22/31`) |
| `.github/workflows/validate.yml` | CI: schema, examples (valid pass, invalid fail), tests, metadata |

**The test suite was mutation-tested**, not just run. Five deliberate bugs were injected (drop
the protected-overrides-writable rule; suffix-match egress; count only executed actions in drift;
anchor the protected set; unanchor the writable set). The first suite caught three. Two survived,
which exposed real gaps (nothing tested nested-path glob semantics), and tests were added until all
five were killed.

**Implementation findings.** Building it exposed ambiguities in the paper (typed resources, bare
glob semantics, undefined predicate "matching", the role of the step ceiling) and two
inconsistencies in the frozen v1. All are catalogued in [`SPEC-NOTES.md`](SPEC-NOTES.md).

### 5b. Critical analysis

A critique of how SIL differs from runtime guardrails, agent governance planes, and agent
identity products is in [`POSITIONING.md`](POSITIONING.md). Headline: the components are not new;
the defensible contribution is per-task purpose-binding and the drift-verification loop, and it
should be framed as a specification layer that compiles into existing enforcement points.

### 6. Strategy decisions

* **Priority first, credibility second.** A Zenodo DOI establishes *priority* (a timestamp). It
  does not establish *credibility*, which needs peer review or evidence.
* **Distribution deferred.** No public promotion until real results exist, so that anyone who
  looks back finds evidence and not only a concept.
* **Staged evidence.** v2 leads with the H2 pilot, then H4, then H1; H3 (human subjects) is
  separate. See [`ROADMAP.md`](ROADMAP.md).
* **Pre-register before running.** The H2 protocol is drafted in
  [`H2-PILOT-PROTOCOL.md`](H2-PILOT-PROTOCOL.md).
