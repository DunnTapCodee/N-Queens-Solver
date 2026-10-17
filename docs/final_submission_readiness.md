# Final Submission Readiness

Date: 2026-10-18

## Executive summary

Current status: **PASS WITH WARNINGS**. The previously missing LaTeX
environment has now been installed in user scope and the report PDF builds
successfully. The older blocked wording below records the earlier audit state;
the build verification update later in this document is authoritative.

**Overall status: NOT READY — BLOCKED for a verified final PDF.** The report
content and benchmark data are internally consistent at the checked level, and
the assignment's explicit CP-SAT comparison requirement is covered by a
separate 25-trial artifact. The report now uses the official PySAT API
citation and identifies the research source as a preprint without an
unsupported year or venue. Final submission is still blocked by the missing
Elsevier class/compiler workflow. No benchmark or solver was run in this audit.

Status vocabulary used below: `PASS` means directly verified, `PASS WITH
WARNINGS` means usable but with a documented limitation, `BLOCKED` means an
external dependency prevents completion, and `NOT CHECKED` means no claim is
made.

## 1. Reference verification

`mode_title.pdf` was read successfully with the already installed PyMuPDF
module. The file has 38 pages and reports the following metadata:

- Title: *A Comparative Study of Exact Solving Paradigms for the N-Queens
  Problem: SAT, CP, and ILP Approaches*
- Author: Nguyen Cong Danh
- Document status: the first page identifies it as a preprint submitted to
  Elsevier.
- The PDF does not provide a verified journal/conference publication venue or
  publication year in the extracted title/front-matter information. Its PDF
  creation date is 2026, but that is not treated as a publication year.

The current `bibitem{reference}` contains the same title and author initials
(`N. C. Danh`) and now describes it only as a preprint submitted to Elsevier.
The title, author, and preprint status are consistent with the source PDF; no
unsupported publication year or venue is asserted.

Verification status: **PASS WITH WARNINGS**. Title, author, and preprint status
are supported; the PDF does not establish a journal/conference publication.

The source PDF's reference section confirms:

- Sinz, *Towards an Optimal CNF Encoding of Boolean Cardinality Constraints*,
  Principles and Practice of Constraint Programming (2005), with a URL.
- Google OR-Tools official N-Queens documentation.
- W. Klieber and G. Kwon, *Efficient CNF Encoding for Selecting 1 from N
  Objects* (2007).
- J. Chen, *A New SAT Encoding of the At-Most-One Constraint* (2010).
- PySAT official solver API documentation.

The report's Sinz citation is consistent with the source PDF. The report now
uses the official PySAT solver API URL listed in the source PDF's reference
section. No guessed DOI, venue, year, or page range was added.

## 2. LaTeX environment

Build status: **PASS WITH WARNINGS**. MiKTeX 25.12 was installed in user
scope, `cas-sc.cls` was supplied by the official `els-cas-templates` package,
and `pdflatex` is available at
`C:\Users\ADMIN\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe`.
The report was compiled twice with exit code 0 using:

```powershell
pdflatex -enable-installer -interaction=nonstopmode -halt-on-error `
  -file-line-error -output-directory build/submission report/report.tex
