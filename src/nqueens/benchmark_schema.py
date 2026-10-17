"""Small, additive helpers for benchmark artifacts.

These helpers do not run solvers and deliberately leave historical schemas
unchanged.  They are used only by future benchmark runs.
"""

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


SUPPORTED_STATUSES = (
    "SAT", "UNSAT", "FEASIBLE", "OPTIMAL", "TIMEOUT", "ERROR", "LICENSE_LIMIT"
)


def new_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:12]


def status_counts(records):
    counts = {status: 0 for status in SUPPORTED_STATUSES}
    for record in records:
        status = record["status"]
        if status not in counts:
            raise ValueError(f"unsupported benchmark status: {status}")
        counts[status] += 1
    return counts


def metric_fields(result, encoding: str):
    """Return additive, unambiguous metric aliases for a SolveResult.

    ``nclauses`` retains its legacy meaning.  The explicit fields below make
    clear whether it is a SAT CNF metric or a model constraint metric.
    """
    is_sat = encoding != "n/a"
    return {
        "construction_time_s": result.encoding_time,
        "solver_time_s": result.solve_time,
        "sat_nvars": result.nvars if is_sat else None,
        "sat_nclauses": result.nclauses if is_sat else None,
        "model_nvars": None if is_sat else result.nvars,
        "model_nconstraints": None if is_sat else result.nclauses,
    }


def ensure_output_available(paths, force: bool = False):
    existing = [str(Path(path)) for path in paths if Path(path).exists()]
    if existing and not force:
        raise FileExistsError(
            "output already exists; refusing to overwrite: " + ", ".join(existing)
            + " (use --force only for an intentional new run)"
        )


def manifest_entry(result):
    error = result.error
    installed = result.backend != "none" and "unavailable" not in (error or "").lower()
    usable = result.status in {"SAT", "UNSAT", "FEASIBLE", "OPTIMAL"}
    return {
        "installed_or_callable": installed,
        "smoke_status": result.status,
        "raw_status": result.raw_status,
        "usable": usable,
        "error": error,
    }
