"""SAT-based N-Queens solver for Assignment 1."""

from .model import NQueensProblem, validate_solution
from .solver import SolveResult, solve

__all__ = ["NQueensProblem", "SolveResult", "solve", "validate_solution"]
