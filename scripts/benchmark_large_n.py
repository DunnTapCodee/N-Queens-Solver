"""Resumable, subprocess-isolated large-N benchmark runner.

This runner is intentionally separate from the historical benchmark scripts.
It is an execution tool only; importing it never runs a solver.
"""
from __future__ import annotations

import argparse
import csv
import json
import multiprocessing as mp
import platform
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from nqueens.benchmark_schema import (  # noqa: E402
    SUPPORTED_STATUSES, ensure_output_available, metric_fields, new_run_id,
    status_counts,
)
from nqueens.model import validate_solution  # noqa: E402

DEFAULT_SOLVERS = ["SAT/Glucose3", "SAT/CaDiCaL", "OR-Tools CP-SAT"]
DEFAULT_SIZES = [128, 256, 512, 1024]
SAT_SOLVERS = {"SAT/Glucose3", "SAT/CaDiCaL"}


def trial_key(record: dict) -> tuple:
    return (record["solver"], record["encoding"], int(record["n"]), int(record["trial"]))


def _child_worker(solver: str, n: int, encoding: str, timeout: float, queue) -> None:
    try:
        from scripts.benchmark_comparison import dispatch
        result = dispatch(solver, n, encoding, timeout)
        queue.put({"status": result.status, "solution": result.solution,
                   "encoding_time": result.encoding_time, "solve_time": result.solve_time,
                   "nvars": result.nvars, "nclauses": result.nclauses,
                   "backend": result.backend, "error": result.error,
                   "raw_status": result.raw_status})
    except BaseException as exc:  # communicate child import/license failures
        queue.put({"status": "ERROR", "solution": None, "encoding_time": None,
                   "solve_time": None, "nvars": None, "nclauses": None,
                   "backend": "none", "error": f"{type(exc).__name__}: {exc}",
                   "raw_status": type(exc).__name__})


def run_isolated(solver: str, n: int, encoding: str, timeout: float) -> tuple[dict, float]:
    """Run one adapter in a spawned child; timeout covers construction too."""
    context = mp.get_context("spawn")
    queue = context.Queue(1)
    process = context.Process(target=_child_worker, args=(solver, n, encoding, timeout, queue))
    started = perf_counter()
    process.start()
    process.join(timeout)
    elapsed = perf_counter() - started
    if process.is_alive():
        process.terminate()
        process.join(2.0)
        if process.is_alive() and hasattr(process, "kill"):
            process.kill()
            process.join()
        return ({"status": "TIMEOUT", "solution": None, "encoding_time": None,
                 "solve_time": None, "nvars": None, "nclauses": None,
                 "backend": solver, "error": "parent deadline exceeded (construction or solve)",
                 "raw_status": "PARENT_TIMEOUT"}, elapsed)
    if not queue.empty():
        return queue.get(), elapsed
    return ({"status": "ERROR", "solution": None, "encoding_time": None,
             "solve_time": None, "nvars": None, "nclauses": None,
             "backend": solver, "error": f"child exited with code {process.exitcode}",
             "raw_status": "CHILD_EXIT"}, elapsed)


def make_record(solver: str, n: int, encoding: str, trial: int, timeout: float,
                result: dict, elapsed: float) -> dict:
    status = result["status"]
    solution = result.get("solution")
    valid = validate_solution(solution, n) if solution is not None else None
    error = result.get("error")
    if status in {"SAT", "FEASIBLE", "OPTIMAL"} and not valid:
        error = (error + "; " if error else "") + "independent validation failed"
        status, result["raw_status"] = "ERROR", result.get("status")
    is_sat = encoding != "n/a"
    record = {
        "instance": f"nqueens-{n}", "n": n, "method": solver,
        "solver": result.get("backend", solver), "encoding": encoding, "trial": trial,
        "status": status, "raw_status": result.get("raw_status"),
        "timeout_s": timeout, "build_time_s": result.get("encoding_time"),
        "solve_time_s": result.get("solve_time"), "total_time_s": elapsed,
        "nvars": result.get("nvars") if is_sat else None,
        "nclauses": result.get("nclauses") if is_sat else None,
        "nconstraints": None if is_sat else result.get("nclauses"),
        "solution_valid": valid, "validator": "nqueens.model.validate_solution" if solution is not None else None,
        "solution": solution, "error": error,
    }
    record.update(metric_fields(type("Result", (), {
        "encoding_time": result.get("encoding_time"), "solve_time": result.get("solve_time"),
        "nvars": result.get("nvars"), "nclauses": result.get("nclauses"),
    })(), encoding))
    return record


