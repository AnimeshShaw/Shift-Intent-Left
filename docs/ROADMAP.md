# Roadmap

What is done, what is next, and what each step must produce before the next begins. Time
estimates are **rough, part-time guesses** and exist to expose ordering and size, not to promise
dates.

## Guiding principles

1. **Evidence before distribution.** No public promotion until real results exist.
2. **Pre-register, then run.** Protocols are frozen and deposited before data is collected.
3. **Stage the evidence.** Four hypotheses are four different projects; ship them in order of
   value-per-cost rather than waiting for all of them.
4. **Publish negative results.** The hypotheses are stated with refutation criteria; a refutation
   is a finding, not a failure.
5. **One record per artifact, versioned.** New paper versions are *New version* on the existing
   Zenodo record, never a fresh upload.

## Status

| Phase | Work | State |
|---|---|---|
| **0** | Paper v1, schema, validator, examples, repo, DOIs | **Done** (published 2026-09-20) |
| **1** | **H2 pilot**: drift as a detection signal | **In progress**: core built and tested; harness and study not started |
| **2** | **H4**: delegation containment | Next |
| **3** | **H1**: specification dominance, with comparison arms | Later |
| **4** | **H3**: approval cost (human subjects) | Separate; needs an ethics route |
| **5** | Paper v2 and venue submission | After Phase 1 (and 2) |
| **6** | Distribution and community | After Phase 1 results |

## Phase 0: done

See [`PROJECT_LOG.md`](PROJECT_LOG.md).

## Phase 1: H2 pilot

**Goal:** determine whether Intent Drift `D` separates compromised runs from benign ones at a
useful operating point, whether it fires before an attack would succeed, and whether severity
weighting earns its complexity. **Design:** [`H2-PILOT-PROTOCOL.md`](H2-PILOT-PROTOCOL.md).

| Step | Deliverable | State |
|---|---|---|
| 1.1 | Model-independent core: admissibility, drift, trace, gateway. **57 tests; reproduces the paper's `22/31`; mutation-tested.** | **Done** |
| 1.2 | Minimal agent loop with tool implementations, every call routed through the gateway; Docker sandbox; Ollama client | To do |
| 1.3 | 30 task repositories (10 per family) with pytest suites and frozen contracts; 6 development / 24 evaluation | To do |
| 1.4 | Attack corpus (24 cells + adaptive in-scope stratum), canary secrets, attacker sink, filesystem audit hook | To do |
| 1.5 | Baselines, including the pre-committed injection scanner (B3) | To do |
| 1.6 | **Development runs**: measure compliance rate, calibrate the threshold, fix run counts | To do |
| 1.7 | **Freeze and register**: resolve all `[OPEN]` items, deposit on OSF Registries and Zenodo | To do |
| 1.8 | **Evaluation runs** (roughly hours per model per 200 runs on local hardware) | To do |
| 1.9 | Analysis scripts (cluster bootstrap AUC, lead time, paired differences); deposit traces as a dataset | To do |
| 1.10 | Write up results, including any refutation | To do |

**Exit criteria:** a registered protocol, a published trace dataset, and pre-specified criteria
applied without modification. **Rough size:** 6-10 weeks part-time, dominated by 1.3 and 1.4
(authoring realistic tasks and attacks), not by compute.

**Decisions still open** (tracked as `[OPEN]` in the protocol): final model list; whether to add
hosted models as a replication arm; the run-count figures; the success thresholds.

**Why local models first:** zero API cost, pinned weights, and anyone can reproduce the study. The
cost is that 7B-12B models are weaker agents and may be more injection-susceptible than frontier
models; the paper must say so and a hosted replication is the remedy.

## Phase 2: H4, delegation containment

**Goal:** show that enforcing the refinement order on sub-agent contracts reduces the blast radius
of one compromised sub-agent, without breaking legitimate work.

* Reuses the Phase 1 harness, so most of the cost is already paid.
* The compromised worker is a **substituted policy**, not a prompt-injected LLM, so the measurement
  is about *containment*, not *susceptibility*.
* Compare **flat** shared authority against **refined** per-sub-agent contracts; report blast
  radius **and** task success (a containment win bought with broken functionality is a negative
  result).
