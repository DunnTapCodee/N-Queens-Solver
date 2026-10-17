# P2 data audit

## Scope

This audit reads the P1 JSON, CSV, and summary artifacts only. No solver or
benchmark was run. The six complete P1 families contain 300 records. The two
DPLL recovery artifacts are inspected but excluded from the complete P1
population.

## VERIFIED findings

- Complete artifacts are `glucose3.json` (100), `cadical195.json` (100),
  `dpll_final.json` (40), `cplex_mip.json` (10), `cplex_cp.json` (25), and
  `gurobi.json` (25).
- Final-family N values are exactly the plan: SAT families N=4,8,16,32,64;
  DPLL N=4,8; CPLEX MIP N=4,8; CP Optimizer and Gurobi N=4,8,16,32,64.
- Each complete cell has five trials. The final population has 250 `SAT` and
  50 `FEASIBLE` records; it has no `UNSAT`, `OPTIMAL`, `TIMEOUT`, `ERROR`, or
  `LICENSE_LIMIT` records.
- Every complete JSON has a matching CSV with the same record count and the
  same record keys after normalizing JSON nulls to empty CSV cells.
- Every complete summary matches the raw JSON per `(solver, encoding, N)` for
  trial count and each normalized status count.
- All 300 non-null solutions have `solution_valid=true` from
  `nqueens.model.validate_solution`, as recorded by the P1 runner.
- `dpll.json` is a separate 15-record initial configuration failure: all
  records are `ERROR` with `encoding=n/a` and solver `none`.
- `dpll_v2.json` is a separate 44-record partial run: 40 SAT records and four
  N=16 TIMEOUT records. It is incomplete and excluded from final P1 tables.

## WARNING findings

- The performance matrix uses only satisfiable N values. It supports SAT or
  FEASIBLE runtime analysis, but not UNSAT performance analysis.
- `FEASIBLE` from CP Optimizer and Gurobi is not `OPTIMAL`; no final P1 record
  has `OPTIMAL` status.
- SAT backend/encoding comparisons are the strongest direct comparisons:
  same N, same encoding family, five trials, same timeout, and the same total
  time field. They remain descriptive because solver implementations differ.
- CP/MIP/Gurobi are separate model families. CPLEX MIP has only N=4,8 because
  the known Community Edition size limit excluded N>=16. Its curve must not be
  treated as a complete N=4..64 comparison.
- Construction/build and solver timing fields exist, but total time is an
  outer wall-clock measurement and is not guaranteed to equal their sum.
  SAT construction is CNF encoding; model-family build time is adapter/model
  construction. Cross-paradigm timing claims are therefore limited.
- `nclauses` and `nconstraints` retain legacy meanings and are not universally
  interchangeable. New explicit aliases are safer: SAT uses
  `sat_nvars`/`sat_nclauses`; model adapters use `model_nvars`/
  `model_nconstraints`.
- Peak memory, CPU utilization, thread count, and a universal solver build
  version are absent. PySAT package version is in metadata, while its
  per-record `solver_version` is null.
- Runtime plots use medians of completed records only. TIMEOUT/ERROR are
  counted in status tables and are never replaced by zero or a fabricated
  runtime.

## UNKNOWN findings

- The artifacts do not independently preserve a source revision or dependency
  lock for each run, so exact code/environment identity beyond recorded
  metadata cannot be reconstructed.
- A direct cross-paradigm ranking cannot be established from these artifacts
  without a common timing and formulation protocol.
- The final performance set does not reveal UNSAT scaling beyond the separate
  N=3 smoke test.

## Metric definitions observed in source and artifacts

| Field | Observed meaning | Applicability |
|---|---|---|
| `build_time_s` / `construction_time_s` | Adapter construction time for CP/MIP/Gurobi; CNF encoding time for SAT | Available in all P1 records |
| `solve_time_s` / `solver_time_s` | Backend solver-call interval after construction | Available in all P1 records |
| `total_time_s` | Outer elapsed time around adapter dispatch | Available in all P1 records |
| `nvars` | CNF variables for SAT; model variables for CP/MIP adapters | Meaning depends on family |
| `nclauses` | CNF clauses for SAT; legacy container for model constraint count in adapters | Do not compare across families |
| `nconstraints` | Legacy result field; populated from `SolveResult.nclauses` | Ambiguous; use explicit aliases |
| `sat_nvars`, `sat_nclauses` | Explicit SAT formulation metrics | SAT only; null for model families |
| `model_nvars`, `model_nconstraints` | Explicit model formulation metrics | CP/MIP/Gurobi only; null for SAT |
| `solution_valid` | Independent validator result for non-null solutions | Null when no solution is returned |

## Fair analysis groups

1. Glucose3 by encoding and N.
2. CaDiCaL by encoding and N.
3. Glucose3 versus CaDiCaL only within the same encoding and N.
4. DPLL final N=4,8 by encoding, as a separate fallback baseline.
5. CPLEX MIP N=4,8 as its own binary-cell formulation.
6. CPLEX CP Optimizer N=4..64 as its own integer-column formulation.
7. Gurobi N=4..64 as its own binary-cell formulation.

The P2/P3 outputs use these groups and do not produce one combined ranking.
