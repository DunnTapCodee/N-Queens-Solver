# P4.1 benchmark gap analysis

## Scope and sources

This is a read-only audit. No benchmark, solver, smoke test, dependency
installation, or report edit was performed.

Sources inspected:

- Assignment requirements: `Assignment 1 - requirements.pdf`;
- research reference: `mode_title.pdf` at the repository root;
- report template/sample: `Mau xay dung bao cao BTL so 1 và BTL so 2.pdf`;
- current report: `report/report.tex`;
- P0--P3 documents under `docs/`;
- P1 JSON/CSV/summary files under `results/p1/`;
- P2/P3 tables and SVG plots under `results/p2_p3/`;
- README and the current source/validator descriptions.

The Vietnamese sample PDF is a 2DBMP paper rather than an N-Queens results
paper. It is useful as a scientific-report structure reference, but its
experiments are not evidence about this project.

## Current status

The project has a verified and reproducible P1 family containing 300 records:
250 `SAT` and 50 `FEASIBLE`, with 300/300 returned solutions marked valid.
The complete families are Glucose3, CaDiCaL, DPLL fallback, CPLEX MIP, CPLEX
CP Optimizer, and Gurobi. P1 covers N=4,8,16,32,64 for the SAT backends and
model families where feasible; DPLL is complete only at N=4,8; CPLEX MIP is
complete only at N=4,8 because of the known Community Edition limit.

P2/P3 verified JSON/CSV/summary consistency, produced per-family statistics,
and generated SVG plots. OR-Tools remains unavailable. The current
`report/report.tex` is syntactically structured as a `cas-sc` report, but its
main results still describe the earlier 72-record comparison and historical
medium artifacts rather than the 300-record P1/P2 data.

## Assignment requirements versus evidence

| Assignment requirement | Status | Evidence | Importance / action |
|---|---|---|---|
| Implement an N-Queens solver using PySAT SAT solving | VERIFIED | `src/nqueens/solver.py`, PySAT smoke results, P1 Glucose3/CaDiCaL records | Mandatory; satisfied |
| Compare SAT with exact ILP/CP methods | PARTIALLY VERIFIED | P1 has CPLEX MIP, CPLEX CP Optimizer, and Gurobi; CP-SAT adapter exists but is unavailable | Mandatory comparison is mostly covered; CP-SAT availability/result remains the largest assignment gap |
| Use CPLEX CP, CPLEX MIP, Gurobi, and CP-SAT where applicable | PARTIALLY VERIFIED | P1 validates the first three; `backend_smoke_test_current.md` records `ortools` missing | Do not present CP-SAT as benchmarked; either run it in a permitted environment or explicitly document it as unavailable |
| Provide SAT encoding alternatives | VERIFIED for implemented scope | Pairwise, Sequential, Binary, Commander in `src/nqueens/encoding.py` and P1 | Satisfied for implemented encodings; Product is not required by the wording, but is a research gap |
| Conduct experiments on large matrices/sizes | PARTIALLY VERIFIED | P1 reaches N=64; historical SAT artifact also reaches N=64 | Assignment asks for large sizes but does not prescribe 1331; a selected scalability experiment would strengthen compliance |
| Validate returned N-Queens solutions | VERIFIED | P1 records `solution_valid`; P2 confirms 300/300 valid | Satisfied for returned solutions; UNSAT is separately represented |
| Preserve statuses and explain license/dependency limitations | VERIFIED | P0.5 schema, smoke manifest, P1 reports; CPLEX and OR-Tools limitations explicit | Satisfied |
| Submit a scientific-style report using Elsevier `cas-sc` | PARTIALLY VERIFIED | `report/report.tex` uses `cas-sc`; current content is stale relative to P1/P2 | Update report only after the gap decisions are made |
| Include a repository/data-availability link | VERIFIED in current report | `report/report.tex` contains the GitHub URL | Recheck the final URL against the intended repository before submission |

The assignment does not explicitly require reproducing all 18 sizes, Product,
peak RSS instrumentation, exhaustive AMO enumeration, or the exact 252-run
design in `mode_title.pdf`. Those are research extensions, not automatically
mandatory submission requirements.

## Gaps against the original research report

