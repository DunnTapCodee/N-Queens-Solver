from scripts.benchmark_large_n import make_record, trial_key, write_outputs


def test_invalid_solution_downgrades_solver_success_to_error():
    record = make_record("SAT/Glucose3", 4, "sequential", 1, 100.0,
                         {"status": "SAT", "solution": [0, 0, 0, 0],
                          "encoding_time": 1.0, "solve_time": 2.0, "nvars": 4,
                          "nclauses": 3, "backend": "PySAT/glucose3", "raw_status": "True"}, 3.0)
    assert record["status"] == "ERROR"
    assert record["solution_valid"] is False


def test_resume_identity_and_nullable_timeout_metrics():
    record = {"solver": "SAT/Glucose3", "encoding": "sequential", "n": 128, "trial": 1,
              "status": "TIMEOUT", "total_time_s": 100.0}
    assert trial_key(record) == ("SAT/Glucose3", "sequential", 128, 1)


def test_writer_keeps_json_csv_and_status_summary_consistent(tmp_path):
    output = tmp_path / "large.json"
    records = [{"solver": "OR-Tools CP-SAT", "encoding": "n/a", "n": 128, "trial": 1,
                "status": "FEASIBLE", "solution_valid": True, "total_time_s": 2.0}]
    write_outputs(output, {"run_id": "test"}, records)
    assert output.exists() and output.with_suffix(".csv").exists()
    summary = output.with_name("large_summary.json")
    assert summary.exists()
    assert '"FEASIBLE": 1' in summary.read_text(encoding="utf-8")
