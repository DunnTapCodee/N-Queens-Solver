# CP-SAT Correctness Results

Date: 2026-10-17

## 1. Environment

The test used the isolated environment `.venv-cpsat`; the global Python
environment was not modified.

| Item | Value |
|---|---|
| Python | 3.11.9 |
| OR-Tools | 9.15.6755 |
| Interpreter | `.venv-cpsat/Scripts/python.exe` |
| Timeout per correctness case | 10 seconds |
| Random seed | 0 |

Commands used:

```powershell
python -m venv .venv-cpsat
.\.venv-cpsat\Scripts\python.exe -m pip install ortools
$env:PYTHONPATH = 'src'
.\.venv-cpsat\Scripts\python.exe -c "import ortools; print(ortools.__version__)"
```

The correctness command called `solve_cp_sat` directly for N=1, 2, 3, and 4.
It did not invoke the performance benchmark, smoke-test runner, or any large-N
experiment.

## 2. Adapter changes

`src/nqueens/cp_sat.py` was changed minimally:

- CP-SAT `OPTIMAL` is preserved as benchmark status `OPTIMAL`.
- CP-SAT `FEASIBLE` is preserved as benchmark status `FEASIBLE`.
- `INFEASIBLE` maps to `UNSAT`.
- `UNKNOWN` maps to `TIMEOUT`.
- Exceptions and invalid decoded solutions map to `ERROR`.
- CP-SAT does not expose a SAT clause count in this adapter, so `nclauses` is
  now `null` (`None`) rather than the misleading value `0`.
- The existing `encoding_time` and `solve_time` fields are retained. Total
  time in the table below is their sum for this correctness check.

No other backend, encoding, historical benchmark, P1/P2/P3 artifact, or
`report/report.tex` was changed by this step.

## 3. Correctness matrix

| N | Status | Raw CP-SAT status | Solution | Independent validation | Encoding time (s) | Solver time (s) | Total (s) | nvars | nclauses |
|---:|---|---|---|---|---:|---:|---:|---:|---|
| 1 | OPTIMAL | `CpSolverStatus.OPTIMAL` | `[0]` | PASS | 1.604923 | 0.024889 | 1.629812 | 1 | null |
| 2 | UNSAT | `CpSolverStatus.INFEASIBLE` | none | PASS (UNSAT has no solution) | 0.000659 | 0.000622 | 0.001282 | 2 | null |
| 3 | UNSAT | `CpSolverStatus.INFEASIBLE` | none | PASS (UNSAT has no solution) | 0.000680 | 0.001281 | 0.001961 | 3 | null |
| 4 | OPTIMAL | `CpSolverStatus.OPTIMAL` | `[2, 0, 3, 1]` | PASS | 0.000575 | 0.011488 | 0.012063 | 4 | null |

For SAT cases, the returned column positions were checked independently with
`nqueens.model.validate_solution`. For N=2 and N=3, the independent check
confirmed that the result is UNSAT and that no solution was returned. The
results therefore satisfy the expected N-Queens correctness cases.

## 4. Compatibility checks

The adapter was imported using the isolated interpreter and executed without
an import or runtime error. The benchmark schema was checked with a CP-SAT
result using the non-SAT encoding marker `n/a`:

- `model_nvars` is populated from the adapter's `nvars`.
- `model_nconstraints` remains unavailable (`null`) because the adapter does
  not measure a CP-SAT constraint count.
- SAT-specific `sat_nvars` and `sat_nclauses` remain unavailable (`null`).
- The status values `OPTIMAL`, `UNSAT`, and the adapter's other mappings are
  supported by the current benchmark status schema.

The adapter and schema also passed Python bytecode compilation with:

```powershell
.\.venv-cpsat\Scripts\python.exe -m py_compile `
  src/nqueens/cp_sat.py src/nqueens/benchmark_schema.py
```

## 5. Decision for the next step

**READY for a separately planned CP-SAT performance benchmark.** Correctness
for N=1..4 passed, the isolated dependency is available, and the adapter
preserves solver status semantics. Performance has not been run in this step.

Before performance execution, the benchmark should use a new output namespace,
retain `OPTIMAL` and `FEASIBLE` separately, leave unavailable CP-SAT metrics as
null, and record the OR-Tools version in run metadata where supported.

