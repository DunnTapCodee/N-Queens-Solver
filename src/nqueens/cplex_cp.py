"""IBM CP Optimizer adapter for N-Queens (lazy optional dependency)."""
from time import perf_counter
from .model import validate_solution
from .solver import SolveResult


def solve_cplex_cp(n: int, timeout: float | None = None) -> SolveResult:
    started = perf_counter()
    try:
        from docplex.cp.model import CpoModel
    except ImportError as exc:
        return SolveResult("ERROR", None, 0.0, 0.0, 0, 0, "CPLEX CP Optimizer", f"dependency unavailable: {exc}")
    try:
        model = CpoModel(name=f"nqueens_cp_{n}")
        q = [model.integer_var(0, n - 1, name=f"q_{r}") for r in range(n)]
        model.add(model.all_diff(q))
        for r1 in range(n):
            for r2 in range(r1 + 1, n):
                model.add(q[r1] - q[r2] != r1 - r2)
                model.add(q[r1] - q[r2] != r2 - r1)
        build_time = perf_counter() - started
        solve_started = perf_counter()
        kwargs = {"TimeLimit": timeout, "LogVerbosity": "Quiet"} if timeout is not None else {"LogVerbosity": "Quiet"}
        solution = model.solve(**kwargs)
        solve_time = perf_counter() - solve_started
        status_text = str(solution.get_solve_status()).lower() if solution is not None else "unknown"
        nconstraints = len(model.get_all_expressions())
        if solution is None or "infeasible" in status_text or "no solution" in status_text:
            state = "UNSAT" if "infeasible" in status_text or "no solution" in status_text else ("TIMEOUT" if "time" in status_text else "ERROR")
            return SolveResult(state, None, build_time, solve_time, n, nconstraints, "CPLEX CP Optimizer", status_text, status_text)
        queens = [int(solution.get_value(v)) for v in q]
        status_text = str(solution.get_solve_status()).lower()
        if not validate_solution(queens, n):
            return SolveResult("ERROR", None, build_time, solve_time, n, nconstraints, "CPLEX CP Optimizer", "decoded model failed validation", status_text)
        return SolveResult("FEASIBLE", queens, build_time, solve_time, n, nconstraints, "CPLEX CP Optimizer", None, status_text)
    except Exception as exc:
        message = f"{type(exc).__name__}: {exc}"
        state = "TIMEOUT" if "time" in message.lower() else "ERROR"
        return SolveResult(state, None, 0.0, 0.0, 0, 0, "CPLEX CP Optimizer", message, type(exc).__name__)
