# Large-N benchmark infrastructure

This document describes the new, independent runner for a future scalability
experiment. It does not contain benchmark results. No large-N solver run is
performed when implementing or testing this infrastructure.

## Scope and defaults

`scripts/benchmark_large_n.py` defaults to N = 128, 256, 512, 1024, three
trials per configuration, a 100-second per-trial deadline, and an eight-hour
global budget. The initial solver set is `SAT/Glucose3`, `SAT/CaDiCaL`, and
`OR-Tools CP-SAT`. SAT solvers use the requested encodings (default:
`sequential`); CP-SAT uses `n/a` because it is not a CNF encoding.

Example staged command (when the experiment is explicitly authorized):

```powershell
$env:PYTHONPATH = "src"
python scripts/benchmark_large_n.py --sizes 128 --output results/large_n/stage1.json
```

Use a new output path for a new stage. `--resume` reloads an existing JSON
artifact and skips an existing `(solver, encoding, N, trial)` identity. Each
completed trial is persisted immediately to JSON and CSV, and a summary is
regenerated without overwriting historical namespaces.

## Isolation and interpretation

Each trial runs in a spawned child process. The parent deadline therefore
covers model construction and solver execution; an expired child is
terminated and recorded as `TIMEOUT` with unavailable construction/solver
metrics rather than fabricated zeros. Child exceptions are `ERROR`. Returned
SAT/FEASIBLE/OPTIMAL solutions are independently checked with
`nqueens.model.validate_solution`; a failed check is recorded as `ERROR` with
the original backend status in `raw_status`.

The runner preserves `SAT`, `UNSAT`, `FEASIBLE`, `OPTIMAL`, `TIMEOUT`, `ERROR`,
and `LICENSE_LIMIT`. It does not enforce an RSS memory cap; consequently no
memory conclusion may be drawn from its output. `nclauses` is populated only
for SAT encodings; CP-SAT constraint counts remain unavailable unless supplied
by its adapter.

The runner is resumable but deliberately has no retry policy: an existing
timeout or error is a recorded outcome and is not silently rerun. The output
metadata records the run configuration, Python/platform information, deadline,
and whether construction was covered by the subprocess timeout.