def write_outputs(output: Path, metadata: dict, records: list[dict]) -> None:
    payload = {"schema_version": 1, "metadata": metadata, "records": records}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    fields = list(records[0]) if records else ["n", "solver", "encoding", "trial", "status"]
    with output.with_suffix(".csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)
    summaries = []
    groups = {}
    for record in records:
        groups.setdefault((record["solver"], record["encoding"], record["n"]), []).append(record)
    for (solver, encoding, n), group in sorted(groups.items(), key=str):
        completed = [r["total_time_s"] for r in group
                     if r["status"] in {"SAT", "FEASIBLE", "OPTIMAL", "UNSAT"}
                     and r["total_time_s"] is not None]
        summaries.append({"solver": solver, "encoding": encoding, "n": n,
                          "trials": len(group), "status_counts": status_counts(group),
                          "valid_solutions": sum(r["solution_valid"] is True for r in group),
                          "median_total_time_s": statistics.median(completed) if completed else None,
                          "mean_total_time_s": statistics.mean(completed) if completed else None,
                          "stdev_total_time_s": statistics.stdev(completed) if len(completed) > 1 else None})
    output.with_name(output.stem + "_summary.json").write_text(
        json.dumps({"schema_version": 1, "metadata": metadata, "summaries": summaries}, indent=2),
        encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Safe resumable large-N N-Queens benchmark")
    parser.add_argument("--sizes", nargs="+", type=int, default=DEFAULT_SIZES)
    parser.add_argument("--solvers", nargs="+", default=DEFAULT_SOLVERS)
    parser.add_argument("--encodings", nargs="+", default=["sequential"])
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=100.0)
    parser.add_argument("--global-budget", type=float, default=8 * 60 * 60)
    parser.add_argument("--output", type=Path, default=Path("results/large_n/large_n.json"))
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.repetitions < 1 or args.timeout <= 0 or args.global_budget <= 0:
        raise SystemExit("repetitions, timeout, and global budget must be positive")
    output = args.output
    summary = output.with_name(output.stem + "_summary.json")
    csv_output = output.with_suffix(".csv")
    records: list[dict] = []
    metadata = None
    if args.resume:
        if not output.exists():
            raise SystemExit(f"--resume requires an existing JSON artifact: {output}")
        existing = json.loads(output.read_text(encoding="utf-8"))
        records = existing.get("records", [])
        metadata = existing.get("metadata") or {}
    else:
        ensure_output_available((output, csv_output, summary))
    if metadata is None:
        metadata = {"run_id": new_run_id(), "created_utc": datetime.now(timezone.utc).isoformat(),
                    "python": sys.version, "platform": platform.platform(), "sizes": args.sizes,
                    "solvers": args.solvers, "encodings": args.encodings, "repetitions": args.repetitions,
                    "timeout_s": args.timeout, "global_budget_s": args.global_budget,
                    "memory_limit_enforced": False, "subprocess_timeout_includes_construction": True}
    else:
        metadata["resumed_utc"] = datetime.now(timezone.utc).isoformat()
    started = perf_counter()
    completed = {trial_key(r) for r in records}
    stop_reason = None
    for solver in args.solvers:
        encodings = args.encodings if solver in SAT_SOLVERS else ["n/a"]
        for n in args.sizes:
            for encoding in encodings:
                for trial in range(1, args.repetitions + 1):
                    key = (solver, encoding, n, trial)
                    if key in completed:
                        continue
                    if perf_counter() - started >= args.global_budget:
                        stop_reason = "GLOBAL_DEADLINE"
                        break
                    result, elapsed = run_isolated(solver, n, encoding, args.timeout)
                    record = make_record(solver, n, encoding, trial, args.timeout, result, elapsed)
                    records.append(record); completed.add(key)
                    write_outputs(output, metadata, records)
                    print(f"{solver} n={n} enc={encoding} trial={trial} {record['status']} {elapsed:.3f}s")
                if stop_reason: break
            if stop_reason: break
        if stop_reason: break
    metadata["stopped_reason"] = stop_reason
    write_outputs(output, metadata, records)
    print(f"records={len(records)} output={output}")


if __name__ == "__main__":
    main()
