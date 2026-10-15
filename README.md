# Assignment 1 — SAT and Exact N-Queens Solvers

The project implements N-Queens with PySAT/Glucose3 using pairwise and Sinz sequential CNF encodings. It also provides optional adapters for CPLEX MIP, CPLEX CP Optimizer, OR-Tools CP-SAT, and Gurobi. Optional solvers are never silently replaced by another solver.

## Environment and tests

```powershell
python -m pip install -e .
$env:PYTHONPATH = "src"
python scripts/check_environment.py
python -m pytest -q
```

The verified environment has Python 3.11.9, PySAT, `cplex==22.2.0.1`, and `docplex==2.32.264`. Gurobi and OR-Tools are not installed. CPLEX Community Edition is usable for small models but enforces model-size limits.

## Benchmarks

Historical SAT-only artifacts are preserved:

```powershell
python scripts/benchmark.py --sizes 1 2 3 4 8 16 32 64 --repetitions 5 --timeout 10 --output results/raw/benchmark_repeated.json
python scripts/plot_results.py --input results/raw/benchmark_repeated_summary.json
python scripts/validate_artifacts.py
```

The multi-solver benchmark writes new files and does not overwrite the SAT history:

```powershell
python scripts/benchmark_comparison.py --solvers SAT "CPLEX MIP" "CPLEX CP Optimizer" --sizes 1 2 3 4 8 16 --repetitions 3 --timeout 10 --output results/raw/benchmark_comparison.json
python scripts/plot_comparison.py
python scripts/validate_comparison.py
```

The comparison benchmark records SAT, UNSAT, TIMEOUT, and ERROR separately. Timeouts and errors are not included in successful-runtime medians. At N=16, the CPLEX MIP Community Edition model limit is recorded as ERROR rather than being misreported as timeout or UNSAT.

The approved medium matrix is generated separately and does not overwrite historical artifacts:

```powershell
python scripts/smoke_backends.py
python scripts/benchmark_medium_matrix.py --repetitions 3 --timeout 10
python scripts/plot_medium_matrix.py
python scripts/validate_medium_matrix.py
```

It covers Pairwise, Sequential, Binary, and Commander with Glucose3 and
CaDiCaL, plus CPLEX MIP and CP Optimizer, using N=1,2,3,4 for correctness and
N=4,8,16 for performance. CPLEX MIP is intentionally omitted at N=16 after
its verified Community Edition limit; this is recorded in the artifact
metadata rather than represented as a solver failure.

## Artifacts and report

- Historical SAT data: `results/raw/benchmark_repeated.*`
- Comparison data: `results/raw/benchmark_comparison.*`
- SAT figures: `results/figures/`
- Comparison figures: `results/figures/comparison/`
- Report source: `report/report.tex`

Compile the report with the Elsevier `cas-sc.cls` template and a LaTeX distribution. The current environment has no LaTeX compiler or `cas-sc.cls`, so compilation must be performed in an appropriately configured environment.

Repository remote: `https://github.com/DunnTapCodee/N-Queens-Solver`
