# P0 Benchmark Audit — N-Queens Solver

Audit date: 2026-10-17

Scope: read-only inspection of source code, README, benchmark artifacts, existing
validators, and report references. No benchmark, solver, dependency installation,
algorithm, benchmark artifact, or `report/report.tex` was modified.

## Executive conclusion

The project can move toward P1 only after a small data/schema cleanup. The
existing results are useful and most primary JSON/CSV pairs are semantically
consistent, but they are not yet one homogeneous benchmark corpus. There are
multiple runs with overlapping sizes and different schemas, historical metadata
states, and summary defects in older smoke/Gurobi files. A new P1 benchmark
should therefore use a new output namespace and an explicit schema version.

## A. Implemented methods and infrastructure

### SAT encodings

`src/nqueens/encoding.py` contains the following VERIFIED encodings:

- `pairwise` (Binomial AMO);
- `sequential` (Sinz-style sequential AMO);
- `binary`;
- `commander` with group size three and recursive commander constraints.

Recursive 2-Product is not implemented. The source does not contain a Product
encoding. No constructive N-Queens algorithm or integer-column MIP model is
implemented.

### Solver backends and adapters

VERIFIED integrations:

- PySAT with selectable `glucose3` and `cadical195` backends;
- an internal DPLL fallback when PySAT cannot be imported;
- CPLEX MIP through `docplex.mp`;
- CPLEX CP Optimizer through `docplex.cp`;
- Gurobi through `gurobipy`;
- OR-Tools CP-SAT through a lazy optional adapter.

The current manifest records PySAT and CPLEX as usable and OR-Tools/Gurobi as
unavailable. This manifest is older than the Gurobi follow-up artifacts: the
follow-up metadata records Gurobi 13.0.3 as installed and usable. This is a
VERIFIED historical environment inconsistency, not evidence that either set of
results is fabricated.

### Configuration entry points

| Component | Configurable inputs | Output behavior |
|---|---|---|
| `scripts/benchmark.py` | `--sizes`, `--encodings`, `--repetitions`, `--timeout`, `--seed`, `--output` | Writes JSON, CSV, and a summary next to the selected output; no overwrite guard |
| `scripts/benchmark_comparison.py` | `--solvers`, `--sizes`, `--encodings`, `--repetitions`, `--timeout`, `--output` | Supports individual solver/backend selection and separate output path; writes an initial empty output immediately |
| `scripts/benchmark_medium_matrix.py` | only `--repetitions`, `--timeout` | Sizes and configurations are hard-coded; fixed output paths can be overwritten |
| `scripts/smoke_backends.py` | no CLI configuration | Always writes `results/raw/backend_manifest.json` |
| `scripts/plot_*.py` | input/output options vary | Reads summaries and writes SVG files |

README commands document the historical, comparison, medium, plotting, and
validation workflows. The recommended `PYTHONPATH=src` setup is present in
README and `pyproject.toml` configures pytest to use `src`.

## B. Artifact inventory

Counts below are from the files currently present under `results/raw`. `N`
sets, statuses, and schemas were read from the actual JSON records, not inferred
from filenames.

### Primary record artifacts