* Needs a refinement checker (`I' ⊑ I`) in `src/sil/`: not yet implemented.
* Must address the limitation the paper states openly: **step ceilings do not compose**, so
  aggregate autonomy across a tree is not bounded by refinement alone. A budget debited across the
  tree is the candidate remedy and is itself worth evaluating.

**Rough size:** 3-5 weeks after Phase 1.

## Phase 3: H1, specification dominance

The 27-cell factorial (model × intent precision × Agency Budget). Higher cost: real model spend
and many runs.

**Add comparison arms** so the question *"isn't a guardrail enough?"* is answered by measurement
(see [`POSITIONING.md`](POSITIONING.md) §5):

| Arm | Authority | Detection |
|---|---|---|
| G | broad standing | injection classifier |
| I | agent-level least privilege | none |
| C | task-level contract | none |
| C+G | task-level contract | classifier |

Prediction, stated in advance: attack success is lowest for `C` and `C+G`; if `G` matched `C`,
SIL's marginal value would be small and the paper should say so.

## Phase 4: H3, approval cost

A user study (about 40 practising engineers, within-subjects). It is a different kind of project:

* **Ethics.** Human subjects require ethics-board approval. As an independent researcher there is
  no institutional board, so this needs either a **partner institution**, a properly scoped exempt
  design, or reframing as a practitioner survey. **Decide the route before designing the study.**
* It tests the central adoption risk: does approval stay a real control under time pressure, or
  degrade into click-through? The vigilance probe (deliberately over-broad drafts) measures this.
* Likely **its own paper**, with its own pre-registration.

## Phase 5: Paper v2 and venues

**Paper v2** (a *New version* of the existing record) adds Phase 1 (and 2) results, the concept DOI
on the title page, a "SIL and commercial agent security" subsection, the fixes catalogued in
[`SPEC-NOTES.md`](SPEC-NOTES.md), and updated abstract and Status.

**Venue submission** is a derived, abridged version (roughly 8-12 pages) citing the Zenodo DOI.
Fit, in order for the stated goal (build standing as a practitioner-researcher with technical
depth):

| Venue | Why | Note |
|---|---|---|
| **IEEE Security & Privacy Magazine** | peer reviewed, IEEE, practitioner reach | short format |
| **IEEE SecDev** | practitioner-facing, receptive to frameworks | |
| **ICSE NIER / FSE IVR** | designed for new ideas with early results | short |
| **ACM AISec** (with CCS) | squarely on topic | workshop |
| **Elsevier Computers & Security** | Scopus/SCIE-indexed journal | for institutional credit |
| Top security conferences (S&P, USENIX Sec, CCS, NDSS) | highest visibility | **will not accept without empirical results**; Phase 1-3 are what make this reachable |

Page limits usually apply to the body only, with references and appendices excluded, but reviewers
are **not obliged to read appendices**: anything load-bearing must survive in the body. Check the
live call for papers each year.

If cutting to venue length: merge Background into Related Work; fold Motivation into the
Introduction; drop the Adoption Maturity Model (a candidate practitioner article or follow-up);
compress the research agenda to hypotheses plus one design table; keep the formal definitions and a
single worked example.

## Phase 6: Distribution and community (after Phase 1 results)

* Lead with the *idea* and the *evidence*, linking the concept DOI.
* **OWASP GenAI Security Project / Agentic Security Initiative**: contribute the SIL mapping onto
  ASI01-ASI10 and the pre-registered evaluation. This is the highest-leverage community step.
* Practitioner write-up; talk proposals.
* Release the H2 dataset and harness so others can attempt to refute the result.

## Risks

| Risk | Consequence | Mitigation |
|---|---|---|
| H2 refuted | v2 reports a negative result | Registered criteria; publish it; refine the metric |
| Small local models unrepresentative | limited generalisation | state it; hosted replication arm |
| Realistic task/attack authoring is slow | Phase 1 stalls | start small, freeze early, grow in later versions |
| A vendor ships per-task contracts first | novelty erodes | timestamped priority; publish evidence quickly; position as a spec layer |
| Mediation completeness not achievable in practice | guarantee weaker than claimed | scope claims; H2 harness has it by construction |
| Reviewers see "least privilege relabelled" | rejection on novelty | concede the components; claim the composition; show evidence |
| No IRB route for H3 | H3 blocked | decide the route before design |
