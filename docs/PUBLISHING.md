# Publishing workflow

How the paper and the code are published, versioned and cited. Read this before touching Zenodo.

## The two records and four DOIs

Zenodo mints a **concept DOI** (always resolves to the newest version) and a **version DOI** (pins
one version) for every record. There are two records:

| Record | Concept DOI | v1.0.0 version DOI |
|---|---|---|
| **Paper** (preprint) | `10.5281/zenodo.22855795` | `10.5281/zenodo.22855796` |
| **Software** (GitHub release) | `10.5281/zenodo.22856519` | `10.5281/zenodo.22856520` |

**Cite the concept DOI** in talks, the CV, posts and other papers. It stays valid across versions.
Use a version DOI only when you need to pin exactly what was read.

## Rules

1. **Published Zenodo files are immutable.** The PDF cannot be swapped. Metadata (description,
   keywords, related identifiers) *can* be edited on a published record without a new version.
2. **`paper/` is frozen.** It holds the byte-identical published PDF and source. Never edit it.
   Its integrity is recorded in `paper/PUBLISHED.md` (`md5 41464fca2c3562ceb056fafac59a3281`).
3. **A new paper version is a *New version of the existing record*.** Open the paper record on
   Zenodo and use **New version**. Never make a fresh upload: that produces an unrelated DOI and
   breaks the concept-DOI chain and the priority date.
4. **The paper is not tracked in git.** `paper/` and `paper-v2/` are gitignored by design.
5. **No AI attribution** in commits, PRs or release notes.

## Publishing paper v2

1. Work only in `paper-v2/`. Track changes in `paper-v2/CHANGES.md`.
2. Put the paper **concept DOI** on the title page (v1 could not: DOIs are only known at
   publication).
3. Update the abstract, Status paragraph and Scope: v1 says "We do not report empirical results".
4. Build clean: 0 errors, 0 undefined references, no overfull boxes, citation keys all resolved.
5. Confirm every reference and every vendor claim is verified and dated.
6. Zenodo → paper record → **New version** → replace the PDF → set version `2.0.0` → publish.
7. Update `CITATION.cff` preferred-citation version.

## Publishing a software release

Zenodo archives every GitHub release automatically (the repository toggle is on).

```bash
# bump version in pyproject.toml and CITATION.cff first
python -m pytest -q
python tools/validate_contract.py examples/*.yaml
git tag -a v1.1.0 -m "..."
git push origin v1.1.0
gh release create v1.1.0 --title "..." --notes "..."
```

* `.zenodo.json` supplies the metadata Zenodo uses for new releases (it takes precedence over
  `CITATION.cff`). It declares the release as *supplement to* the paper's concept DOI.
* **Already-published release records** (v1.0.0) are not rebuilt from `.zenodo.json`. To link the
  v1.0.0 software record to the paper, edit its metadata once in the Zenodo web UI:
  *Related works → is supplement to → DOI `10.5281/zenodo.22855795` → Publication / Preprint*.
* Likewise, on the **paper** record, the *is supplemented by* link currently points at the GitHub
  URL. It can be upgraded to the software concept DOI `10.5281/zenodo.22856519` (resource type
  *Software*), which is a stronger DOI-to-DOI link.

## Pre-registration and datasets (H2 onward)

Each of these gets its **own** Zenodo record, deposited *before* it is needed:

| Record | When | Purpose |
|---|---|---|
| **H2 pre-registration** | before any evaluation run | timestamped protocol; see `H2-PILOT-PROTOCOL.md` |
| **H2 trace dataset** | after the run | all hash-chained traces, so the analysis is reproducible |
| **Paper v2** | after analysis | new version of the paper record |

Also register the protocol on **OSF Registries** for a formal, citable preregistration.

## Venue submission (later)

Zenodo v2 is the **complete, extended record** (no page limit). A venue submission is a **derived,
abridged** version that cites the Zenodo DOI ("An extended version is available at …"). Check the
target venue's preprint and double-blind policies before promoting the preprint during review.
Venues and their fit are in [`ROADMAP.md`](ROADMAP.md).

## Metadata checklist for any Zenodo upload

Resource type · title · publication date · authors with ORCID · description · CC BY 4.0 licence ·
keywords · version · related works (URL or DOI, with correct relation and resource type) ·
repository URL. Leave funding, journal, imprint, thesis and conference fields empty unless they
genuinely apply.