```

The resulting PDF is `build/submission/report.pdf`. Inkscape was unavailable;
Edge headless generated build-local PNG copies in `build/generated/` from the
five SVG sources. The original SVGs and benchmark artifacts were preserved.

Checks performed in the current environment:

- `pdflatex`: not found.
- `lualatex`: not found.
- `xelatex`: not found.
- `tectonic`: not found.
- `latexmk`: not found.
- `cas-sc.cls`: not found in the repository or through the checked local paths.

The report uses the Elsevier `cas-sc` document class, so a working TeX
distribution and the class file are required before compilation. Compilation
was not attempted because no compiler or class file is available.

The report references five SVG files under `results/p2_p3/`; all five files
exist. A standard `graphicx` setup with pdfLaTeX does not generally include SVG
directly. The least invasive compilation plan is either:

1. use a LaTeX environment with an SVG-capable package and its converter,
   after verifying those tools are available; or
2. convert the existing SVG plots to PDF/PNG outside the repository's raw
   benchmark data and update only the figure paths in a controlled report copy.

No conversion was performed in this audit. The report's SVG sources and
benchmark artifacts remain unchanged.

Build status: **BLOCKED**. No compiler command was executed because the
required compiler and class file are absent. Consequently there is no exit
code or PDF path to report, and no visual PDF inspection was performed.

## Assignment and template compliance

The extracted one-page assignment explicitly requires:

| Requirement | Evidence | Status |
|---|---|---|
| Implement an N-Queens solver using PySAT/SAT solving | `src/nqueens/solver.py`; PySAT Glucose3/CaDiCaL P1 records | PASS |
| Compare SAT with exact ILP/CP methods including CPLEX CP, CPLEX MIP, Gurobi, and CP-SAT | P1 model-family artifacts plus separate `results/cp_sat/` run | PASS WITH WARNINGS: separate scopes are stated |
| Conduct experiments on large matrices | P1 covers N through 64; CP-SAT covers N through 64 | PASS WITH WARNINGS: no specific larger N is mandated in the assignment text |
| Encourage AMO/ALO encodings including Binary, Commander, Product, Sequential Counter | Pairwise, Sequential, Binary, Commander are implemented and benchmarked; Product is explicitly documented as not implemented | PASS WITH WARNINGS: Product is encouraged, not stated as mandatory |
| Submit a scientific-paper-style report using the Elsevier `cas-sc` template | `report/report.tex` uses `cas-sc`; PDF cannot be built in this environment | BLOCKED |
| Provide repository link in Data Availability | GitHub URL is present in `report/report.tex` | PASS |

The assignment does not specify an exact N maximum, a required number of
trials, peak memory measurement, recursive 2-Product, or exhaustive
enumeration. Those are research extensions or limitations, not silently
converted into mandatory requirements.

The separate template PDF was read as a report-structure example. It does not
add a project-specific solver requirement beyond the assignment text.

## 3. Verified blockers

1. No LaTeX compiler is installed or discoverable in the current environment.
2. `cas-sc.cls` is unavailable locally.
3. The existing `graphicx` configuration may require SVG support or converted
   figures before a standard pdfLaTeX build.
4. No LaTeX compiler or `cas-sc.cls` is available for a final build.

## 4. Recommended next step

Use a controlled, separately provisioned LaTeX environment that supplies the
Elsevier `cas-sc` class and a compiler. Before changing the report, verify the
environment with a minimal `cas-sc` document. Then compile a copy of the
report, resolve SVG handling using an existing SVG-capable workflow or
reproducible converted figure copies, and inspect the generated PDF.

For bibliography, retain only fields supported by the source PDF unless an
authoritative publication record is provided. In particular, treat the source
as a preprint rather than asserting a journal/conference venue.

## 5. Submission checklist

- [x] CP-SAT raw JSON, CSV, and summary audited.
- [x] CP-SAT results integrated as a separate dataset in the report.
- [x] Historical and P1/P2/P3 benchmark artifacts preserved.
- [x] Figure paths checked for existence.
- [x] Reference title and author checked against `mode_title.pdf`.
- [x] Remove unsupported year/venue wording from `bibitem{reference}`.
- [x] Replace the unconfirmed PySAT proceedings citation with the official API
  citation supported by the source PDF.
- [ ] Provide a verified `cas-sc` LaTeX environment.
- [ ] Resolve SVG inclusion for the selected compiler.
- [ ] Compile the report and inspect the resulting PDF.

## Files and change scope

This audit created or modified only:

- `docs/final_submission_readiness.md` — updated with the final status,
  assignment matrix, and exact blockers.

`report/report.tex` was updated in this phase. All files under `results/p1/`, `results/p2_p3/`,
`results/cp_sat/`, and historical benchmark files were not modified in this
audit. The working tree already contains earlier changes and untracked
artifacts from the project; they were preserved and not reset or cleaned.

## Checks run in this phase

The report change in this phase is limited to keywords, explicit formulation
explanations, CP-SAT model clarification, and the two bibliography corrections
described above. Benchmark source files and generated result artifacts were
not edited.

Exact files changed in this continuation:

- `report/report.tex`
- `docs/final_submission_readiness.md`

- `git status --short` and read-only inspection of the relevant files.
- PyMuPDF extraction of `mode_title.pdf`, the assignment PDF, and the template
  PDF.
- Inspection of the report bibliography, document class, figure paths, and
  existing readiness/integration documents.
- Tool discovery for LaTeX compilers, `cas-sc.cls`, SVG converters, and PDF
  utilities.
- No solver, benchmark, smoke test, dependency installation, or artifact
  rewrite was performed.

## Build verification update

The report now builds successfully at `build/submission/report.pdf` using the
user-scoped MiKTeX installation described above. The PDF has 7 pages. Text
extraction confirms the title, CP-SAT section, references, and data availability;
no undefined citation/reference text was found. Representative pages were
rendered and inspected visually. Remaining log messages are non-fatal
overfull/underfull boxes and float-placement warnings.

The report was expanded with research questions, detailed descriptions of the
four implemented AMO encodings, experimental-protocol discussion, SAT
backend/encoding analysis, CP/MIP status semantics, and quantitative analysis
of CP-SAT medians and the N=4 startup outlier. The anonymous title
configuration was also verified: the PDF text and metadata contain no
`Assignment 1`, `Course project`, `Local environment`, or `First Author`
placeholder. `\shortauthors{}` is used with the existing `cas-sc` class.

The layout was then refined without changing benchmark data: SAT runtime and
encoding figures share a page, the cactus and model-family figures share a
page, and the footer now reports `Page x of 8`. The ORCID line is suppressed
for the anonymous report. All eight rendered PDF pages were generated for
inspection; representative pages containing the title, equation, SAT figures,
model results, discussion, conclusion, and references were visually checked.
The final build remains exit code 0. Non-fatal warnings are limited to a long
abstract line, minor box warnings, and float-placement notices.

## Conclusion

The bibliography is now verified to the level supported by repository sources:
title, author, preprint status, Sinz reference, and the official PySAT API
reference are supported. The report cannot be compiled in the current
environment.
The next concrete step is to use a verified LaTeX environment with `cas-sc.cls`
and an SVG-capable build path, then perform the final PDF review. The report
was updated in this phase; benchmark artifacts were not changed.

Final recommendation: **NOT READY — BLOCKED**. The next action requiring user
approval is to provide or select a verified LaTeX distribution containing
`cas-sc.cls` and a compiler. After that, compile in an isolated build
directory, resolve SVG inclusion, and perform the PDF visual check.

