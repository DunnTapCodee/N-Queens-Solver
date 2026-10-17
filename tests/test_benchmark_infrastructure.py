from hashlib import sha256
from types import SimpleNamespace

import pytest

from nqueens.benchmark_schema import (
    ensure_output_available,
    manifest_entry,
    metric_fields,
    new_run_id,
    status_counts,
)


def result(status="SAT", backend="glucose3", error=None):
    return SimpleNamespace(
        status=status, backend=backend, error=error, raw_status="raw",
        nvars=10, nclauses=20, encoding_time=0.1, solve_time=0.2,
    )


def test_status_summary_keeps_feasible_and_optimal_separate():
    counts = status_counts([
        {"status": "SAT"}, {"status": "FEASIBLE"}, {"status": "OPTIMAL"},
        {"status": "TIMEOUT"}, {"status": "ERROR"}, {"status": "LICENSE_LIMIT"},
    ])
    assert counts["SAT"] == 1
    assert counts["FEASIBLE"] == 1
    assert counts["OPTIMAL"] == 1
    assert counts["TIMEOUT"] == counts["ERROR"] == counts["LICENSE_LIMIT"] == 1
    assert counts["UNSAT"] == 0


def test_unknown_status_is_not_silently_invented():
    with pytest.raises(ValueError):
        status_counts([{"status": "SUCCESS"}])


def test_metrics_do_not_infer_inapplicable_values():
    sat = metric_fields(result(), "pairwise")
    model = metric_fields(result("FEASIBLE", "cplex"), "n/a")
    assert sat["sat_nclauses"] == 20
    assert sat["model_nconstraints"] is None
    assert model["model_nconstraints"] == 20
    assert model["sat_nclauses"] is None


def test_output_guard_refuses_existing_path_unless_forced(tmp_path):
    existing = tmp_path / "result.json"
    existing.write_text("historical", encoding="utf-8")
    with pytest.raises(FileExistsError):
        ensure_output_available([existing])
    ensure_output_available([existing], force=True)
    assert existing.read_text(encoding="utf-8") == "historical"


def test_run_ids_are_unique():
    assert new_run_id() != new_run_id()


def test_manifest_reflects_fixture_backend_state():
    available = manifest_entry(result("FEASIBLE", "gurobi"))
    unavailable = manifest_entry(result("ERROR", "none", "backend unavailable"))
    assert available["installed_or_callable"] is True
    assert available["usable"] is True
    assert unavailable["installed_or_callable"] is False
    assert unavailable["usable"] is False


def test_json_and_csv_writer_use_same_fixture_records(tmp_path):
    from scripts.benchmark_comparison import write_artifacts
    from json import loads
    import csv

    output = tmp_path / "new.json"
    payload = {"schema_version": 1, "metadata": {"run_id": new_run_id()},
               "records": [{"n": 4, "status": "FEASIBLE", "solution_valid": True}]}
    write_artifacts(output, payload)
    json_records = loads(output.read_text(encoding="utf-8"))["records"]
    with output.with_suffix(".csv").open(newline="", encoding="utf-8") as handle:
        csv_records = list(csv.DictReader(handle))
    assert len(json_records) == len(csv_records) == 1
    assert csv_records[0]["n"] == str(json_records[0]["n"])
    assert csv_records[0]["status"] == json_records[0]["status"]


def test_historical_artifact_is_read_only():
    path = "results/raw/benchmark_repeated.json"
    before = sha256(open(path, "rb").read()).hexdigest()
    after = sha256(open(path, "rb").read()).hexdigest()
    assert before == after
