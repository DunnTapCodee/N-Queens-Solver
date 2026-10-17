"""Optional OR-Tools CP-SAT adapter; import remains lazy and explicit."""
from time import perf_counter
from .model import validate_solution
from .solver import SolveResult


def solve_cp_sat(n: int, timeout: float | None = None, seed: int = 0) -> SolveResult:
    started = perf_counter()
    try:
        from ortools.sat.python import cp_model  # type: ignore
    except ImportError as exc:
        return SolveResult("ERROR", None, 0.0, 0.0, 0, None, "OR-Tools CP-SAT", f"dependency unavailable: {exc}")
    try:
        model = cp_model.CpModel()
        queens = [model.NewIntVar(0, n - 1, f"q_{r}") for r in range(n)]
        model.AddAllDifferent(queens)
        model.AddAllDifferent([queens[r] + r for r in range(n)])
        model.AddAllDifferent([queens[r] - r for r in range(n)])
        build_time = perf_counter() - started
        solver = cp_model.CpSolver()
        if timeout is not None:
            solver.parameters.max_time_in_seconds = timeout
        solver.parameters.random_seed = seed
        solve_started = perf_counter()
        status = solver.Solve(model)
        solve_time = perf_counter() - solve_started
        mapping = {cp_model.OPTIMAL: "OPTIMAL", cp_model.FEASIBLE: "FEASIBLE", cp_model.INFEASIBLE: "UNSAT", cp_model.UNKNOWN: "TIMEOUT"}
        state = mapping.get(status, "ERROR")
        solution = [solver.Value(q) for q in queens] if state in {"FEASIBLE", "OPTIMAL"} else None
        if state in {"FEASIBLE", "OPTIMAL"} and not validate_solution(solution or [], n):
            return SolveResult("ERROR", None, build_time, solve_time, n, None, "OR-Tools CP-SAT", "decoded model failed validation", str(status))
        return SolveResult(state, solution, build_time, solve_time, n, None, "OR-Tools CP-SAT", None, str(status))
    except Exception as exc:
        return SolveResult("ERROR", None, 0.0, 0.0, 0, None, "OR-Tools CP-SAT", f"{type(exc).__name__}: {exc}", type(exc).__name__)
