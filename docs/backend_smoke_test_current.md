# Current backend smoke test

## Scope

This was a backend availability/correctness smoke test only. It did not run a
benchmark matrix, collect performance results, modify `report/report.tex`, or
modify any historical artifact.

## Commands

The first direct invocation was:

```text
python scripts/smoke_backends.py --output results/raw/backend_manifest_current_20261017.json
```

It stopped before backend execution because this source-layout checkout did
not have `src` on `PYTHONPATH` (`ModuleNotFoundError: No module named
'nqueens'`). No output was created by that attempt.

The successful commands were:

```text
$env:PYTHONPATH='src'
python scripts/smoke_backends.py --output results/raw/backend_manifest_current_20261017.json
$env:PYTHONPATH='src'
python scripts/smoke_backends.py --output results/raw/backend_manifest_current_20261017_v2.json
```

The second successful run is authoritative because it uses the corrected
manifest interpretation for unavailable dependencies. Both output paths were
new and passed the overwrite guard.

## Test cases and validation

Every backend used the existing `sequential` encoding with:

- `N=4` for a SAT case;
- `N=3` for an UNSAT case;
- timeout 10 seconds for SAT/DPLL/CPLEX/Gurobi adapters and 1 second for
  OR-Tools, as specified by the existing script.

Returned SAT/FEASIBLE solutions were independently checked with
`nqueens.model.validate_solution`. For UNSAT cases, no solution was accepted
and the normalized solver status was recorded as the proof/result status.

| Backend | Detected/initialized | N=4 | Valid solution | N=3 | Conclusion |
|---|---:|---|---:|---|---|
| PySAT/Glucose3 | yes / yes | SAT | yes | UNSAT | verified |
| PySAT/CaDiCaL | yes / yes | SAT | yes | UNSAT | verified |
| DPLL fallback | yes / yes | SAT | yes | UNSAT | verified |
| CPLEX MIP | yes / yes | SAT | yes | UNSAT | verified |
| CPLEX CP Optimizer | yes / yes | FEASIBLE | yes | UNSAT | verified; feasibility is not OPTIMAL |
| Gurobi | yes / yes | FEASIBLE | yes | UNSAT | verified; feasibility is not OPTIMAL |
| OR-Tools CP-SAT | no / no | ERROR | n/a | ERROR | dependency unavailable |

Raw statuses are preserved in the manifest. CPLEX emitted its normal
infeasible detail for the UNSAT case; this is not treated as an operational
error. No `LICENSE_LIMIT`, `TIMEOUT`, or solver exception occurred in the
available backends. Gurobi printed its license ID during initialization but
completed both smoke cases.

## Artifacts

- Authoritative manifest:
  `results/raw/backend_manifest_current_20261017_v2.json`
- Preliminary manifest from the first successful run:
  `results/raw/backend_manifest_current_20261017.json`
- This report:
  `docs/backend_smoke_test_current.md`

The manifest contains `schema_version`, `run_id`, the encoding/case sizes,
and per-backend detected, initialized, SAT-solved, UNSAT-confirmed, raw
status, validation, backend, and error information.

## Follow-up checks

The P0.5 fixture tests were rerun after the smoke-script change:

```text
python -m pytest -q tests/test_benchmark_infrastructure.py
```

Result: `8 passed`. AST parsing and `git diff --check` also passed. The test
suite was not run wholesale.

## P1 decision

Eligible for the next P1 matrix, subject to its explicit configuration:

- PySAT/Glucose3;
- PySAT/CaDiCaL;
- DPLL fallback as a separate baseline;
- CPLEX MIP;
- CPLEX CP Optimizer;
- Gurobi.

OR-Tools CP-SAT should be excluded from the executable P1 matrix until the
`ortools` dependency is installed and a new smoke test is run. This smoke test
does not justify performance claims or direct ranking between the backends.

The historical `results/raw/backend_manifest.json`, benchmark JSON/CSV files,
and `report/report.tex` were not overwritten.
