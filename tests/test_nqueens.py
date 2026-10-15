import pytest
import csv
import json
from pathlib import Path
from nqueens.encoding import encode_nqueens
from nqueens.model import validate_solution
from nqueens.solver import solve
from nqueens.cp_sat import solve_cp_sat
from nqueens.cplex_mip import solve_cplex_mip
from nqueens.cplex_cp import solve_cplex_cp


@pytest.mark.parametrize("n,status", [(1, "SAT"), (2, "UNSAT"), (3, "UNSAT"), (4, "SAT")])
@pytest.mark.parametrize("encoding", ["pairwise", "sequential", "binary", "commander"])
def test_known_instances(n, status, encoding):
    result = solve(n, encoding, prefer_pysat=False)
    assert result.status == status
    if status == "SAT":
        assert validate_solution(result.solution, n)


def test_encoding_equivalence_small_instances():
    for n in range(1, 8):
        statuses = {solve(n, encoding, prefer_pysat=False).status for encoding in ["pairwise", "sequential", "binary", "commander"]}
        assert statuses == {"SAT" if n in {1, 4, 5, 6, 7} else "UNSAT"}


def test_new_encoding_formula_sizes_are_stable():
    assert (encode_nqueens(4, "binary")[0].nvars, encode_nqueens(4, "binary")[0].nclauses) == (32, 100)
    assert (encode_nqueens(4, "commander")[0].nvars, encode_nqueens(4, "commander")[0].nclauses) == (32, 116)


def test_invalid_inputs():
    with pytest.raises(ValueError):
        encode_nqueens(0)
    assert solve(4, "bogus", prefer_pysat=False).status == "ERROR"
    assert not validate_solution([0, 1], 2)


def test_timeout_is_not_reported_as_unsat():
    assert solve(16, "pairwise", timeout=0.0, prefer_pysat=False).status == "TIMEOUT"


def test_optional_cp_sat_reports_missing_dependency_honestly():
    result = solve_cp_sat(4, timeout=1)
    if result.status == "ERROR":
        assert "unavailable" in (result.error or "")
    else:
        assert result.status == "SAT"
        assert validate_solution(result.solution, 4)


def test_saved_benchmark_json_csv_schema_matches():
    json_path = Path("results/raw/benchmark_repeated.json")
    csv_path = Path("results/raw/benchmark_repeated.csv")
    if not json_path.exists() or not csv_path.exists():
        pytest.skip("generated benchmark artifact is not present")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    with csv_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert payload["schema_version"] == 2
    assert len(payload["records"]) == len(rows)
    assert {r["status"] for r in payload["records"]} == {r["status"] for r in rows}


@pytest.mark.parametrize("adapter", [solve_cplex_mip, solve_cplex_cp])
def test_cplex_adapters_smoke(adapter):
    result = adapter(4, timeout=5)
    if result.status == "ERROR" and result.error and "unavailable" in result.error:
        pytest.skip(result.error)
    assert result.status in {"SAT", "FEASIBLE"}
    assert validate_solution(result.solution, 4)
