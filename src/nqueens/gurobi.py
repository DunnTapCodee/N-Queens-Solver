"""Optional Gurobi MIP adapter; no fallback is performed when unavailable."""
from time import perf_counter
from .model import validate_solution
from .solver import SolveResult


def solve_gurobi(n: int, timeout: float | None = None) -> SolveResult:
    started = perf_counter()
    try:
        import gurobipy as gp
        from gurobipy import GRB
    except ImportError as exc:
        return SolveResult("ERROR", None, 0.0, 0.0, 0, 0, "Gurobi", f"dependency unavailable: {exc}")
    try:
        model = gp.Model(f"nqueens_{n}")
        model.Params.OutputFlag = 0
        if timeout is not None:
            model.Params.TimeLimit = timeout
        x = model.addVars(n, n, vtype=GRB.BINARY, name="x")
        for r in range(n): model.addConstr(gp.quicksum(x[r, c] for c in range(n)) == 1)
        for c in range(n): model.addConstr(gp.quicksum(x[r, c] for r in range(n)) == 1)
        for r1 in range(n):
            for r2 in range(r1 + 1, n):
                d = r2 - r1
                for c1 in range(n):
                    for c2 in (c1-d, c1+d):
                        if 0 <= c2 < n: model.addConstr(x[r1,c1] + x[r2,c2] <= 1)
        build_time = perf_counter() - started
        solve_started = perf_counter(); model.optimize(); solve_time = perf_counter() - solve_started
        if model.Status == GRB.TIME_LIMIT and model.SolCount == 0: return SolveResult("TIMEOUT", None, build_time, solve_time, n*n, model.NumConstrs, "Gurobi", "TIME_LIMIT", str(model.Status))
        if model.Status == GRB.INFEASIBLE: return SolveResult("UNSAT", None, build_time, solve_time, n*n, model.NumConstrs, "Gurobi", None, "INFEASIBLE")
        if model.SolCount == 0: return SolveResult("ERROR", None, build_time, solve_time, n*n, model.NumConstrs, "Gurobi", str(model.Status), str(model.Status))
        queens = [next(c for c in range(n) if x[r,c].X > 0.5) for r in range(n)]
        if not validate_solution(queens, n): return SolveResult("ERROR", None, build_time, solve_time, n*n, model.NumConstrs, "Gurobi", "decoded model failed validation", str(model.Status))
        return SolveResult("FEASIBLE", queens, build_time, solve_time, n*n, model.NumConstrs, "Gurobi", None, str(model.Status))
    except Exception as exc:
        message = f"{type(exc).__name__}: {exc}"
        lowered = message.lower()
        status = "LICENSE_LIMIT" if any(term in lowered for term in ("license", "size-limited", "model too large")) else "ERROR"
        return SolveResult(status, None, 0.0, 0.0, 0, 0, "Gurobi", message, type(exc).__name__)
