# CP-SAT Report Integration Audit

Date: 2026-10-18

## Checks performed

The following inputs were inspected:

- `docs/cp_sat_performance_results.md`
- `results/cp_sat/cp_sat_performance_20261017.json`
- `results/cp_sat/cp_sat_performance_20261017.csv`
- `results/cp_sat/cp_sat_performance_20261017_summary.json`
- `docs/benchmark_report_plan.md`
- `report/report.tex`

The raw CP-SAT audit found 25 JSON records and 25 CSV records. The five N
values (4, 8, 16, 32, 64) each contain exactly five trials, numbered 1--5.
All 25 records have status `OPTIMAL`, `solution_valid=true`, no error, and
OR-Tools version 9.15.6755. The timeout is 10 seconds and the run metadata
contains the run ID, Python version, platform, repetitions, and timeout.

The summary statistics were recomputed from the raw `total_time_s` values and
match the summary artifact exactly:

| N | Median (s) | Mean (s) | Sample stdev (s) |
|---:|---:|---:|---:|
| 4 | 0.072137 | 0.801006 | 1.627616 |
| 8 | 0.119335 | 0.109767 | 0.017473 |
| 16 | 0.189959 | 0.190035 | 0.017919 |
| 32 | 0.376305 | 0.523912 | 0.289680 |
| 64 | 1.630790 | 1.642322 | 0.404449 |

The N=4 mean is much larger than its median because trial 1 took 3.712484 s,
while the other trials were below 0.1 s. The trial was retained; no outlier was
removed. `nclauses` and `nconstraints` are null for CP-SAT and are not treated
as measured counts.

The referenced P1/P2/P3 artifacts and historical results were not modified.

## Report changes

`report/report.tex` was updated to:

- describe CP-SAT as a separately benchmarked constraint-model family;
- record Python 3.11.9, OR-Tools 9.15.6755, and the separate run scope;
- add the CP-SAT median runtime row to the model-family table;
- state that the 25 CP-SAT trials are not included in the 300-record P1 total;
- distinguish CP-SAT `OPTIMAL` results from P1 `FEASIBLE` model results;
- explain the N=4 mean/median difference and retain the first trial;
- update the limitations and conclusion so they no longer claim CP-SAT was
  unavailable, while preserving the lack of a cross-paradigm ranking;
- add `results/cp_sat/` to data availability.

No CP-SAT records were merged into P1. The report still treats SAT encodings
with Glucose3/CaDiCaL, DPLL, CPLEX MIP, CPLEX CP Optimizer, Gurobi, and CP-SAT
as separate groups where formulation or experimental scope differs.

## Figures, references, and LaTeX checks

All five existing figure paths referenced by `report/report.tex` exist:

- `results/p2_p3/sat_runtime_by_n.svg`
- `results/p2_p3/sat_encoding_median_runtime.svg`
- `results/p2_p3/sat_cactus.svg`
- `results/p2_p3/model_family_runtime.svg`
- `results/p2_p3/completion_status_by_n.svg`

`git diff --check` reported no whitespace errors. Brace counts in the TeX
source are balanced. No `pdflatex`, `lualatex`, or `xelatex` compiler was
available, and no `cas-sc.cls` file was found in the repository, so PDF
compilation could not be attempted successfully.

The repository contains `mode_title.pdf` and the assignment PDF, but no PDF
text extraction tool or Python PDF reader was available in the current
environment. Therefore the bibliographic metadata of the reference PDF could
not be independently compared page-by-page with `bibitem{reference}`. The
report does not add a new citation or claim this comparison was verified.
This remains a documentation check to complete if the final submission
requires exact reference metadata.

## Commands and outcome

Read-only validation used Python to load JSON/CSV/summary, recompute per-N
counts and mean/median/stdev, check all statuses and validation flags, and
verify null CP-SAT metrics. It passed. `git diff --check` also passed.

No benchmark, solver, or smoke test was run in this integration step. No
dependency was installed. The only source change was `report/report.tex`; the
only new file created was this audit.

## Submission status

The report content is updated consistently with the verified CP-SAT dataset,
but a final PDF cannot be claimed because the LaTeX compiler and `cas-sc.cls`
are unavailable. Exact reference-metadata verification is also pending PDF
text extraction. The benchmark data themselves are ready for report use; the
remaining blockers are environmental/documentation checks, not missing CP-SAT
trials.

