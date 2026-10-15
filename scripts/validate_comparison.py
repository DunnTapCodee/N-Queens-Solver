"""Validate the multi-solver benchmark without treating errors as timeouts."""
import csv
import json
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    path = root / "results/raw/benchmark_comparison.json"
    payload = json.loads(path.read_text(encoding="utf-8")); records = payload["records"]
    with path.with_suffix(".csv").open(newline="", encoding="utf-8") as handle:
        csv_records = list(csv.DictReader(handle))
    assert len(records) == len(csv_records) == 72
    assert all(str(a["n"]) == b["n"] and a["solver"] == b["solver"] and a["status"] == b["status"] and str(a["trial"]) == b["trial"] for a,b in zip(records,csv_records))
    assert all(r["solution_valid"] for r in records if r["status"] in {"SAT", "FEASIBLE", "OPTIMAL"})
    assert all(not r["solution_valid"] for r in records if r["status"] not in {"SAT", "FEASIBLE", "OPTIMAL"})
    counts = {}
    for r in records: counts.setdefault(r["solver"], {}).setdefault(r["status"], 0); counts[r["solver"]][r["status"]] += 1
    summary = json.loads((root / "results/raw/benchmark_comparison_summary.json").read_text(encoding="utf-8"))["summaries"]
    assert summary
    print(f"validated comparison records: {len(records)}")
    print(json.dumps(counts, indent=2))
    print("availability:", json.dumps(payload["metadata"]["availability"], indent=2))


if __name__ == "__main__": main()
