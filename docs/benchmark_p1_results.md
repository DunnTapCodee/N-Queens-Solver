# P1 controlled benchmark results

## Scope and execution

P1 used the plan in [benchmark_p1_plan.md](benchmark_p1_plan.md), with five
trials and a 10-second timeout per call. The final complete matrix contains
**300 records** in the new `results/p1/` namespace. No historical result or
`report/report.tex` was overwritten.

The commands were run with the repository source layout enabled:

```text
$env:PYTHONPATH='src'
python scripts/benchmark_comparison.py --solvers SAT/Glucose3 --sizes 4 8 16 32 64 --encodings pairwise sequential binary commander --repetitions 5 --timeout 10 --output results/p1/glucose3.json
python scripts/benchmark_comparison.py --solvers SAT/CaDiCaL --sizes 4 8 16 32 64 --encodings pairwise sequential binary commander --repetitions 5 --timeout 10 --output results/p1/cadical195.json
python scripts/benchmark_comparison.py --solvers "DPLL fallback" --sizes 4 8 --encodings pairwise sequential binary commander --repetitions 5 --timeout 10 --output results/p1/dpll_final.json
python scripts/benchmark_comparison.py --solvers "CPLEX MIP" --sizes 4 8 --repetitions 5 --timeout 10 --output results/p1/cplex_mip.json
python scripts/benchmark_comparison.py --solvers "CPLEX CP Optimizer" --sizes 4 8 16 32 64 --repetitions 5 --timeout 10 --output results/p1/cplex_cp.json
python scripts/benchmark_comparison.py --solvers Gurobi --sizes 4 8 16 32 64 --repetitions 5 --timeout 10 --output results/p1/gurobi.json
```

The runner was extended only to dispatch the already-existing DPLL fallback
and to record independent `validate_solution` results. No encoding or solver
algorithm was changed.

## Final complete matrix

| Family | Records | SAT | UNSAT | FEASIBLE | OPTIMAL | TIMEOUT | ERROR | LICENSE_LIMIT | Valid solutions |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| PySAT/Glucose3 | 100 | 100 | 0 | 0 | 0 | 0 | 0 | 0 | 100 |
| PySAT/CaDiCaL | 100 | 100 | 0 | 0 | 0 | 0 | 0 | 0 | 100 |
| DPLL fallback | 40 | 40 | 0 | 0 | 0 | 0 | 0 | 0 | 40 |
| CPLEX MIP | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 10 |
| CPLEX CP Optimizer | 25 | 0 | 0 | 25 | 0 | 0 | 0 | 0 | 25 |
| Gurobi | 25 | 0 | 0 | 25 | 0 | 0 | 0 | 0 | 25 |
| **Total** | **300** | **250** | **0** | **50** | **0** | **0** | **0** | **0** | **300** |

All performance sizes are satisfiable N-Queens instances, so the performance
matrix does not provide an UNSAT timing comparison. UNSAT behavior remains
covered by the separate backend smoke test at N=3.

## Backend and environment information

The availability metadata recorded with each run reports:

- CPLEX/docplex: `22.2.0.0`;
- Gurobi: `13.0.3`;
- PySAT package: `1.9.dev15`;
- OR-Tools: unavailable (`No module named 'ortools'`).

The per-record `solver_version` is populated for CPLEX/Gurobi. PySAT records
retain `null` there because the existing helper looks up the adapter label
while the record stores the backend name; the package version is still present
in run metadata. DPLL has no external solver version.

CPLEX MIP was intentionally limited to N=4,8 because the historical N=16
Community Edition limit is already documented. CP Optimizer and Gurobi ran to
N=64. OR-Tools was not attempted beyond the prior smoke result because its
dependency is missing.

## Interrupted/failed attempts kept separately

The first DPLL invocation exposed a runner compatibility defect: `DPLL
fallback` was incorrectly assigned `encoding=n/a`. Its separate artifact is
`results/p1/dpll.json` with 15 `ERROR` records and is not part of the final
matrix.

After the dispatch-selection fix, an exploratory DPLL N=16 run was stopped
after repeated long timeouts. Its partial artifact is
`results/p1/dpll_v2.json`: 44 records, consisting of 40 SAT and 4 TIMEOUT.
It is retained as evidence and excluded from the complete summary. The final
DPLL family is `dpll_final.json`, containing only the completed N=4,8 cells.

This handling preserves the actual failures and avoids silently treating an
incomplete run as a full five-trial matrix.

## Artifact validation

For each final family, a read-only validation checked:

- JSON and CSV record counts match;
- expected trial keys are unique;
- each planned cell has five trials;
- summary counts match raw records for every status;
- every non-null returned solution has `solution_valid=true` from the
  independent validator.

The validation result was:

```text
glucose3     100 records: SAT=100, valid=100
cadical195   100 records: SAT=100, valid=100
dpll_final    40 records: SAT=40, valid=40
cplex_mip     10 records: SAT=10, valid=10
cplex_cp      25 records: FEASIBLE=25, valid=25
gurobi        25 records: FEASIBLE=25, valid=25
VALIDATION OK
```

The infrastructure tests also passed:

```text
python -m pytest -q tests/test_benchmark_infrastructure.py
8 passed in 0.15s
```

AST parsing passed and `git diff --check` reported no content errors. No full
test suite was run.

## Metrics and comparability limits

The artifacts contain construction/build time, solver-call time, total time,
and model-size fields available from each adapter. Peak memory is unavailable.
SAT total time includes the SAT dispatch/setup interval after CNF construction;
CP/MIP/Gurobi build timing includes adapter/model construction. These are
reported separately and should not be treated as perfectly identical timing
protocols across paradigms. SAT and CP/MIP formulation sizes are kept in
separate explicit aliases, while legacy fields remain for compatibility.

The data is sufficient for P2/P3 descriptive tables and plots within each
family, with the above caveats. It is not sufficient for an unconditional
ranking across SAT, CP, and MIP based only on total time, nor for UNSAT
performance claims at N=4..64.

## Final artifact list

Each final JSON has a matching CSV and summary JSON:

- `results/p1/glucose3.json`, `.csv`, `_summary.json`;
- `results/p1/cadical195.json`, `.csv`, `_summary.json`;
- `results/p1/dpll_final.json`, `.csv`, `_summary.json`;
- `results/p1/cplex_mip.json`, `.csv`, `_summary.json`;
- `results/p1/cplex_cp.json`, `.csv`, `_summary.json`;
- `results/p1/gurobi.json`, `.csv`, `_summary.json`.

The partial/error DPLL artifacts are also retained in the same namespace and
are explicitly excluded from final aggregate counts.
