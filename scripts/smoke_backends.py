"""Smoke-test optional backends and write an explicit availability manifest."""
import argparse
import json
from pathlib import Path
from nqueens.cplex_cp import solve_cplex_cp
from nqueens.cplex_mip import solve_cplex_mip
from nqueens.cp_sat import solve_cp_sat
from nqueens.gurobi import solve_gurobi
from nqueens.solver import solve
from nqueens.benchmark_schema import ensure_output_available, new_run_id
from nqueens.model import validate_solution


def check_case(result, n):
    has_solution = result.solution is not None
    solution_valid = validate_solution(result.solution, n) if has_solution else None
    return {
        "status": result.status,
        "raw_status": result.raw_status,
        "solution_valid": solution_valid,
        "error": result.error,
        "backend": result.backend,
    }


def check_backend(run_case):
    cases = {}
    for label, n in (("SAT_n4", 4), ("UNSAT_n3", 3)):
        try:
            cases[label] = check_case(run_case(n), n)
        except Exception as exc:
            cases[label] = {
                "status": "ERROR",
                "raw_status": type(exc).__name__,
                "solution_valid": None,
                "error": f"{type(exc).__name__}: {exc}",
                "backend": "none",
            }
    usable_cases = [case for case in cases.values() if case["backend"] != "none" and "unavailable" not in (case["error"] or "").lower()]
    detected = bool(usable_cases)
    initialized = bool(usable_cases)
    operational_error = next((case["error"] for case in cases.values() if case["status"] in {"ERROR", "TIMEOUT", "LICENSE_LIMIT"} and case["error"]), None)
    return {
        "detected": detected,
        "initialized": initialized,
        "sat_case": cases["SAT_n4"],
        "unsat_case": cases["UNSAT_n3"],
        "sat_solved": cases["SAT_n4"]["status"] in {"SAT", "FEASIBLE", "OPTIMAL"} and cases["SAT_n4"]["solution_valid"] is True,
        "unsat_confirmed": cases["UNSAT_n3"]["status"] == "UNSAT" and cases["UNSAT_n3"]["solution_valid"] is None,
        "error": operational_error,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="results/raw/backend_manifest.json")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    out = Path(args.output)
    ensure_output_available((out,), args.force)
    checks = {}
    for name, fn in {
        "PySAT/Glucose3": lambda n: solve(n, "sequential", timeout=10, sat_solver="glucose3"),
        "PySAT/CaDiCaL": lambda n: solve(n, "sequential", timeout=10, sat_solver="cadical195"),
        "DPLL fallback": lambda n: solve(n, "sequential", timeout=10, prefer_pysat=False),
        "CPLEX MIP": lambda n: solve_cplex_mip(n, 10),
        "CPLEX CP Optimizer": lambda n: solve_cplex_cp(n, 10),
        "OR-Tools CP-SAT": lambda n: solve_cp_sat(n, 1),
        "Gurobi": lambda n: solve_gurobi(n, 1),
    }.items():
        checks[name] = check_backend(fn)
    out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps({"schema_version": 2, "run_id": new_run_id(), "encoding": "sequential", "cases": {"SAT": {"n": 4}, "UNSAT": {"n": 3}}, "checks": checks}, indent=2), encoding="utf-8")
    print(json.dumps(checks, indent=2))


if __name__ == "__main__": main()