| Artifact | Records | N values | Encoding/backend | Trials | Statuses | Validation and fields |
|---|---:|---|---|---:|---|---|
| `benchmark.json`, `.csv` | 14 | 1,2,3,4,8,16,32 | Pairwise/Sequential; backend field is stored | No trial field | SAT 10, UNSAT 4 | `encoding_time_s`, `solve_time_s`, `total_time_s`, `nvars`, `nclauses`, `solution_valid`; no `raw_status` or solver version |
| `benchmark_repeated.json`, `.csv` | 80 | 1,2,3,4,8,16,32,64 | Pairwise/Sequential, `PySAT/Glucose3` | 5 per cell | SAT 60, UNSAT 20 | `encoding_time_s`, `solve_time_s`, `total_time_s`, formula size, seed, validation flag; no raw backend status |
| `benchmark_comparison.json`, `.csv` | 72 | 1,2,3,4,8,16 | Glucose3 Pairwise/Sequential; CPLEX MIP; CPLEX CP | 3 per cell | SAT 45, UNSAT 24, ERROR 3 | Solver version, Python, timeout, build/solve/total time, model size, validation, error |
| `benchmark_comparison_smoke.json`, `.csv` | 20 | 1,2,3,4,8 | Glucose3 Pairwise/Sequential; CPLEX MIP/CP | 1 per cell | SAT 12, UNSAT 8 | Same comparison-style fields; generated with one trial per configuration/size |
| `benchmark_medium_correctness.json`, `.csv` | 40 | 1,2,3,4 | Glucose3/CaDiCaL × four encodings; CPLEX MIP/CP | 1 per cell | SAT 18, UNSAT 20, FEASIBLE 2 | `raw_status`, solver version, build/solve/total, CNF/model counts, validation, error |
| `benchmark_medium_performance.json`, `.csv` | 87 | 4,8,16 | Glucose3/CaDiCaL × four encodings; CPLEX MIP/CP | 3 per executed cell | SAT 78, FEASIBLE 9 | CPLEX MIP N=16 is intentionally excluded in metadata |
| `benchmark_gurobi.json`, `.csv` | 9 | 4,8,16 | Gurobi | 3 per N | FEASIBLE 6, ERROR 3 | N=4/8 valid; old N=16 records are license errors; solver version is null |
| `benchmark_gurobi_n16.json`, `.csv` | 3 | 16 | Gurobi | 3 | FEASIBLE 3 | `solution_valid=true`, raw status `2`, solver version null |
| `benchmark_gurobi_followup.json`, `.csv` | 15 | 1,2,3,4,8 | Gurobi | 3 per N | FEASIBLE 9, UNSAT 6 | Gurobi 13.0.3, raw status, build/solve/total, validation and error fields |

There are no separate result files for a successful OR-Tools benchmark, nor
separate CPLEX-only output files beyond the comparison and medium matrices.

### Summary and manifest artifacts

| Artifact | Verified content | Finding |
|---|---|---|
| `benchmark_repeated_summary.json` | 16 groups × 5 trials | Consistent with the 80-record repeated benchmark; medians use SAT/UNSAT records |
| `benchmark_comparison_summary.json` | 24 groups × 3 trials | Consistent with the 72-record comparison; old Gurobi is not included |
| `benchmark_comparison_smoke_summary.json` | 4 groups × 5 records | **Schema defect:** summary omits `n`, so five sizes are collapsed into one group per solver/encoding; metadata has `repetitions=1` |
| `benchmark_medium_correctness_summary.json` | 40 groups × 1 trial | Status dictionary includes SAT, UNSAT, FEASIBLE, OPTIMAL, TIMEOUT, ERROR, LICENSE_LIMIT |
| `benchmark_medium_performance_summary.json` | 29 groups × 3 trials | Consistent with 87 records and declared CPLEX MIP exclusion |
| `benchmark_gurobi_summary.json` | 3 groups × 3 trials | **Historical summary defect:** raw FEASIBLE records are not counted in `sat`; summary reports only errors for the old N=16 failure case |
| `benchmark_gurobi_n16_summary.json` | 1 group × 3 trials | **Historical summary defect:** raw FEASIBLE records are not represented by a `feasible` count |
| `benchmark_gurobi_followup_summary.json` | 5 groups × 3 trials | Includes `feasible`, `optimal`, and `license_limits`; consistent with follow-up raw records |
| `backend_manifest.json` | Six backend smoke results | **Environment drift:** Gurobi is recorded unavailable here, while later Gurobi artifacts record 13.0.3 and successful runs |

## C. Consistency audit

### JSON/CSV correspondence

Every primary record artifact has a corresponding CSV with the same record
count. Existing validators confirm the key fields for the 80-record historical
benchmark, 72-record comparison, and 40/87 medium matrices.

The JSON and CSV are not type-identical: JSON `null` values are emitted as
empty CSV cells. Therefore a strict string comparison reports differences for
nullable fields such as `error`, `solver_version`, or `nvars`, but this is a
serialization difference rather than a record-count or status mismatch. The
old Gurobi CSVs also serialize null solver versions as empty cells.

