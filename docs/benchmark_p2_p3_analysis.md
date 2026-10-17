# P2/P3 analysis and plots

## Data quality summary

The analysis uses only the six complete P1 JSON artifacts. They contain 300
records: 250 `SAT` and 50 `FEASIBLE`, with 300/300 returned solutions marked
valid. There are no final `UNSAT`, `OPTIMAL`, `TIMEOUT`, `ERROR`, or
`LICENSE_LIMIT` records because the performance sizes are all satisfiable and
the available backends completed those runs.

The JSON/CSV pairs have matching record counts and the summaries match raw
records by solver, encoding, N, and status. Five trials are present for every
cell in the complete families. The initial DPLL error artifact and the partial
DPLL timeout artifact remain outside the complete population.

## Comparable groups

The strongest direct comparisons are Glucose3 versus CaDiCaL for the same N
and encoding. Each has five samples per cell and the same timeout and total
time field. Encoding comparisons are made within one SAT backend and N.
DPLL is reported separately for N=4,8 because it is an internal fallback and
does not have the same backend implementation or coverage.

CPLEX MIP, CPLEX CP Optimizer, and Gurobi are plotted as separate model
families. Their formulations differ from SAT and from one another; CPLEX MIP
also covers only N=4,8 because of the documented Community Edition limit.
The model-family plot is descriptive and is not a single solver ranking.

## Runtime observations supported by the artifacts

All values below are medians of five completed trials from
`results/p2_p3/p1_group_statistics.csv`:

- Glucose3 pairwise median total time rises from about `0.000473 s` at N=4 to
  `0.376201 s` at N=64.
- CaDiCaL pairwise rises from about `0.001069 s` to `0.890577 s` over the
  same sizes.
- DPLL pairwise is about `0.001218 s` at N=4 and `0.040864 s` at N=8; no
  complete DPLL N>=16 cell is claimed.
- CPLEX CP Optimizer has FEASIBLE medians from about `0.034450 s` at N=4 to
  `0.261713 s` at N=64.
- Gurobi has FEASIBLE medians from about `0.002051 s` at N=4 to `2.082438 s`
  at N=64.

Means are retained in the tables but medians are used for the plots because
some first-trial records include visible initialization overhead. Construction
and solver medians are also retained separately. No missing metric is replaced
with zero.

## Status and incomplete data

The completion plot shows only the complete final families; consequently it
contains no timeout/error bars. This accurately reflects the final artifacts,
but it must not be read as evidence that every attempted configuration
completed: the separate DPLL attempts contain failures.

- `results/p1/dpll.json`: 15 `ERROR` records caused by the initial runner
  encoding-selection defect.
- `results/p1/dpll_v2.json`: 44 records, 40 SAT and 4 TIMEOUT at N=16,
  interrupted before completion.

Those records are preserved and summarized in `p1_audit_metadata.json`, not
silently discarded.

## Generated plots

All plots are SVG and were generated without installing Matplotlib (it is not
available in this environment):

- [sat_runtime_by_n.svg](../results/p2_p3/sat_runtime_by_n.svg): Glucose3 and
  CaDiCaL, separated by encoding.
- [sat_encoding_median_runtime.svg](../results/p2_p3/sat_encoding_median_runtime.svg):
  same-backend encoding median comparison.
- [sat_cactus.svg](../results/p2_p3/sat_cactus.svg): completed SAT runs only,
  separated by backend; timeout/error runs would not be assigned a fake time.
- [completion_status_by_n.svg](../results/p2_p3/completion_status_by_n.svg):
  status counts for the complete final families.
- [model_family_runtime.svg](../results/p2_p3/model_family_runtime.svg):
  separate descriptive curves for CPLEX MIP, CP Optimizer, and Gurobi.

The plots use seconds, and runtime curves use a log10 y scale because the
observed values span multiple orders of magnitude.

## Generated tables and metadata

- [p1_group_statistics.csv](../results/p2_p3/p1_group_statistics.csv) and
  [p1_group_statistics.json](../results/p2_p3/p1_group_statistics.json):
  per-family/N/encoding samples, status counts, median/mean/stdev runtime,
  and construction/solver timing.
- [p1_status_by_n.csv](../results/p2_p3/p1_status_by_n.csv): status counts by
  family and N.
- [p1_audit_metadata.json](../results/p2_p3/p1_audit_metadata.json): input
  artifact/run IDs, partial artifact summaries, and metric handling notes.

The source artifact and sample counts are present in each statistics row. A
timeout or error is counted in status columns and excluded only from completed
runtime statistics; no timeout is converted to zero or to a fabricated runtime.

## Reproduction and checks

Recreate the P2/P3 namespace with:

```text
python scripts/analyze_p1.py
```

The script reads `results/p1/*.json` and writes only `results/p2_p3/`. It does
not import or invoke a solver. The audit and consistency checks completed with
the following outcomes:

```text
final records: 300
statistics rows: 60
JSON/CSV counts and summary status checks: VALIDATION OK
python -m pytest -q tests/test_benchmark_infrastructure.py -> 8 passed
AST parsing: OK
```

No solver or benchmark was run for P2/P3, no dependency was installed, no P1
artifact was overwritten, no `results/raw/` historical artifact was modified,
and `report/report.tex` was not changed.

## Conclusions and limits

The data supports within-family descriptive plots and SAT backend/encoding
comparisons at the tested N values. It supports reporting that all returned
P1 solutions passed validation and that DPLL encountered a clear scalability
boundary around the attempted N=16 run.

It does not support a universal ranking across SAT, CP, and MIP, an UNSAT
performance claim for N=4..64, an OPTIMALity claim for FEASIBLE results, or a
memory/scalability claim because peak memory was not measured. The results can
be incorporated into `report/report.tex` only as a separately identified P1
experiment with these formulation, status, and metric limitations; this task
does not modify the report.
