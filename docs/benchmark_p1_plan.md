# P1 controlled benchmark plan

## Compatibility audit

The source currently implements four SAT encodings: `pairwise`, `sequential`,
`binary`, and `commander`. There is no recursive 2-Product encoding. PySAT
dispatches `glucose3` and `cadical195`; the internal DPLL path is selected
explicitly with `prefer_pysat=False`. CPLEX MIP, CPLEX CP Optimizer, and
Gurobi use their existing `n/a` model formulation rather than a SAT encoding.
OR-Tools is excluded because the smoke test found the dependency unavailable.

The six supported P1 families are therefore:

1. PySAT/Glucose3 × four SAT encodings;
2. PySAT/CaDiCaL × four SAT encodings;
3. DPLL fallback × four SAT encodings;
4. CPLEX MIP × its binary cell model;
5. CPLEX CP Optimizer × its integer-column model;
6. Gurobi × its binary cell model.

No model solver is forced to run a SAT encoding, and no SAT encoding is
pretended to be available for a CP/MIP formulation.

## Performance matrix

The performance sizes are `N = 4, 8, 16, 32, 64`, with five repetitions and
a 10-second timeout per solver call. Outputs are written below a new
`results/p1/` namespace, with one JSON/CSV/summary family per compatible
backend group. Each family receives its own run ID and refuses an existing
output path.

| Family | Encodings | Sizes | Repetitions | Planned records |
|---|---|---|---:|---:|
| PySAT/Glucose3 | pairwise, sequential, binary, commander | 4,8,16,32,64 | 5 | 100 |
| PySAT/CaDiCaL | pairwise, sequential, binary, commander | 4,8,16,32,64 | 5 | 100 |
| DPLL fallback | pairwise, sequential, binary, commander | 4,8 | 5 | 40 |
| CPLEX MIP | n/a, binary cell formulation | 4,8 | 5 | 10 |
| CPLEX CP Optimizer | n/a, integer-column formulation | 4,8,16,32,64 | 5 | 25 |
| Gurobi | n/a, binary cell formulation | 4,8,16,32,64 | 5 | 25 |

Planned total: **300 records**. The CPLEX MIP N=16 and above cells are
excluded before execution because the project has already observed the
Community Edition model-size/license limit at N=16. This is recorded as an
exclusion, not as an algorithmic timeout or failure. DPLL is limited to N=16
for this controlled run because it is a fallback baseline with rapidly
increasing search cost. An initial N=16 attempt reached repeated 10-second
timeouts and was stopped; N=16/32/64 are therefore explicitly excluded from
the complete DPLL family rather than silently omitted.

## Correctness and status rules

Every returned solution is checked with
`nqueens.model.validate_solution`. The artifact records the validator result
separately from solution presence. `SAT`, `UNSAT`, `FEASIBLE`, `OPTIMAL`,
`TIMEOUT`, `ERROR`, and `LICENSE_LIMIT` remain distinct. For CP Optimizer and
Gurobi, `FEASIBLE` is not relabeled as `OPTIMAL`.

Construction/build time, solver-call time, total time, and formulation size
fields are retained as provided by each adapter. SAT CNF aliases and model
constraint aliases are kept separate; unavailable or inapplicable metrics are
null. Peak memory is not measured by the current infrastructure.

## Execution commands

Each command uses the existing comparison runner and a new output path:

```text
$env:PYTHONPATH='src'
python scripts/benchmark_comparison.py --solvers SAT/Glucose3 --sizes 4 8 16 32 64 --encodings pairwise sequential binary commander --repetitions 5 --timeout 10 --output results/p1/glucose3.json
python scripts/benchmark_comparison.py --solvers SAT/CaDiCaL --sizes 4 8 16 32 64 --encodings pairwise sequential binary commander --repetitions 5 --timeout 10 --output results/p1/cadical195.json
python scripts/benchmark_comparison.py --solvers "DPLL fallback" --sizes 4 8 --encodings pairwise sequential binary commander --repetitions 5 --timeout 10 --output results/p1/dpll_final.json
python scripts/benchmark_comparison.py --solvers "CPLEX MIP" --sizes 4 8 --repetitions 5 --timeout 10 --output results/p1/cplex_mip.json
python scripts/benchmark_comparison.py --solvers "CPLEX CP Optimizer" --sizes 4 8 16 32 64 --repetitions 5 --timeout 10 --output results/p1/cplex_cp.json
python scripts/benchmark_comparison.py --solvers Gurobi --sizes 4 8 16 32 64 --repetitions 5 --timeout 10 --output results/p1/gurobi.json
```

These are smoke-validated backend families, not a claim that all runs will
finish successfully. Errors and license limits must remain as records if they
occur. No historical file is an input to the new summaries.
