# Specification notes

Implementing the model as running code exposed places where the paper's formalism is **ambiguous or
under-specified**. They are recorded here because they are the most honest kind of finding:
the specification did not survive contact with an implementation unchanged. Each one is a
candidate fix for v2 of the paper. v1 is frozen and is not edited.

## A. Decisions the implementation had to make

### A1. Resources are typed
The paper treats `R` as one flat set and applies "`r ∈ S`" to every action. That cannot hold: an
egress host is not a path in the readable scope, and a package name is not a writable file.
The implementation types each resource as **path / host / package / command** and applies each
condition only where it is meaningful:

| Condition | Applies to |
|---|---|
| C1 `(tool, op) ∈ Θ` | all actions |
| C2 target in `S` | path |
| C3 write in `W`, outside `Π` | path (`write`) |
| C4 connect target in `E` | host |
| C5 `class(r) ∈ Δ` | path |
| C6 confirmation | all actions carrying a matching tag |

*v2 action:* state typed resources in Definition 1 and restate Definition 4 per kind.

### A2. Bare glob patterns: anchored vs anywhere
A pattern with no `/` (for example `requirements*.txt` or `.env*`) is ambiguous.

* In a **permitting** set (`read`, `write`) it is **anchored to the workspace root**.
  Otherwise `requirements*.txt` in `write` would silently authorise `tests/deep/requirements.txt`.
* In a **restricting** set (`protected`, secret classifier) it matches **at any depth**, so
  `.env*` catches `services/payments/.env.local`.

Rule: *permitting sets err narrow, restricting sets err broad.* Both directions are covered by
mutation-tested unit tests.

### A3. Path normalisation
Paths are normalised (`.`, `..`, duplicate separators, backslashes). Anything absolute,
drive-lettered, or escaping the workspace after normalisation is in **no** permitting set.
**Not handled:** symbolic links, hard links, case-insensitive filesystems. These are mediation
gaps (see B1).

### A4. `execute` has no path target
`(shell, execute, "pytest tests/payments")`: what is `r`? The implementation treats the command as
the target and checks it against the tool's `allow_cmds` allowlist (whole-argument prefix match)
under C1. It does **not** evaluate C2/C3 for `execute`, because the paths a command touches are
not knowable from its string.

### A5. Installing implies a network hop
`install` is checked against the tool's `registries` under C1. The network connection to the
registry is a second, separate event that the *network layer* must enforce against `E`. The paper
does not say whether one action is counted or two.

### A6. "`a` matches a predicate in `H`"
"Matches" is undefined in the paper. The implementation has actions carry **tags** naming the
confirmation predicates they fall under, and a separate `confirmation` flag. *Something* must
classify a raw tool call into a predicate such as `install_new_top_level_package`; that classifier
is a real component the architecture does not currently list.

### A7. The step ceiling is not part of admissibility
`n_max` bounds autonomy but is not one of the six conditions, so a call blocked *only* by the
ceiling is recorded (`reason: step_ceiling`) but is **not** counted as drift. The paper is
silent; this is the reading that keeps `D` a measure of *contract violation*.

### A8. The weight function
The paper says only that `w` should be "higher for writes to protected resources, egress and
credential use". The implementation ships three weightings:

| Weighting | protected write | secret access | egress | write / install | other |
|---|---|---|---|---|---|
| `unit` | 1 | 1 | 1 | 1 | 1 |
| `severity` (default) | 9 | 8 | 5 | 2 | 1 |
| `steep` | 30 | 20 | 10 | 3 | 1 |

`severity` reproduces the worked example in Appendix D exactly (see C1).

### A9. Data classification
`class(r)` is deployment-specific. The default classifier marks `.env*`, `*.pem`, `*.key`,
`id_rsa*`, `**/secrets/**`, `**/.ssh/**`, `**/credentials*` as `secrets`, at any depth, and
everything else as `source_code`. A real deployment needs its own.

## B. Structural limits the implementation makes visible

### B1. Mediation completeness is the whole guarantee
Every property in the paper assumes P1 (all side-effecting calls are mediated). A Python gateway
mediates only calls routed through it. Anything a permitted `execute` does internally (a
`pytest` run that writes files or opens sockets) is **outside** the gateway's view. Real
deployments need OS-level isolation underneath. The H2 harness gets P1 by construction (a custom
agent loop with no other action space), which is why it does not use an off-the-shelf scaffold.

### B2. The trace is tamper-*evident*, not tamper-proof
The action trace is hash-chained, so editing, deleting or reordering a record is detected
(tested). A party with write access to the file can still delete the *whole* file, or rewrite the
chain end to end. The paper's assumption ("the action log is append-only") is an operational
property of the deployment, not something a library can provide.

### B3. Drift is order-insensitive; the trace is not
`D` ignores order, but the prefix series `D_i` used for lead-time analysis does not.

## C. Inconsistencies found in paper v1 (fix in v2)

Both are in the frozen, published v1.

| # | Where | Issue |
|---|---|---|
| **C1** | Listing 1 vs Appendix D | Appendix D says it uses "the dependency-upgrade contract from the main paper", but its `Θ` (shell `read`/`write`, `git status`) differs from Listing 1 (shell `execute` only; `allow_cmds` = `pip`, `pytest`, `git diff`). The worked example is internally consistent but does not match the listing it cites. *Fix:* give Appendix D its own contract, or align the two. The fixture `tests/fixtures/appendix_d.yaml` encodes the Appendix D version. |
| **C2** | Appendix D, action 9 | Says the CI-config write "fails condition 3". Under the paper's own Definition 4, `.github/workflows/ci.yml` is also outside `S`, so it fails **conditions 2 and 3**. The verdict is unchanged. |

Both reproductions are asserted in the test suite: `D = 22/31 ≈ 0.7097` for Run A and
`D = 0.10` for Run B.
