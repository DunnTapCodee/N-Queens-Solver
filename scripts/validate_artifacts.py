"""Validate the repeated benchmark artifacts and report references."""
import csv
import json
import re
from pathlib import Path
from statistics import median


ROOT = Path(__file__).resolve().parents[1]
raw = ROOT / "results/raw"


def main() -> None:
    json_payload = json.loads((raw / "benchmark_repeated.json").read_text(encoding="utf-8"))
    records = json_payload["records"]
    with (raw / "benchmark_repeated.csv").open(newline="", encoding="utf-8") as handle:
        csv_records = list(csv.DictReader(handle))
    assert len(records) == len(csv_records) == 80, (len(records), len(csv_records))
    fields = list(records[0])
    numeric_fields = {"n", "trial", "seed", "timeout_s", "encoding_time_s", "solve_time_s", "total_time_s", "nvars", "nclauses"}
    for left, right in zip(records, csv_records):
        for field in fields:
            if field in numeric_fields:
                assert abs(float(left[field]) - float(right[field])) < 1e-12, (field, left, right)
            elif field == "solution_valid":
                assert str(left[field]).lower() == right[field].lower(), (field, left, right)
            elif left[field] is None:
                assert right[field] == "", (field, left, right)
            else:
                assert str(left[field]) == right[field], (field, left, right)
    assert sorted({r["n"] for r in records}) == [1, 2, 3, 4, 8, 16, 32, 64]
    assert {r["encoding"] for r in records} == {"pairwise", "sequential"}
    assert all(sum(r["n"] == n and r["encoding"] == enc for r in records) == 5 for n in {r["n"] for r in records} for enc in {"pairwise", "sequential"})
    statuses = {status: sum(r["status"] == status for r in records) for status in ("SAT", "UNSAT", "TIMEOUT", "ERROR")}
    assert statuses == {"SAT": 60, "UNSAT": 20, "TIMEOUT": 0, "ERROR": 0}
    assert all(r["solution_valid"] is True for r in records if r["status"] == "SAT")
    assert all(r["solution_valid"] is False for r in records if r["status"] != "SAT")

    summary = json.loads((raw / "benchmark_repeated_summary.json").read_text(encoding="utf-8"))["summaries"]
    for row in summary:
        values = [r["total_time_s"] for r in records if r["n"] == row["n"] and r["encoding"] == row["encoding"] and r["solver"] == row["solver"] and r["status"] in ("SAT", "UNSAT")]
        assert abs(median(values) - row["median_total_time_s"]) < 1e-12

    report = (ROOT / "report/report.tex").read_text(encoding="utf-8")
    assert not re.search(r"\\\\(?:documentclass|usepackage|begin|end|section|includegraphics|url)", report)
    assert report.count("\\begin{figure}") == report.count("\\end{figure}") >= 2
    for figure in re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", report):
        assert (ROOT / "report" / figure).resolve().exists(), figure
    print(f"validated JSON/CSV records: {len(records)}")
    print(f"status counts: {statuses}")
    print("validated configurations: 8 sizes x 2 encodings x 5 trials")
    figure_count = len(re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", report))
    print(f"validated report syntax markers and {figure_count} referenced figures")


if __name__ == "__main__":
    main()
