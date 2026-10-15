"""Validate correctness/performance matrix JSON and CSV artifacts."""
import csv
import json
from pathlib import Path


def check(path: Path):
    payload=json.loads(path.read_text(encoding="utf-8")); rows=payload["records"]
    with path.with_suffix(".csv").open(newline="",encoding="utf-8") as f: csv_rows=list(csv.DictReader(f))
    assert len(rows)==len(csv_rows)
    for a,b in zip(rows,csv_rows):
        for key in ["n","solver","encoding","trial","status","raw_status","solution_valid"]:
            assert str(a[key]).lower() == b[key].lower(), (key,a,b)
    assert all((r["solution_valid"] is True) == (r["status"] in {"SAT","FEASIBLE","OPTIMAL"}) for r in rows)
    return len(rows), rows


def main():
    root=Path(__file__).resolve().parents[1]; c,cr=check(root/"results/raw/benchmark_medium_correctness.json"); p,pr=check(root/"results/raw/benchmark_medium_performance.json")
    assert c==40 and p==87
    assert {r["n"] for r in cr}=={1,2,3,4}; assert {r["n"] for r in pr}=={4,8,16}
    assert all(sum(x["n"]==r["n"] and x["solver"]==r["solver"] and x["encoding"]==r["encoding"] for x in pr)==3 for r in pr if r["solver"] != "CPLEX MIP" or r["n"] < 16)
    print(f"correctness records={c}; performance records={p}; JSON/CSV and validation flags consistent")
    print("CPLEX MIP N=16 excluded by declared Community Edition limit")


if __name__ == "__main__": main()
