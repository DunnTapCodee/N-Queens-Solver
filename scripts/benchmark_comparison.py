"""Run a comparable multi-solver N-Queens benchmark without overwriting old data."""
import argparse
import csv
import json
import platform
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

from nqueens.cplex_cp import solve_cplex_cp
from nqueens.cplex_mip import solve_cplex_mip
from nqueens.cp_sat import solve_cp_sat
from nqueens.solver import solve as solve_sat
from nqueens.gurobi import solve_gurobi


def solver_version(name: str) -> str | None:
    try:
        if name == "CPLEX MIP" or name == "CPLEX CP Optimizer":
            import cplex
            return getattr(cplex, "__version__", None) or ".".join(map(str, cplex.Cplex().get_version().split(".")[:3]))
        if name in {"PySAT/Glucose3", "PySAT/CaDiCaL"}:
            import pysat
            return getattr(pysat, "__version__", "unknown")
        if name == "Gurobi":
            import gurobipy
            return getattr(gurobipy, "__version__", None) or str(gurobipy.version())
        if name == "OR-Tools CP-SAT":
            import ortools
            return getattr(ortools, "__version__", "unknown")
    except Exception:
        return None
    return None


def availability() -> dict[str, dict[str, object]]:
    result = {}
    for label, module in (("CPLEX MIP", "docplex"), ("CPLEX CP Optimizer", "docplex"), ("Gurobi", "gurobipy"), ("OR-Tools CP-SAT", "ortools"), ("PySAT/Glucose3", "pysat"), ("PySAT/CaDiCaL", "pysat")):
        try:
            __import__(module)
            result[label] = {"installed": True, "usable": label in {"PySAT/Glucose3", "PySAT/CaDiCaL", "CPLEX MIP", "CPLEX CP Optimizer", "Gurobi"}, "version": solver_version(label), "note": "backend instantiation checked; benchmark status recorded separately"}
        except ImportError as exc:
            result[label] = {"installed": False, "usable": False, "version": None, "note": f"not installed: {exc}"}
    return result


def dispatch(name: str, n: int, encoding: str, timeout: float):
    if name in {"SAT", "SAT/Glucose3", "SAT/CaDiCaL"}:
        backend = "cadical195" if name == "SAT/CaDiCaL" else "glucose3"
        return solve_sat(n, encoding, timeout=timeout, prefer_pysat=True, sat_solver=backend)
    if name == "CPLEX MIP": return solve_cplex_mip(n, timeout)
    if name == "CPLEX CP Optimizer": return solve_cplex_cp(n, timeout)
    if name == "OR-Tools CP-SAT": return solve_cp_sat(n, timeout)
    if name == "Gurobi": return solve_gurobi(n, timeout)
    raise ValueError(f"unsupported solver: {name}")


def write_artifacts(out: Path, payload: dict) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    records = payload["records"]
    csv_path = out.with_suffix(".csv")
    fieldnames = list(records[0]) if records else ["solver", "status"]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames); writer.writeheader(); writer.writerows(records)


def make_summary(records: list[dict]) -> list[dict]:
    groups = {}
    for r in records: groups.setdefault((r["solver"], r["encoding"], r["n"]), []).append(r)
    result = []
    for (solver, encoding, n), group in groups.items():
        completed = [r["total_time_s"] for r in group if r["status"] in ("SAT", "UNSAT", "FEASIBLE", "OPTIMAL")]
        result.append({"n": n, "solver": solver, "encoding": encoding, "trials": len(group), "sat": sum(r["status"] == "SAT" for r in group), "unsat": sum(r["status"] == "UNSAT" for r in group), "feasible": sum(r["status"] == "FEASIBLE" for r in group), "optimal": sum(r["status"] == "OPTIMAL" for r in group), "timeouts": sum(r["status"] == "TIMEOUT" for r in group), "errors": sum(r["status"] == "ERROR" for r in group), "license_limits": sum(r["status"] == "LICENSE_LIMIT" for r in group), "median_total_time_s": statistics.median(completed) if completed else None, "mean_total_time_s": statistics.mean(completed) if completed else None, "stdev_total_time_s": statistics.stdev(completed) if len(completed) > 1 else None, "median_build_time_s": statistics.median(r["build_time_s"] for r in group), "median_solve_time_s": statistics.median(r["solve_time_s"] for r in group), "nvars": group[0]["nvars"], "nconstraints": group[0]["nconstraints"]})
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--solvers", nargs="+", default=["SAT/Glucose3", "CPLEX MIP", "CPLEX CP Optimizer"])
    parser.add_argument("--sizes", nargs="+", type=int, default=[1, 2, 3, 4, 8, 16, 32])
    parser.add_argument("--encodings", nargs="+", default=["pairwise", "sequential"])
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--output", default="results/raw/benchmark_comparison.json")
    args = parser.parse_args()
    if args.repetitions < 1: parser.error("--repetitions must be positive")
    records = []
    out = Path(args.output)
    meta = {"schema_version": 1, "timestamp_utc": datetime.now(timezone.utc).isoformat(), "python": sys.version, "platform": platform.platform(), "timeout_s": args.timeout, "repetitions": args.repetitions, "availability": availability()}
    write_artifacts(out, {"schema_version": 1, "metadata": meta, "records": records})
    for solver in args.solvers:
        encs = args.encodings if solver in {"SAT", "SAT/Glucose3", "SAT/CaDiCaL", "SAT"} else ["n/a"]
        for n in args.sizes:
            for encoding in encs:
                for trial in range(1, args.repetitions + 1):
                    started = perf_counter(); result = dispatch(solver, n, encoding, args.timeout); total = perf_counter() - started
                    record = {"instance": f"nqueens-{n}", "n": n, "method": solver, "solver": result.backend, "encoding": encoding, "trial": trial, "status": result.status, "raw_status": result.raw_status, "solver_version": solver_version(result.backend), "python": platform.python_version(), "timeout_s": args.timeout, "build_time_s": result.encoding_time, "solve_time_s": result.solve_time, "total_time_s": total, "nvars": result.nvars if encoding != "n/a" else None, "nclauses": result.nclauses if encoding != "n/a" else None, "nconstraints": result.nclauses, "solution_valid": result.solution is not None, "error": result.error}
                    records.append(record); write_artifacts(out, {"schema_version": 1, "metadata": meta, "records": records})
                    print(f"{solver:20} n={n:>3} enc={encoding:10} trial={trial} {result.status:7} total={total:.6f}s")
    summary = make_summary(records)
    out.with_name(out.stem + "_summary.json").write_text(json.dumps({"schema_version": 1, "metadata": meta, "summaries": summary}, indent=2), encoding="utf-8")
    print(f"completed records={len(records)}; summary={out.with_name(out.stem + '_summary.json')}")


if __name__ == "__main__": main()