### Summary correspondence

VERIFIED consistent:

- `benchmark_repeated_summary.json` with the 80 raw records;
- `benchmark_comparison_summary.json` with the 72 raw records;
- both medium summaries with their raw record sets;
- Gurobi follow-up summary with its 15 raw records.

VERIFIED inconsistent or incomplete:

- `benchmark_comparison_smoke_summary.json` loses the `n` grouping key;
- old Gurobi summaries omit a `FEASIBLE` counter even though raw records contain
  FEASIBLE solutions;
- old Gurobi artifacts have null solver versions, while the later follow-up
  records Gurobi 13.0.3.

### Status semantics

The adapters use the following convention:

- SAT: a valid satisfying placement from the SAT or MIP adapter;
- UNSAT: backend reports infeasibility/no solution;
- FEASIBLE: a valid placement from CP Optimizer or Gurobi;
- OPTIMAL: schema-supported but no current N-Queens record uses it;
- TIMEOUT: solver/process reaches its time limit without a solution;
- ERROR: dependency, decoding, or unexpected backend failure;
- LICENSE_LIMIT: recognized license/model-size restriction.

The normalized status is not always the raw backend status. For example,
CPLEX MIP stores SAT for a valid feasibility placement while retaining
`integer optimal solution` as raw status; Gurobi stores FEASIBLE for a valid
placement with raw status `2`. This is appropriate for a feasibility problem,
but P1 should make the distinction explicit in a shared schema.

### Validation flags

SAT/FEASIBLE/OPTIMAL records in the validated medium and Gurobi follow-up
artifacts have `solution_valid=true`; UNSAT records do not have a solution.
The adapters call `validate_solution` before returning a solution. However,
the benchmark record writer stores only `result.solution is not None`, not a
separate validator result or validator version. This is VERIFIED as a schema
limitation: validation happens in the adapter, but the artifact does not expose
that provenance directly.

### Timing and resource measurements

| Family | Construction field | Solver-call field | Total field | Peak memory |
|---|---|---|---|---|
| Historical SAT | `encoding_time_s` | `solve_time_s` | `encoding + solve` | Not recorded |
| Comparison/medium/Gurobi | `build_time_s` | `solve_time_s` | Outer `perf_counter` around adapter | Not recorded |

SAT construction time measures CNF encoding. Its solve interval includes the
SAT backend setup/call after encoding. CPLEX/CP/Gurobi construction timing
starts before the lazy dependency import and model construction, so the
intervals are not perfectly comparable across paradigms. Total time in the
comparison and medium scripts includes the adapter dispatch; it is not simply
the sum of the two stored sub-times in every backend.

No artifact stores RSS, peak memory, process-tree memory, CPU utilization, or
solver thread count. The supplied reference report contains memory and
large-scale measurements, but those fields are absent from this repository's
current benchmark schema.

### Overlapping runs and direct comparability

The following overlaps are VERIFIED but must not be merged without an explicit
run identity:

- `benchmark.json` is an earlier 14-record SAT run; `benchmark_repeated.json`
  is the later 80-record repeated run and supersedes it for repeated SAT
  analysis.
- `benchmark_comparison_smoke` overlaps N=1..8 with the 72-record comparison,
  but uses one trial and an incomplete summary schema.
- The medium matrix overlaps N=4,8,16 and Pairwise/Sequential with the older
  comparison, but has different backend labels, four encodings, CaDiCaL, and a
  separate execution timestamp.
- `benchmark_gurobi.json` overlaps N=4,8 with the follow-up and N=16 with the
  separate N=16 artifact, but the files were generated under different code or
  environment states. They must remain separate.

The artifacts do not contain a run UUID or source revision, so exact duplicate
record detection across runs is UNKNOWN. Timestamps and schema differences are
enough to establish that these are separate benchmark families.

## D. Data present and missing

### Present and VERIFIED

