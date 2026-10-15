from dataclasses import dataclass
from time import perf_counter
from typing import Optional
import threading
from .cnf import CNF
from .encoding import decode_model, encode_nqueens
from .model import validate_solution


@dataclass
class SolveResult:
    status: str
    solution: Optional[list[int]]
    encoding_time: float
    solve_time: float
    nvars: int
    nclauses: int
    backend: str
    error: Optional[str] = None
    raw_status: Optional[str] = None


def _dpll(cnf: CNF, timeout: float | None) -> tuple[str, list[int] | None]:
    started = perf_counter()
    clauses = [tuple(c) for c in cnf.clauses]
    assignment: dict[int, bool] = {}

    def recurse() -> list[int] | None:
        if timeout is not None and perf_counter() - started >= timeout:
            raise TimeoutError
        while True:
            changed = False
            for clause in clauses:
                values = [assignment.get(abs(lit)) == (lit > 0) for lit in clause if abs(lit) in assignment]
                undecided = [lit for lit in clause if abs(lit) not in assignment]
                if not undecided and not any(values):
                    return None
                if len(undecided) == 1 and not any(values):
                    var, value = abs(undecided[0]), undecided[0] > 0
                    if var in assignment and assignment[var] != value:
                        return None
                    if var not in assignment:
                        assignment[var] = value
                        changed = True
            if not changed:
                break
        if all(any(assignment.get(abs(l)) == (l > 0) for l in c) for c in clauses):
            return [v if assignment.get(v, False) else -v for v in range(1, cnf.nvars + 1)]
        clause = next(c for c in clauses if not any(assignment.get(abs(l)) == (l > 0) for l in c))
        var = abs(next(l for l in clause if abs(l) not in assignment))
        snapshot = assignment.copy()
        for value in (True, False):
            assignment[var] = value
            answer = recurse()
            if answer is not None:
                return answer
            assignment.clear(); assignment.update(snapshot)
        return None

    try:
        model = recurse()
        return ("SAT" if model is not None else "UNSAT"), model
    except TimeoutError:
        return "TIMEOUT", None


def solve(n: int, encoding: str = "pairwise", timeout: float | None = None, prefer_pysat: bool = True, sat_solver: str = "glucose3") -> SolveResult:
    try:
        cnf, encoding_time = encode_nqueens(n, encoding)
        backend = "internal-dpll"
        started = perf_counter()
        model = None
        status = "ERROR"
        raw_status = None
        if prefer_pysat:
            try:
                from pysat.solvers import Solver  # type: ignore
                backend = f"PySAT/{sat_solver}"
                with Solver(name=sat_solver, bootstrap_with=cnf.clauses) as sat:
                    timer = threading.Timer(timeout, sat.interrupt) if timeout is not None else None
                    if timer:
                        timer.start()
                    limited = sat.solve_limited(expect_interrupt=True)
                    if timer:
                        timer.cancel()
                    status = "SAT" if limited is True else ("TIMEOUT" if limited is None else "UNSAT")
                    raw_status = str(limited)
                    if status == "SAT":
                        model = sat.get_model()
            except ImportError:
                status, model = _dpll(cnf, timeout); raw_status = status
        else:
            status, model = _dpll(cnf, timeout)
        elapsed = perf_counter() - started
        solution = decode_model(model, n) if model else None
        if status == "SAT" and not validate_solution(solution or [], n):
            return SolveResult("ERROR", None, encoding_time, elapsed, cnf.nvars, cnf.nclauses, backend, "decoded model failed validation", "SAT")
        return SolveResult(status, solution, encoding_time, elapsed, cnf.nvars, cnf.nclauses, backend, None, raw_status)
    except Exception as exc:
        message = f"{type(exc).__name__}: {exc}"
        normalized = "LICENSE_LIMIT" if "limit" in message.lower() and ("license" in message.lower() or "promotional" in message.lower()) else "ERROR"
        return SolveResult(normalized, None, 0.0, 0.0, 0, 0, "none", message, type(exc).__name__)
