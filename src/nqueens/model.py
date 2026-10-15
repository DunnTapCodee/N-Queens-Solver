from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class NQueensProblem:
    n: int

    def __post_init__(self) -> None:
        if not isinstance(self.n, int) or isinstance(self.n, bool) or self.n < 1:
            raise ValueError("n must be a positive integer")


def validate_solution(solution: Sequence[int], n: int) -> bool:
    """Return whether solution[row] is the queen column for each row."""
    if not isinstance(n, int) or n < 1 or len(solution) != n:
        return False
    if any(not isinstance(c, int) or isinstance(c, bool) or c < 0 or c >= n for c in solution):
        return False
    if len(set(solution)) != n:
        return False
    descending = {r - c for r, c in enumerate(solution)}
    ascending = {r + c for r, c in enumerate(solution)}
    return len(descending) == n and len(ascending) == n
