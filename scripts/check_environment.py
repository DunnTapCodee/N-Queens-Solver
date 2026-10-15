import importlib.util
import platform
import sys

print(f"Python: {sys.version.split()[0]}")
print(f"Platform: {platform.platform()}")
for package in ("pysat", "ortools", "docplex", "cplex", "gurobipy"):
    print(f"{package}: {'available' if importlib.util.find_spec(package) else 'unavailable'}")
