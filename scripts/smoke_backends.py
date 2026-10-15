"""Smoke-test optional backends and write an explicit availability manifest."""
import json
from pathlib import Path
from nqueens.cplex_cp import solve_cplex_cp
from nqueens.cplex_mip import solve_cplex_mip
from nqueens.cp_sat import solve_cp_sat
from nqueens.gurobi import solve_gurobi
from nqueens.solver import solve


def main():
    checks = {}
    for name, fn in {
        "PySAT/Glucose3": lambda: solve(4, "sequential", timeout=10, sat_solver="glucose3"),
        "PySAT/CaDiCaL": lambda: solve(4, "sequential", timeout=10, sat_solver="cadical195"),
        "CPLEX MIP": lambda: solve_cplex_mip(4, 10),
        "CPLEX CP Optimizer": lambda: solve_cplex_cp(4, 10),
        "OR-Tools CP-SAT": lambda: solve_cp_sat(4, 1),
        "Gurobi": lambda: solve_gurobi(4, 1),
    }.items():
        result = fn()
        checks[name] = {"installed_or_callable": result.backend != "none" and "unavailable" not in (result.error or ""), "smoke_status": result.status, "raw_status": result.raw_status, "usable": result.status in {"SAT", "FEASIBLE", "OPTIMAL", "UNSAT"}, "error": result.error}
    out = Path("results/raw/backend_manifest.json"); out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps({"schema_version": 1, "checks": checks}, indent=2), encoding="utf-8")
    print(json.dumps(checks, indent=2))


if __name__ == "__main__": main()
