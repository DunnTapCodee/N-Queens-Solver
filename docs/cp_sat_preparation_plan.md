# CP-SAT preparation plan

## Scope

This is a preparation and design step only. No dependency was installed, no
solver or smoke test was run, no benchmark was executed, and no existing source,
report, configuration, or artifact was modified.

## 1. Environment and dependency options

The repository uses a `pyproject.toml` with:

- `requires-python = ">=3.10"`;
- no mandatory runtime dependencies;
- pytest configured to add `src` to `PYTHONPATH`.

The active interpreter is:

```text
C:\Users\ADMIN\AppData\Local\Programs\Python\Python311\python.exe
Python 3.11.9, 64-bit Windows
```

`py -0p` found only the Python 3.11 installation and the WindowsApps alias.
No repository virtual environment directory was found. The read-only module
check returned:

```text
ortools_spec: None
```

The least disruptive future option is an isolated virtual environment under a
new, clearly named path such as `.venv-cpsat`, created with the existing Python
3.11 interpreter. OR-Tools should be installed only there, with its exact
version recorded in the CP-SAT artifact metadata. This avoids changing the
global interpreter used by the existing SAT/CPLEX/Gurobi results. A separate
machine or CI environment with a locked dependency is an equally valid option.

No installation command is authorized or executed in this step. The existing
`pyproject.toml` should not be changed merely to inspect readiness; if CP-SAT
becomes a supported project dependency later, that change should be reviewed
separately.

## 2. Adapter and schema findings

`src/nqueens/cp_sat.py` lazily imports
`ortools.sat.python.cp_model`, so the repository itself remains importable when
OR-Tools is absent. When available, the model uses one integer column variable
per row, `AddAllDifferent` for columns and both diagonal index families, a
configurable time limit, and a random seed. It validates returned placements
with `nqueens.model.validate_solution`.

The current status mapping is:

| CP-SAT API status | Current adapter behavior | Preparation assessment |
|---|---|---|
| `OPTIMAL` | Intermediate `SAT`, then returned as `FEASIBLE` | Valid placement, but optimality is not preserved |
| `FEASIBLE` | Intermediate `SAT`, then returned as `FEASIBLE` | Correct feasibility meaning |
| `INFEASIBLE` | `UNSAT` | Appropriate for this feasibility model |
| `UNKNOWN` | `TIMEOUT` | Usually suitable for a time-limited run, but raw status must be retained |
| Unexpected status/exception | `ERROR` | Appropriate error category |

`raw_status` is already stored by the `SolveResult` path as a string, so a
future artifact can retain the underlying CP-SAT status. The minimum reviewed
change before benchmarking should be to preserve `OPTIMAL` separately from
`FEASIBLE` if the report requires the normalized status vocabulary to be
lossless. This is a small adapter change, not a model change. If the team
chooses to keep the current feasibility normalization, the report must state
that CP-SAT optimality is not separately represented.

The adapter returns `nvars=N` and `nclauses=0`. That zero is not a measured
CP-SAT clause or constraint count. Under the current additive schema it must be
treated as unavailable for CP-SAT, not compared with SAT clauses and not
reported as a real constraint count. The benchmark writer currently populates
legacy `nconstraints` from the generic `SolveResult.nclauses`; this is already
ambiguous for model backends. For CP-SAT, the minimal safe approach is to emit
null/unavailable for model constraint metrics unless a separately reviewed
adapter change obtains a real count. No count should be inferred.

The current comparison runner can dispatch `OR-Tools CP-SAT` and selects
`encoding=n/a` for non-SAT solvers. It also records timeout, raw status,
validation, timing, run ID, and output guard metadata. Therefore the execution
path is compatible in principle, subject to the status and metric decisions
above and a real OR-Tools installation.

## 3. Minimum changes before data collection

No code is changed in this preparation step. Before benchmark execution, review
only these minimal items:

1. Preserve CP-SAT `OPTIMAL` and `FEASIBLE` separately, or explicitly approve
   the existing feasibility-only normalization in the report protocol.
2. Ensure CP-SAT unavailable model metrics are null/unavailable rather than
   zero or SAT clause counts. Keep `model_nconstraints` distinct from
   `sat_nclauses`.
3. Record the exact OR-Tools version and interpreter in the new run metadata.
4. Use a new output namespace, for example `results/cp_sat/`, and rely on the
   existing overwrite guard. Never reuse `results/raw/` or `results/p1/`.
5. Keep `FEASIBLE`, `OPTIMAL`, `UNSAT`, `TIMEOUT`, `ERROR`, and
   `LICENSE_LIMIT` distinct in summaries. CP-SAT `UNKNOWN` should retain its
   raw status and only be normalized to `TIMEOUT` under the documented timeout
   policy.

These changes do not require changing the N-Queens model or any existing SAT
encoding.

## 4. Pre-benchmark test plan

### Correctness gate

Run CP-SAT only after the dependency is available and the reviewed schema
decision is implemented:

- N=1 and N=4: expect a valid returned placement;
- N=2 and N=3: expect `UNSAT` and no placement;
- independent `validate_solution` for every returned placement;
- record raw CP-SAT status, normalized status, error, and version;
- verify no model metric is silently represented by zero.

The correctness gate must pass before any performance command is started.

### Performance family

After correctness passes, run a separate CP-SAT family with:

- N=4, 8, 16, 32, 64;
- five trials per configuration;
- 10-second timeout per solver call;
- fixed/documented seed policy;
- new JSON, CSV, and summary paths under a CP-SAT namespace;
- run ID, Python version, OR-Tools version, configuration, raw/normalized
  status, validator result, build/solver/total timing, and applicable metrics.

The performance run must preserve every outcome. It must not replace a timeout
with a runtime of zero, treat FEASIBLE as OPTIMAL, or merge CP-SAT records into
the existing SAT/CP/MIP families without an explicit comparability note.

## 5. Conditions required before execution

All of the following must be true:

1. An authorized isolated environment provides an importable OR-Tools package.
2. The exact Python and OR-Tools versions are recorded.
3. The CP-SAT status normalization decision is approved.
4. Unavailable constraint metrics are represented as null/unavailable.
5. The correctness matrix plan and output namespace are fixed.
6. The correctness results pass independent validation before performance is
   attempted.
7. Existing historical and P1 artifacts remain protected by the output guard.

## Current decision

CP-SAT preparation is **BLOCKED for execution** because OR-Tools is absent.
The adapter is **conditionally compatible**, not shown to be incorrect. The
next action is to obtain approval for an isolated OR-Tools environment; after
that, review the status/metric decisions and run the correctness gate before
any performance benchmark.
