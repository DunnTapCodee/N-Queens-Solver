# P4.2 benchmark scope and report update plan

## 1. Decision basis

This plan is based on the assignment PDF, `docs/benchmark_gap_analysis.md`,
and the current `report/report.tex`. No benchmark, solver, dependency
installation, or report edit was performed.

The assignment explicitly says to compare SAT solving with exact ILP/CP
methods and names CPLEX CP, CPLEX MIP, Gurobi, and CP-SAT. Therefore CP-SAT
is an explicitly requested comparison target, not merely a method mentioned
only by the research paper. The assignment does not specify an exact N value,
number of trials, timeout, memory limit, or requirement to reproduce the
reference paper's 18-size/252-run experiment. It does request experiments on
large matrices/sizes and a scientific-style report using the Elsevier
`cas-sc` template.

The research PDF `mode_title.pdf` is a broader reference study: five SAT
encodings including recursive 2-Product, 18 sizes through N=1331, 252 runs,
external process limits, peak RSS, and extensive correctness checks. Those
details are not automatically assignment requirements.

## 2. Gap classification before submission

| Gap | Classification | Evidence and required decision |
|---|---|---|
| CP-SAT has no measured result | **Mandatory to resolve or explicitly document** | The assignment names CP-SAT. OR-Tools is unavailable in the current environment, so the final report must either include a permitted CP-SAT run or clearly state that the requested backend could not be benchmarked because its dependency was unavailable. It must not present CP-SAT as evaluated. |
| Current report describes the old 72-record comparison | **Mandatory** | `report/report.tex` still reports the historical 72 records and old figure paths. It must be updated to the verified P1/P2 namespace and current statuses before submission. |
| Final report/PDF compilation | **Mandatory for a finished submission** | The source uses `cas-sc`, but the repository environment previously lacked a LaTeX compiler/class. Compilation must be tested in an environment with the required class and packages; failure must be reported rather than claimed successful. |
| Scientific structure and Data Availability link | **Mandatory** | The template and a repository URL are present, but final sections must describe actual artifacts and the intended repository URL. |
| N greater than 64 | **Not explicitly mandatory by a specified threshold** | The assignment says “large matrices” but gives no N. P1 reaches N=64 and the research paper reaches N=1331. Do not claim the paper's scalability from P1. Run larger N only if the instructor interprets “large” as requiring more than N=64 or if a scalability conclusion is desired. |
| OR-Tools installation | **Conditional** | No installation is justified in this audit. If CP-SAT is required for strict completeness, an allowed environment/dependency setup is needed; otherwise document the limitation. |
| Recursive 2-Product encoding | **Can be recorded as a scope limitation** | The assignment encourages Binary, Commander, Product, and Sequential but does not state that every encoding is compulsory. Four encodings are implemented and benchmarked. Product is needed only for paper-level reproduction or an encoding-complete claim. |
| Peak memory measurement | **Can be recorded as a limitation** | The assignment does not explicitly require memory. The research paper does, but P1 has no RSS field. Do not include memory conclusions without a separate measurement. |
| Exhaustive AMO/propagation/solution enumeration | **Can be recorded as a limitation or optional strengthening** | P1 validates returned solutions; it does not reproduce the paper's exhaustive checks. This is not needed for the minimum assignment claim unless the report asserts formula-completeness equivalence. |
| CPLEX MIP N>=16 | **Can be recorded as an environment limitation** | Community Edition size limits are documented. P1 reports CPLEX MIP at N=4,8 and does not convert license limits into algorithmic failures. |
| UNSAT performance at larger N | **Not required for ordinary N-Queens performance matrix** | N=2 and N=3 provide UNSAT correctness cases; all P1 performance sizes are satisfiable. Do not invent larger UNSAT instances or claim UNSAT scaling. |

## 3. Minimum additional benchmark scope

The minimum additional experiment is **CP-SAT only**, and only if the
submission must satisfy the assignment's named-backend comparison literally.
It should use the already established schema and conditions:

- correctness: N=1,2,3,4, with independent validation;
- performance: N=4,8,16,32,64, five trials and the existing 10-second timeout
  if the environment permits;
- metrics: status/raw status, solution validation, build/solver/total time,
  model size when exposed, version, and dependency metadata;
- output: a new run namespace, never `results/raw/` or `results/p1/`.

If OR-Tools cannot be installed or used under the course environment, no
substitute benchmark should be fabricated. The report should state
`CP-SAT: not benchmarked; OR-Tools dependency unavailable` and preserve the
existing evidence.

No additional scalability benchmark is required by an exact N threshold in the
assignment. A larger run should be approved only if one of these concrete
reasons applies:

1. the instructor requires sizes beyond N=64;
2. the report intends to claim scalability beyond the observed range; or
3. a final scientific conclusion depends on behavior at larger N.

If needed, use a small selected set rather than reproduce all 18 reference
sizes: for example Commander/Glucose3, the strongest observed alternative SAT
configuration, CPLEX CP Optimizer, and Gurobi. Add external timeout and memory
monitoring before making resource claims. CPLEX MIP should remain excluded at
known Community Edition limits.

