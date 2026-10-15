from time import perf_counter
from .cnf import CNF, VariablePool


def _amo_pairwise(lits: list[int], clauses: list[list[int]]) -> None:
    for i, left in enumerate(lits):
        for right in lits[i + 1:]:
            clauses.append([-left, -right])


def _amo_sequential(lits: list[int], clauses: list[list[int]], pool: VariablePool) -> None:
    """Sinz sequential counter encoding for at-most-one."""
    if len(lits) <= 1:
        return
    aux = [pool.new() for _ in range(len(lits) - 1)]
    clauses.append([-lits[0], aux[0]])
    for i in range(1, len(lits) - 1):
        clauses.extend(([-lits[i], aux[i]], [-aux[i - 1], aux[i]], [-lits[i], -aux[i - 1]]))
    clauses.append([-lits[-1], -aux[-1]])


def _amo_binary(lits: list[int], clauses: list[list[int]], pool: VariablePool) -> None:
    if len(lits) <= 1:
        return
    bits = max(1, (len(lits) - 1).bit_length())
    aux = [pool.new() for _ in range(bits)]
    for index, lit in enumerate(lits):
        for bit, var in enumerate(aux):
            clauses.append([-lit, var if (index >> bit) & 1 else -var])


def _amo_commander(lits: list[int], clauses: list[list[int]], pool: VariablePool, group_size: int = 3) -> None:
    if len(lits) <= 1:
        return
    if len(lits) <= group_size:
        _amo_pairwise(lits, clauses)
        return
    commanders = []
    for start in range(0, len(lits), group_size):
        group = lits[start:start + group_size]
        commander = pool.new()
        commanders.append(commander)
        _amo_pairwise(group, clauses)
        for lit in group:
            clauses.append([-lit, commander])
        clauses.append([-commander, *group])
    _amo_commander(commanders, clauses, pool, group_size)


def _exactly_one(lits: list[int], clauses: list[list[int]], pool: VariablePool, encoding: str) -> None:
    clauses.append(list(lits))
    if encoding == "pairwise":
        _amo_pairwise(lits, clauses)
    elif encoding == "sequential":
        _amo_sequential(lits, clauses, pool)
    elif encoding == "binary":
        _amo_binary(lits, clauses, pool)
    elif encoding == "commander":
        _amo_commander(lits, clauses, pool)
    else:
        raise ValueError("encoding must be 'pairwise', 'sequential', 'binary', or 'commander'")


def encode_nqueens(n: int, encoding: str = "pairwise") -> tuple[CNF, float]:
    if not isinstance(n, int) or n < 1:
        raise ValueError("n must be a positive integer")
    started = perf_counter()
    pool = VariablePool()
    cells = [[pool.new() for _ in range(n)] for _ in range(n)]
    clauses: list[list[int]] = []
    for row in cells:
        _exactly_one(row, clauses, pool, encoding)
    for col in range(n):
        _exactly_one([cells[row][col] for row in range(n)], clauses, pool, encoding)
    for r1 in range(n):
        for c1 in range(n):
            for r2 in range(r1 + 1, n):
                dc = r2 - r1
                for c2 in (c1 - dc, c1 + dc):
                    if 0 <= c2 < n:
                        clauses.append([-cells[r1][c1], -cells[r2][c2]])
    return CNF(clauses, pool.top), perf_counter() - started


def decode_model(model: list[int], n: int) -> list[int] | None:
    positive = set(x for x in model if x > 0)
    result = []
    for row in range(n):
        cols = [col for col in range(n) if row * n + col + 1 in positive]
        if len(cols) != 1:
            return None
        result.append(cols[0])
    return result
