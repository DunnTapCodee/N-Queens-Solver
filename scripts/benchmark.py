import argparse
import csv
import json
import platform
import sys
import statistics
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from nqueens.solver import solve


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", nargs="+", type=int, default=[1, 2, 3, 4, 8, 16, 32])
    parser.add_argument("--encodings", nargs="+", default=["pairwise", "sequential"])
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--output", default="results/raw/benchmark.json")
    parser.add_argument("--repetitions", type=int, default=1)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    if args.repetitions < 1:
        parser.error("--repetitions must be positive")
    records = []
    for n in args.sizes:
        for encoding in args.encodings:
            for trial in range(1, args.repetitions + 1):
                result = solve(n, encoding, timeout=args.timeout, prefer_pysat=True)
                records.append({
                    "instance": f"nqueens-{n}", "n": n, "method": "SAT",
                    "encoding": encoding, "solver": result.backend, "status": result.status,
                    "trial": trial, "seed": args.seed,
                    "timeout_s": args.timeout, "python": platform.python_version(),
                    "encoding_time_s": result.encoding_time, "solve_time_s": result.solve_time,
                    "total_time_s": result.encoding_time + result.solve_time,
                    "nvars": result.nvars, "nclauses": result.nclauses,
                    "solution_valid": result.solution is not None,
                    "error": result.error,
                })
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema_version": 2, "metadata": {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "python": sys.version, "platform": platform.platform(), "timeout_s": args.timeout, "repetitions": args.repetitions, "seed": args.seed}, "records": records}
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    csv_out = out.with_suffix(".csv")
    with csv_out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=records[0].keys())
        writer.writeheader(); writer.writerows(records)
    summaries = []
    groups = {}
    for record in records:
        groups.setdefault((record["n"], record["encoding"], record["solver"]), []).append(record)
    for (n, encoding, solver), group in groups.items():
        successful = [r["total_time_s"] for r in group if r["status"] in ("SAT", "UNSAT")]
        summaries.append({"n": n, "encoding": encoding, "solver": solver, "trials": len(group), "sat": sum(r["status"] == "SAT" for r in group), "unsat": sum(r["status"] == "UNSAT" for r in group), "timeouts": sum(r["status"] == "TIMEOUT" for r in group), "errors": sum(r["status"] == "ERROR" for r in group), "median_total_time_s": statistics.median(successful) if successful else None, "mean_total_time_s": statistics.mean(successful) if successful else None, "stdev_total_time_s": statistics.stdev(successful) if len(successful) > 1 else None, "min_total_time_s": min(successful) if successful else None, "max_total_time_s": max(successful) if successful else None, "median_encoding_time_s": statistics.median(r["encoding_time_s"] for r in group), "median_solve_time_s": statistics.median(r["solve_time_s"] for r in group), "nvars": group[0]["nvars"], "nclauses": group[0]["nclauses"]})
    summary_path = out.with_name(out.stem + "_summary.json")
    summary_path.write_text(json.dumps({"schema_version": 2, "metadata": payload["metadata"], "summaries": summaries}, indent=2), encoding="utf-8")
    print(json.dumps(payload["metadata"], indent=2))
    for summary in summaries:
        print(f"n={summary['n']:>3} {summary['encoding']:10} trials={summary['trials']} SAT={summary['sat']} UNSAT={summary['unsat']} TIMEOUT={summary['timeouts']} median={summary['median_total_time_s']}")


if __name__ == "__main__":
    main()
