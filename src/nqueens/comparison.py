"""Dependency probes for the assignment's required comparison methods.

No unavailable solver is replaced silently. This module only reports what can
be imported in the current environment; model adapters can be added when a
licensed installation is available.
"""
import importlib.util


def available_comparison_methods() -> dict[str, bool]:
    return {
        "CPLEX CP (docplex)": importlib.util.find_spec("docplex") is not None,
        "CPLEX MIP (cplex)": importlib.util.find_spec("cplex") is not None,
        "Gurobi": importlib.util.find_spec("gurobipy") is not None,
        "CP-SAT (ortools)": importlib.util.find_spec("ortools") is not None,
    }