- Four SAT encodings and two PySAT backend selections.
- Validated historical SAT measurements through N=64.
- Correctness and medium performance matrices.
- CPLEX MIP and CP Optimizer results with license/dependency context.
- Gurobi N=16 and follow-up measurements.
- JSON/CSV exports, summaries, solver versions in newer schemas, timeout values,
  model counts, construction/solve/total timing fields, and validation flags.

### Missing or incomplete

- No Product encoding benchmark.
- No successful OR-Tools CP-SAT benchmark.
- No peak-memory measurements.
- No stable run ID, git revision, dependency lock, or full dependency manifest
  inside every artifact.
- No explicit validator version/result field.
- Historical summaries have schema differences and Gurobi FEASIBLE-count gaps.
- `nconstraints` is populated from the generic `SolveResult.nclauses` field in
  comparison writers; its value is meaningful for the adapters but the field
  name is ambiguous for SAT versus CP/MIP.
- `benchmark_medium_matrix.py` has hard-coded sizes/configurations and fixed
  output paths.
- Output scripts do not refuse overwriting an existing path.

## E. Recommended P1 benchmark standard

Before scaling up, use one new schema and one new output directory. Recommended
configuration:

1. Correctness set: N=1,2,3,4, with all implemented encodings/backends that
   are available; one trial is enough for logical correctness.
2. Performance set: N=4,8,16,32,64, with three or five repetitions and a
   documented 10-second timeout. Exclude known license-limited cells before
   execution and record the exclusion in metadata.
3. Record `run_id`, timestamp, git revision, Python version, package versions,
   platform, solver configuration, timeout, seed, thread count, and license
   availability.
4. Use explicit `model_build_time_s`, `solver_time_s`, `total_time_s`,
   `nvars`, `nclauses`, `nconstraints`, and optionally `peak_rss_bytes`.
5. Store normalized status and raw backend status together. Keep FEASIBLE
   distinct from SAT and OPTIMAL, even when all represent a valid placement.
6. Store `solution_valid`, `validator_name`, and `validator_version` separately
   from the presence of a solution object.
7. Write JSON, CSV, and summary atomically to a new path and refuse overwrite
   unless an explicit force option is provided.
8. Generate summaries only from raw records and include per-cell sample counts;
   never aggregate across runs with different N sets or environments.

## F. Minimum changes before P1

1. Define and document a versioned common schema for SAT, CP, MIP, and Gurobi.
2. Add an overwrite guard and a run identifier to benchmark writers.
3. Fix summary generation to preserve `n` and count every normalized status,
   including FEASIBLE, OPTIMAL, and LICENSE_LIMIT.
4. Record dependency versions and environment availability consistently in the
   manifest and every benchmark metadata block.
5. Rename or split the generic model-size fields so SAT clauses and CP/MIP
   constraints cannot be confused.
6. Add an explicit independent-validation field rather than deriving it only
   from `solution is not None`.
7. Decide whether peak memory is required for P1. If yes, add a platform-aware
   measurement protocol before collecting large-instance results.
8. Keep the historical artifacts immutable and write all corrected exports to a
   new namespace.

## Checks executed

Read-only checks executed during this audit:

- File inventory with `rg --files` and `Get-ChildItem`.
- Direct JSON/CSV parsing and record/status/N/configuration inspection.
- Existing validators:

  ```text
  python scripts/validate_artifacts.py       -> passed: 80 records, 60 SAT, 20 UNSAT
  python scripts/validate_comparison.py     -> passed: 72 records
  python scripts/validate_medium_matrix.py  -> passed: 40 correctness, 87 performance
  ```

- Source inspection of encoding, solver adapters, benchmark writers, README,
  and schemas.
- No benchmark, solver run, dependency installation, or full test suite was
  executed for this audit.

Before this report was created, `git status --short` was clean. The only
intended new file from this P0 audit is this document:

`docs/benchmark_audit.md`

## Final decision

**Do not move directly to large P1 execution yet.** The algorithms and most
artifacts are usable, but P1 should first implement the minimum schema/output
guards and reconcile the historical Gurobi/manifest metadata. After those
changes are isolated from the historical files, P1 can proceed with a new
run namespace and explicitly comparable configurations.
