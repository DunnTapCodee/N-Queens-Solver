# CP-SAT Performance Benchmark Results

Date: 2026-10-17

## Scope and reproducibility

This run benchmarked only the OR-Tools CP-SAT backend in the isolated
`.venv-cpsat` environment. It used N = 4, 8, 16, 32, and 64, five trials per
N, and a 10-second timeout per trial. No other backend, correctness rerun, or
large-N experiment was executed.

Command:

```powershell
$env:PYTHONPATH = 'src'
.\.venv-cpsat\Scripts\python.exe scripts/benchmark_comparison.py `
  --solvers 'OR-Tools CP-SAT' `
  --sizes 4 8 16 32 64 `
  --encodings n/a `
  --repetitions 5 `
  --timeout 10 `
  --output results/cp_sat/cp_sat_performance_20261017.json
```

Runtime metadata recorded in the artifact:

- Python: 3.11.9
- OR-Tools: 9.15.6755
- Platform: Windows 10 (`Windows-10-10.0.26200-SP0`)
- Run ID: `20261017T164221Z-a0e839c42718`
- Encoding: `n/a` because CP-SAT is a constraint model, not a SAT CNF
  encoding in this benchmark.
- CP-SAT clause count and constraint count: unavailable (`null`); no clause or
  constraint count was inferred from another metric.

## Trial-level outcome

| N | Trials | OPTIMAL | FEASIBLE | UNSAT | TIMEOUT | ERROR | LICENSE_LIMIT | Valid returned solutions |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 4 | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 5/5 |
| 8 | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 5/5 |
| 16 | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 5/5 |
| 32 | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 5/5 |
| 64 | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 5/5 |
| **Total** | **25** | **25** | **0** | **0** | **0** | **0** | **0** | **25/25** |

Every returned solution was independently checked with
`nqueens.model.validate_solution`. No trial had an error, timeout, or license
limit, and no returned solution failed validation.

## Runtime summary

Times are seconds. `total` is measured around the complete adapter call;
`build` and `solve` come from the adapter. The first N=4 trial is a visible
one-time initialization outlier, so both median and mean are retained.

| N | Median total | Mean total | Sample stdev total | Median build | Median solver |
|---:|---:|---:|---:|---:|---:|
| 4 | 0.072137 | 0.801006 | 1.627616 | 0.005804 | 0.063654 |
| 8 | 0.119335 | 0.109767 | 0.017473 | 0.005546 | 0.112086 |
| 16 | 0.189959 | 0.190035 | 0.017919 | 0.004130 | 0.184410 |
| 32 | 0.376305 | 0.523912 | 0.289680 | 0.003180 | 0.372655 |
| 64 | 1.630790 | 1.642322 | 0.404449 | 0.003845 | 1.626894 |

The data supports an increase in measured CP-SAT runtime across these tested
N values, with solver time dominating the recorded total for N >= 8. This is a
within-backend observation only. It does not establish that CP-SAT is faster
than SAT, CPLEX, Gurobi, or any other backend because this run did not measure
those backends under the same run conditions.

## Artifact validation

The following checks were run without invoking a solver:

```powershell
$env:PYTHONPATH = 'src'
.\.venv-cpsat\Scripts\python.exe -c "...read and validate JSON, CSV, and summary..."
```

Results:

- JSON records: 25.
- CSV records: 25.
- Summary groups: 5, one for each N, with five trials each.
- JSON and CSV field sets match.
- All configured N values are represented exactly five times.
- All statuses are preserved as `OPTIMAL`; there are no omitted timeout or
  error records.
- All 25 `solution_valid` values are true.
- All records report OR-Tools 9.15.6755.
- CP-SAT-specific unavailable metrics remain null rather than zero.
- The summary counts and runtime statistics were read from the raw records and
  passed the consistency assertions.

## Artifacts

- [Raw JSON](../results/cp_sat/cp_sat_performance_20261017.json)
- [Trial CSV](../results/cp_sat/cp_sat_performance_20261017.csv)
- [Summary JSON](../results/cp_sat/cp_sat_performance_20261017_summary.json)

No artifact in `results/raw/`, `results/p1/`, or `results/p2_p3/` was changed,
and `report/report.tex` was not changed.

## Readiness for report integration

The CP-SAT dataset is complete and internally consistent for the requested
25-trial experiment. It can be integrated as a separate CP-SAT constraint-model
result set, with its unavailable model-constraint metric stated explicitly.
It should not be merged into a single ranking with other backends unless their
formulation, timing conditions, and metrics are first shown to be comparable.

