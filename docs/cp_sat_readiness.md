# CP-SAT readiness assessment

## 1. Assignment requirement

`Assignment 1 - requirements.pdf` explicitly names CP-SAT alongside CPLEX CP,
CPLEX MIP, and Gurobi in the requested exact-method comparison. The assignment
does not prescribe an OR-Tools version, a specific N set, a trial count, a
timeout, or a memory limit. `docs/benchmark_report_plan.md` therefore defines
the minimum intended follow-up as correctness at N=1,2,3,4 and performance at
N=4,8,16,32,64, using the established schema, five trials, and a 10-second
timeout if the dependency is available.

This document only assesses readiness. It does not run CP-SAT, a smoke test, or
any benchmark.

## 2. Environment and dependency

The interpreter checked was:

```text
C:\Users\ADMIN\AppData\Local\Programs\Python\Python311\python.exe
Python 3.11.9 (64-bit Windows build)
```

The repository declares Python `>=3.10` and has an empty mandatory dependency
list in `pyproject.toml`. OR-Tools is not declared as a project dependency.
The read-only import-spec check returned:

```text
ortools_spec: None
```

Therefore OR-Tools cannot currently be imported in this interpreter and no
OR-Tools version is available. No installation, upgrade, or removal was
attempted. The existing P1 metadata and backend smoke report independently
record the same condition: `No module named 'ortools'`.

Other environment facts relevant to a future run are Python 3.11.9 and the
existing source-layout setup (`PYTHONPATH=src`). A future CP-SAT run would also
need the OR-Tools package compatible with this Python interpreter and a
recorded package version. Those compatibility details cannot be verified until
the package is installed in an allowed environment.

## 3. Current implementation assessment

The adapter is `src/nqueens/cp_sat.py` and uses a lazy import:

```python
from ortools.sat.python import cp_model
```

When available, it constructs a CP-SAT model with:

- one integer variable per row, with domain `0..N-1`;
- `AddAllDifferent(queens)` for columns;
- `AddAllDifferent(queens[r] + r)` for one diagonal family;
- `AddAllDifferent(queens[r] - r)` for the other diagonal family;
- `max_time_in_seconds` when a timeout is supplied;
- a configurable random seed.

It converts CP-SAT statuses as follows:

| CP-SAT status | Current adapter result |
|---|---|
| `OPTIMAL` | intermediate SAT, returned as FEASIBLE |
| `FEASIBLE` | intermediate SAT, returned as FEASIBLE |
| `INFEASIBLE` | UNSAT |
| `UNKNOWN` | TIMEOUT |
| unexpected value/exception | ERROR |

Returned placements are checked with the existing independent
`validate_solution` function before being returned. The adapter is therefore
structurally usable for a feasibility benchmark once OR-Tools is available;
there is no observed syntax or import-path defect in the source itself.

Two limitations must be recorded before interpreting results:

1. The adapter intentionally collapses CP-SAT `OPTIMAL` and `FEASIBLE` to the
   normalized result `FEASIBLE`. For ordinary N-Queens feasibility this still
   represents a valid placement, but it does not preserve the distinction
   required by a general status audit. A future benchmark should retain the
   raw CP-SAT status and state this normalization explicitly; changing the
   adapter is outside this readiness check.
2. The adapter returns `nvars=N` and `nclauses=0`; it does not expose a CP-SAT
   constraint count. The benchmark must treat unavailable model metrics as
   unavailable, not as zero or as SAT clause counts.

These are reporting/schema limitations rather than evidence that the model is
incorrect. They should be reviewed before claiming a fully normalized
cross-backend schema.

## 4. Verified blockers and decision

| Item | Status | Consequence |
|---|---|---|
| Python interpreter meets project requirement | VERIFIED | No Python-version blocker observed |
| OR-Tools import | BLOCKED | CP-SAT cannot be executed in the current environment |
| OR-Tools version | UNKNOWN | No package is installed, so no version can be recorded |
| Adapter source/model structure | CONDITIONALLY READY | Static inspection found the expected CP-SAT model and validator call |
| CP-SAT runtime behavior | UNKNOWN | It was not run under the no-solver-run constraint |
| CP-SAT model-size metrics | LIMITED | Current adapter exposes no meaningful constraint count |
| Existing benchmark output safety | AVAILABLE | P0.5 output guard and new namespace policy can be reused |

## Decision: BLOCKED

CP-SAT is **not ready to benchmark in the current environment**. The specific
blocker is the missing `ortools` package, not a demonstrated algorithm or
modeling failure. The adapter is conditionally ready for a small validation
run after the dependency is provided, subject to preserving raw status and
marking unavailable model metrics correctly.

## 5. Next steps if benchmarking is authorized

In an environment where dependency changes are allowed:

1. Install or otherwise provide an OR-Tools version compatible with Python
   3.11, without modifying historical artifacts.
2. Record the exact Python and OR-Tools versions and verify importability.
3. Review whether the adapter's `OPTIMAL`/`FEASIBLE` normalization is
   acceptable for the assignment; if not, make a separately reviewed adapter
   change before collecting data.
4. Run a small correctness check at N=1,2,3,4 with independent validation,
   including UNSAT N=2,3.
5. If correctness passes, run the planned performance family at N=4,8,16,32,64
   with five trials and a 10-second timeout, using a new output namespace.
6. Validate JSON/CSV/summary consistency and keep CP-SAT results separate from
   existing P1 artifacts until the comparison conditions are documented.

No benchmark, solver, or smoke test was executed for this assessment. No
dependency was installed. No code, report, configuration, benchmark artifact,
or existing documentation was modified; the only intended new file is this
readiness report.
