# P0.5 benchmark infrastructure changes

## Scope and preservation

This change prepares future benchmark runs without running a solver or
creating benchmark data. `report/report.tex` and all existing files under
`results/raw/` were left unchanged. Historical artifacts retain their original
schemas and limitations.

## Findings addressed

- Status summaries did not consistently expose `FEASIBLE`, `OPTIMAL`, or
  `LICENSE_LIMIT`, and some older summaries collapsed successful outcomes.
- SAT CNF clause counts and CP/MIP constraint counts shared ambiguous fields.
- New benchmark scripts had no run identifier or default output protection.
- The smoke manifest was written to a fixed path and could overwrite an older
  manifest. The historical manifest's Gurobi-unavailable result is not
  rewritten; its disagreement with later Gurobi 13.0.3 artifacts remains an
  environment/timing discrepancy whose precise cause is **UNKNOWN**.

## Changes

- Added `src/nqueens/benchmark_schema.py` with supported-status counting,
  unique UTC `run_id` generation, output guards, explicit metric aliases, and
  runtime manifest conversion.
- Updated `scripts/benchmark.py` and
  `scripts/benchmark_comparison.py` to attach a run ID to new metadata,
  refuse existing JSON/CSV/summary paths by default, and preserve legacy fields
  while adding explicit SAT/model metric fields.
- Updated `scripts/benchmark_medium_matrix.py` with the same additive metrics,
  run ID, output-directory selection, and overwrite guard.
- Updated `scripts/smoke_backends.py` to support a new output path, guard it,
  and write a run ID plus runtime-derived manifest checks. It was not run.

For SAT encodings, `sat_nvars` and `sat_nclauses` are populated while model
constraint aliases are null. For CP/MIP rows, `model_nvars` and
`model_nconstraints` are populated while SAT aliases are null. No clause count
is inferred from a constraint count. Existing `nvars`, `nclauses`, timing, and
status fields retain their old meanings.

`--force` is required to intentionally reuse an output path. It does not alter
historical files unless a user explicitly supplies that path and the flag.

## Verification

Executed:

```text
python -m pytest -q tests/test_benchmark_infrastructure.py
```

Result: **8 passed in 0.14s**. The tests use fixtures and a
temporary directory; they do not invoke SAT, CP, MIP, Gurobi, or OR-Tools.
They cover separate FEASIBLE/OPTIMAL counts, unsupported status rejection,
non-applicable metrics remaining null, JSON/CSV record parity, output refusal,
unique run IDs, manifest conversion, and read-only access to a historical
artifact.

## Remaining limitations

- Existing historical artifacts are intentionally not migrated or regenerated.
- Peak memory and dependency-lock metadata are still not measured universally.
- The legacy `nclauses` field remains for compatibility; consumers should use
  the explicit SAT/model aliases in new artifacts.
- The manifest fix applies only to future smoke runs; no real smoke run was
  performed in P0.5.
- No benchmark, solver comparison, or P1 scalability experiment was started.

## P0.5 decision

The infrastructure-only portion of P0.5 is complete after the targeted tests
pass. P1 may begin with a fresh output path and a recorded run ID. Before
interpreting P1 results, the environment should perform a real backend smoke
run and record the resulting manifest; that is intentionally outside this
task.
