"""Correctness and medium performance matrices for the approved scope."""
import argparse
import csv
import json
import platform
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from scripts.benchmark_comparison import dispatch, solver_version
from nqueens.benchmark_schema import ensure_output_available, metric_fields, new_run_id


def call(solver, n, encoding, timeout):
    return dispatch(solver, n, encoding, timeout)


def record(solver, n, encoding, trial, timeout):
    started = perf_counter(); result = call(solver, n, encoding, timeout); total = perf_counter() - started
    row = {"instance": f"nqueens-{n}", "n": n, "method": solver, "solver": result.backend, "encoding": encoding, "trial": trial, "status": result.status, "raw_status": result.raw_status, "solver_version": solver_version(result.backend), "python": platform.python_version(), "timeout_s": timeout, "build_time_s": result.encoding_time, "solve_time_s": result.solve_time, "total_time_s": total, "nvars": result.nvars, "nclauses": result.nclauses if encoding != "n/a" else None, "nconstraints": result.nclauses, "solution_valid": result.solution is not None, "error": result.error}
    row.update(metric_fields(result, encoding))
    return row


def save(path, records, metadata, summaries=None):
    payload = {"schema_version": 2, "metadata": metadata, "records": records}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    with path.with_suffix(".csv").open("w", newline="", encoding="utf-8") as f:
        fields = list(records[0]) if records else ["status"]; w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(records)
    if summaries is not None: path.with_name(path.stem + "_summary.json").write_text(json.dumps({"schema_version": 2, "metadata": metadata, "summaries": summaries}, indent=2), encoding="utf-8")


def summarize(records):
    groups={}
    for r in records: groups.setdefault((r["solver"],r["encoding"],r["n"]),[]).append(r)
    out=[]
    for (solver,encoding,n), rows in groups.items():
        times=[r["total_time_s"] for r in rows if r["status"] in {"SAT","UNSAT","FEASIBLE","OPTIMAL"}]
        out.append({"solver":solver,"encoding":encoding,"n":n,"trials":len(rows),"statuses":{s:sum(r["status"]==s for r in rows) for s in ["SAT","UNSAT","FEASIBLE","OPTIMAL","TIMEOUT","ERROR","LICENSE_LIMIT"]},"median_total_time_s":statistics.median(times) if times else None,"median_build_time_s":statistics.median(r["build_time_s"] for r in rows),"median_solve_time_s":statistics.median(r["solve_time_s"] for r in rows),"nvars":rows[0]["nvars"],"nclauses":rows[0]["nclauses"],"nconstraints":rows[0]["nconstraints"]})
    return out


def main():
    p=argparse.ArgumentParser(); p.add_argument("--repetitions",type=int,default=3); p.add_argument("--timeout",type=float,default=10); p.add_argument("--output-dir",default="results/raw"); p.add_argument("--force",action="store_true"); a=p.parse_args()
    output_dir = Path(a.output_dir)
    paths = [output_dir / f"benchmark_medium_{name}.json" for name in ("correctness", "performance")]
    paths += [path.with_suffix(".csv") for path in paths]
    paths += [path.with_name(path.stem + "_summary.json") for path in paths[:2]]
    ensure_output_available(paths, a.force)
    run_id = new_run_id()
    meta={"scope":"approved medium matrix","schema_version":2,"run_id":run_id,"timestamp_utc":datetime.now(timezone.utc).isoformat(),"python":sys.version,"platform":platform.platform(),"timeout_s":a.timeout,"repetitions":a.repetitions,"excluded": {"CPLEX MIP": "N=16 omitted after verified Community Edition limit"}}
    correct=[]
    configs=[("SAT/Glucose3",["pairwise","sequential","binary","commander"]),("SAT/CaDiCaL",["pairwise","sequential","binary","commander"]),("CPLEX MIP",["n/a"]),("CPLEX CP Optimizer",["n/a"])]
    for solver,encodings in configs:
        for n in [1,2,3,4]:
            for enc in encodings: correct.append(record(solver,n,enc,1,a.timeout))
    save(output_dir / "benchmark_medium_correctness.json",correct,meta,summarize(correct))
    perf=[]
    for solver, encodings in configs:
        sizes=[4,8,16] if solver != "CPLEX MIP" else [4,8]
        for n in sizes:
            for enc in encodings:
                for trial in range(1,a.repetitions+1): perf.append(record(solver,n,enc,trial,a.timeout))
    save(output_dir / "benchmark_medium_performance.json",perf,meta,summarize(perf))
    print(f"correctness records={len(correct)} performance records={len(perf)}")


if __name__ == "__main__": main()
