"""IBM CPLEX MIP adapter for N-Queens (lazy optional dependency)."""
from time import perf_counter
from .model import validate_solution
from .solver import SolveResult


def solve_cplex_mip(n: int, timeout: float | None = None) -> SolveResult:
    started = perf_counter()
    try:
        from docplex.mp.model import Model
    except ImportError as exc:
        return SolveResult("ERROR", None, 0.0, 0.0, 0, 0, "CPLEX MIP", f"dependency unavailable: {exc}")
    try:
        model = Model(name=f"nqueens_mip_{n}")
        x = {(r, c): model.binary_var(name=f"x_{r}_{c}") for r in range(n) for c in range(n)}
        for r in range(n):
            model.add_constraint(model.sum(x[r, c] for c in range(n)) == 1)
        for c in range(n):
            model.add_constraint(model.sum(x[r, c] for r in range(n)) == 1)
        for r1 in range(n):
            for r2 in range(r1 + 1, n):
                distance = r2 - r1
                for c1 in range(n):
                    for c2 in (c1 - distance, c1 + distance):
                        if 0 <= c2 < n:
                            model.add_constraint(x[r1, c1] + x[r2, c2] <= 1)
        build_time = perf_counter() - started
        if timeout is not None:
            model.parameters.timelimit = timeout
        solve_started = perf_counter()
        solution = model.solve(log_output=False)
        solve_time = perf_counter() - solve_started
        detail = str(model.solve_details.status).lower()
        nconstraints = len(list(model.iter_constraints()))
        if solution is None:
            status = "TIMEOUT" if "time" in detail or "abort" in detail else ("UNSAT" if "infeasible" in detail else "ERROR")
            return SolveResult(status, None, build_time, solve_time, len(x), nconstraints, "CPLEX MIP", detail, detail)
        queens = [next(c for c in range(n) if solution.get_value(x[r, c]) > 0.5) for r in range(n)]
        if not validate_solution(queens, n):
            return SolveResult("ERROR", None, build_time, solve_time, len(x), nconstraints, "CPLEX MIP", "decoded model failed validation", "solution")
        return SolveResult("SAT", queens, build_time, solve_time, len(x), nconstraints, "CPLEX MIP", None, "integer optimal solution")
    except Exception as exc:
        message = f"{type(exc).__name__}: {exc}"
        lowered = message.lower()
        state = "LICENSE_LIMIT" if "promotional" in lowered or "limits" in lowered else ("TIMEOUT" if "time limit" in lowered else "ERROR")
        return SolveResult(state, None, 0.0, 0.0, 0, 0, "CPLEX MIP", message, type(exc).__name__)