The reference PDF claims five AMO encodings (including recursive 2-Product),
two CDCL backends, four non-SAT baselines, 18 sizes through N=1331, 252
single-run experiments, external 100-second process budgets, 14 GiB peak RSS
monitoring, formula-size analysis, construction/solver decomposition, and
validated coverage including timeouts. It also reports exhaustive AMO checks,
unit-propagation checks, projected solution enumeration through N=8, and
placement counts.

| Reference claim or capability | Current evidence | Status | Importance | Resolution |
|---|---|---|---|---|
| Pairwise, Binary, Sequential, Commander | Implemented and P1-tested with Glucose3/CaDiCaL at N through 64 | VERIFIED | High | Can be reported |
| Recursive 2-Product encoding | No implementation or P1 artifact | WARNING | Medium for assignment, high for reproducing the paper | Add only if the report claims paper-level reproduction |
| Glucose3 and CaDiCaL comparison | 200 complete P1 records, five trials per cell | VERIFIED | High | Use P1/P2 data |
| OR-Tools CP-SAT baseline | Adapter exists; dependency missing; no benchmark artifact | WARNING | High for the literal assignment comparison; medium for paper reproduction | Run only in an environment where dependency installation is permitted, or mark unavailable |
| CPLEX CP, Gurobi, CPLEX MIP baselines | P1 records exist; CPLEX MIP stops at N=8 | VERIFIED with limitation | High | Report separate formulation/coverage limits |
| 18 sizes through N=1331 | Current complete P1 maximum is N=64; DPLL complete only to N=8 | WARNING | High for scalability claims, not required to reproduce all paper claims | Run a selected large-size experiment if submission requires “large matrices” |
| 252 runs and 14 configurations | Current complete P1 has 300 records under a different repeated-run design and six families | VERIFIED difference | Medium | Do not call P1 a reproduction of the paper |
| Peak sampled process-tree RSS and 14 GiB limit | No P1/P2 memory field or measurement | WARNING | High only if memory claims are included | Add instrumentation before making memory conclusions |
| Exact formula-size tables at large N | P1 stores variables/clauses/constraints for tested N; no Product or N>64 | PARTIALLY VERIFIED | High for encoding analysis | Current four-encoding tables are supportable; omit Product/large-N claims |
| Build, solver-call, and total timing | P1 stores all three, but protocols are not identical across paradigms | VERIFIED with comparability warning | High | Use within-family comparisons and state timing semantics |
| Timeout/censored-result coverage | Final P1 has no timeout/error; DPLL partial has four TIMEOUT and initial run has 15 ERROR | VERIFIED but incomplete | High for scalability conclusions | Keep partial artifacts separate; do not infer zero failures |
| Exhaustive AMO semantics checks, 570 propagation checks | No corresponding current artifact | UNKNOWN | Medium | Optional research-strengthening test, not needed for basic assignment |
| Exhaustive solution enumeration and counts for N=1..8 | Current validators check individual placements; no enumeration artifact | WARNING | Medium | Add only if making completeness/encoding-equivalence claims |
| Paper claim that compact clauses can be slower | P1 has clause and runtime fields for four encodings, but only N<=64 and no Product | PARTIALLY VERIFIED | High for a local claim | Analyze only observed configurations; do not transfer the paper’s Product/1331 conclusion |
| Cross-paradigm performance hierarchy | P1 has separate model-family curves, but formulations and build protocols differ | WARNING | High | Report descriptive results, not a universal ranking |

## Highest-value additional experiments

No experiment is executed in P4.1. The following list is capped at five and is
ordered by value for assignment completion, not by similarity to the paper.

### 1. CP-SAT availability and controlled comparison — priority P0

**Question:** Can the required CP-SAT comparison be executed under the same
schema and timeout policy?

**Configuration:** OR-Tools CP-SAT on the existing N=1,2,3,4 correctness set
and N=4,8,16,32,64 performance set, five trials where permitted; use the
existing adapter and independent validator.

**Metrics:** status, raw status, solution validity, build/solver/total time,
model counts where the adapter exposes them, dependency/version metadata.

**Value:** closes the clearest literal assignment gap. **Cost:** dependency
installation and an environment change are required; it cannot be performed
under the present no-install audit constraint.

