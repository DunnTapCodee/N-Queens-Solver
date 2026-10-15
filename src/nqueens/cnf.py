from dataclasses import dataclass


@dataclass
class CNF:
    clauses: list[list[int]]
    nvars: int

    @property
    def nclauses(self) -> int:
        return len(self.clauses)


class VariablePool:
    def __init__(self) -> None:
        self.top = 0

    def new(self) -> int:
        self.top += 1
        return self.top