Product, exhaustive enumeration, and RSS instrumentation are not part of the
minimum benchmark scope. They are optional only when the report explicitly
aims to reproduce the stronger claims of `mode_title.pdf`.

## 4. Mapping current report sections to final data

| Current report section | Decision | Final source/content |
|---|---|---|
| Abstract | Update | Replace the old 72-record description with the final selected scope: P1 300 records, four SAT encodings, backend availability, and any CP-SAT result or limitation. Keep SAT/FEASIBLE distinct. |
| Introduction and problem formulation | Keep with minor update | Existing N-Queens definition is usable. Add the feasibility/no-objective distinction and state that the reference paper is not being reproduced in full. |
| Methods | Update | Describe Pairwise, Sequential, Binary, Commander; Glucose3/CaDiCaL; DPLL as a separate fallback; CPLEX MIP/CP and Gurobi formulations. Mark Product and OR-Tools as outside/unavailable unless later measured. |
| Experimental setup | Replace stale setup | Use P1 plan/results: N sets by family, five repetitions, 10-second timeout, run IDs, validator, status vocabulary, build/solver/total timing, and separate output namespace. State that peak RSS was not measured. |
| Correctness and results | Replace stale 72-record table | Use `results/p1/*` and `results/p2_p3/p1_group_statistics.csv`. Report 250 SAT, 50 FEASIBLE, 300/300 valid solutions, and separately describe the DPLL error/partial artifacts. Include UNSAT only where supported by correctness/smoke artifacts. |
| Approved medium encoding matrix | Reframe or merge | It is historical supporting evidence for N=1..4 correctness and N=4,8,16 performance. Do not present it as the final P1 matrix or merge it numerically with P1. |
| Existing comparison tables | Replace | The current table uses old medians and three trials. Replace with P1/P2 tables, grouped by SAT family and model family; do not rank different formulations in one unqualified table. |
| Existing figures | Replace paths and captions | Use `results/p2_p3/sat_runtime_by_n.svg`, `sat_encoding_median_runtime.svg`, `sat_cactus.svg`, `completion_status_by_n.svg`, and `model_family_runtime.svg` only if the LaTeX toolchain supports the format or after a documented conversion. |
| Discussion and limitations | Expand | Explain CP-SAT unavailability/result, CPLEX MIP license limit, DPLL N=16 timeout evidence, no memory measurement, no Product encoding, all-performance-N satisfiable bias, and cross-formulation timing limits. |
| Conclusion and future work | Rewrite conservatively | Conclude only within-family observations supported by P1/P2. Do not claim CP-SAT performance, N=1331 scalability, OPTIMALity of FEASIBLE results, or a universal solver ranking. |
| Data Availability | Keep and verify | Retain the repository URL only after confirming it is the intended submission repository. List P1/P2 artifact namespaces and reproduction commands. |

## 5. Recommended final report structure

1. Abstract with scope, measured backends, and explicit unavailable methods.
2. Introduction and ordinary N-Queens feasibility definition.
3. Related work, clearly separating the reference paper from project results.
4. Methods and formulations: SAT encodings, DPLL baseline, CP, MIP, Gurobi,
   and CP-SAT status.
5. Experimental protocol: configurations, N sets, repetitions, timeout,
   validation, status semantics, timing fields, and environment.
6. Correctness results: N=1..4 SAT/UNSAT evidence and validator outcomes.
7. SAT encoding/backend performance: within-family medians, construction and
   solver timing, formula sizes, and P1 plots.
8. Exact-model family results: CPLEX MIP, CP Optimizer, and Gurobi in separate
   tables/figures with formulation and license caveats.
9. Discussion: observed encoding/backend interaction, scalability boundary,
   and limitations. Avoid cross-paradigm rankings without qualification.
10. Conclusion, future work, and Data Availability.

## 6. Answers and next step

**Is CP-SAT mandatory?** The assignment explicitly names CP-SAT in the required
comparison, so it is mandatory as a target to address. A measured result is
preferred; if the dependency cannot be installed or used, the report must
explicitly document it as unavailable rather than omit it silently.

**Must N exceed 64?** No exact threshold is specified. N>64 is not proven
mandatory by the assignment text alone. It becomes necessary only if the
instructor requires a stronger interpretation of “large matrices” or if the
report claims large-scale scalability.

**What benchmark should come first?** CP-SAT correctness/performance under the
existing schema, if an allowed environment is available. Otherwise no new
benchmark is required before report writing; document the unavailable backend.

**Can report updating start after P4.2?** Yes, structural updating can start
immediately using P1/P2/P3. Finalization should wait for the CP-SAT decision and
for a decision on whether N>64 is required. The current report is stale and
must not be submitted unchanged.

No existing source, report, benchmark artifact, or generated P1/P2/P3 artifact
was modified in this planning step. The only intended new file is this plan.