### 2. Selected large-size scalability run — priority P1

**Question:** Do the strongest currently available configurations remain
usable beyond N=64, as required by the “large matrices” wording?

**Configuration:** choose a small, justified subset after P1 analysis, for
example SAT Commander/Glucose3, the strongest observed alternative SAT
configuration, CPLEX CP Optimizer, and Gurobi at N=81,100,125,216,343,512,
729,1000,1331; use a separate process, explicit external timeout, and skip
known CPLEX MIP license-limited sizes.

**Metrics:** validated status, timeout/error/license status, build/solver/total
time, model size, solver version, and exact resource limits.

**Value:** directly addresses scalability and gives evidence for a large-size
conclusion. **Cost:** potentially high runtime and memory; requires resource
monitoring not present in P1.

### 3. Peak-memory instrumentation for selected configurations — priority P1

**Question:** Can any memory claim from the reference paper be supported by
this project?

**Configuration:** run only the selected large-size configurations from
Experiment 2 in separate processes with process-tree RSS sampling and a
documented memory cap.

**Metrics:** peak RSS in MiB, timeout/termination reason, plus existing timing
and validation fields.

**Value:** enables or rules out a memory section; prevents importing the
reference paper’s RSS claims without measurement. **Cost:** implementation and
platform-specific validation are required.

### 4. Product encoding implementation and bounded validation — priority P2

**Question:** Is the reference paper’s recursive 2-Product claim relevant to
the project’s SAT encoding comparison?

**Configuration:** implement and independently test Product only if the final
report intends to compare all paper encodings; correctness N=1..8 and bounded
performance matching the existing SAT matrix.

**Metrics:** CNF variables/clauses, construction/solver/total time, status,
validator results, and encoding-specific tests.

**Value:** enables a genuine comparison with the paper’s fifth encoding.
**Cost:** nontrivial encoding implementation and new correctness evidence;
not necessary for the assignment’s minimum four-encoding scope.

### 5. Independent exhaustive correctness/solution-count audit — priority P2

**Question:** Do the implemented encodings accept exactly the same N-Queens
placements on small boards, beyond checking one returned solution?

**Configuration:** no performance benchmark; enumerate/project solutions for
N=1..8 or use the existing independent permutation checker, with Pairwise,
Sequential, Binary, and Commander.

**Metrics:** placement counts, set equality, UNSAT at N=2,3, and runtime only
as a secondary diagnostic.

**Value:** strengthens encoding correctness and supports claims about formula
equivalence. **Cost:** moderate implementation/test time; it does not address
large-scale performance.

## What should happen before editing the report

1. Decide whether the submission must include a measured CP-SAT result. If yes,
   obtain an allowed environment and run Experiment 1; otherwise state the
   dependency limitation explicitly.
2. Decide whether “large matrices” is interpreted as N=64 being sufficient for
   this assignment. If not, perform Experiment 2, with Experiment 3 if memory
   is discussed.
3. Do not add Product or exhaustive enumeration solely to imitate the PDF;
   add them only if the report will claim reproduction or encoding-complete
   comparison.
4. Update the report’s source/artifact references from the stale 72-record
   comparison to the verified P1/P2 namespace, and separate SAT, FEASIBLE,
   UNSAT, and unavailable CP-SAT results.
5. Add the P1/P2 tables and figures only after the final experiment scope is
   frozen. Keep `mode_title.pdf` claims clearly labeled as reference results,
   not project results.

## Final decision

The project’s most important remaining gap is the missing CP-SAT result for the
literal multi-solver assignment comparison, followed by uncertain compliance
with the request for large-size experiments. Product, exhaustive enumeration,
and peak memory are important only if the report aims to reproduce the research
paper’s stronger claims.

Additional benchmarking is therefore **conditionally needed**: run CP-SAT
first if dependency installation is allowed; otherwise document it as
unavailable. If the instructor expects genuinely large matrices, run the
selected scalability experiment next, with memory instrumentation before
making RSS claims.

There is enough evidence to begin report finalization structurally, but not to
claim that the report is fully final. `report/report.tex` should be completed
only after the CP-SAT decision and the interpretation of the large-size
requirement are settled. No old file or artifact was changed by this audit.
