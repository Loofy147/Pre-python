# Validation and comparative benchmark

## Purpose

The project needs to prove two different things:

1. **Correctness:** invalid, contradictory, or insufficient evidence cannot produce an incorrect ALLOW decision.
2. **Differentiation:** the evidence relationships detect or explain important release defects that the existing toolchain does not reliably detect or connect.

A green CI run is not a substitute for either proof.

## 1. Current validation evidence

The reviewed main workflow includes:

- pytest on Python 3.10, 3.11, 3.12, 3.13, and 3.14;
- DeprecationWarning treated as an error;
- static evaluator import-boundary checks;
- degraded-operation and geometry mutation tests;
- mypy on the configured Python 3.13 lane;
- native platform warning collection on Ubuntu, Windows, and macOS;
- sdist build;
- wheel build from the sdist;
- Twine description-rendering validation;
- receipt-cycle release audit;
- workflow artifact upload.

The inspected main CI run 42054977699 completed successfully for commit 7ef2c82fb2ebdf2e08376b154bd6e9f112b6a5ca.

This is evidence for the configured jobs and tests only. It is not proof of semantic stub correctness, complete archive parity, signed provenance, historical deprecation eligibility, or cross-release API compatibility.

## 2. Existing test coverage map

| Test or workflow | Current purpose | What it does not establish |
|---|---|---|
| test_build.py | Basic sdist/wheel metadata and identity checks; dynamic-version hook test | Full package file-content parity or archive resource safety |
| test_licenses.py | License expression grammar, LicenseRef mapping, file and subject coverage | Complete SPDX identifier validity or legal acceptability |
| test_types.py | Runtime Protocol behavior and stub-set selection experiments | .pyi semantic correspondence with runtime contract |
| test_markers.py | PEP 508 evaluation and version-row selection | Policy completeness of a real platform support matrix |
| test_deprecations.py | Warning capture and schedule logic | Trusted historical evidence from published packages |
| test_imports.py | Lazy exports, module identity, namespace behavior, entry-point discovery | Safe execution of arbitrary candidate package code |
| test_versions.py | PEP 440 ordering and specifier behavior | Exact wheel installation and identity in a clean environment |
| test_execution_proof.py | Receipt cycle, teacup tolerance, degraded states, import constraints | Comprehensive false-pass resistance |
| test_cli.py | Current command behavior and import error output | Full stable exit-code contract |
| CI workflow | Matrix tests, native observations, sdist/wheel build and receipt audit | Independent provenance attestation or comparative advantage |

## 3. Required adversarial regression tests

Add tests before claiming the affected capability is robust.

### Geometry and parser safety

- NaN, positive infinity, negative infinity;
- Boolean coordinates and Boolean tolerance fraction;
- zero and negative notch depth;
- missing, duplicated, malformed, or non-finite coordinate values;
- extra JSON tokens and non-standard numeric constants;
- very large coordinate magnitudes and overflow cases.

### Archive integrity

- source file changed only in the wheel;
- source file missing only in the sdist;
- unexpected additional package file;
- duplicate normalized member path;
- malicious path names and link types;
- highly compressed oversized member;
- member-count and total-expanded-size limits;
- ambiguous fixture or metadata member suffixes.

### Receipt and evidence trust

- missing required receipt;
- unknown receipt state or verdict;
- malformed evidence type;
- stale evidence;
- wrong commit/artifact digest;
- duplicated observations;
- conflicting platform identity;
- emitted=true with warning_count=0;
- forged warning JSON;
- caller assertion without attestation;
- attestation with the wrong subject digest;
- untrusted builder identity;
- correction that supersedes an earlier result without deleting it.

### API and release history

- removed function with and without a warning;
- changed signature, default, type, re-export, and module path;
- warning on one required platform but not another;
- marker row no longer selected after policy change;
- warning evidence from an unpublished version;
- missing intervening published releases;
- tag version different from project metadata;
- wheel metadata version different from sdist or installed artifact.

## 4. Comparative baseline

The baseline must be declared before experiments run. A reasonable first baseline is:

- Griffe API snapshot comparison;
- pydistcheck and appropriate wheel/archive checks;
- Twine description check;
- mypy and existing unit tests;
- packaging for PEP 440 and PEP 508;
- version-pinned SPDX identifier validation;
- existing CI and available PyPI provenance verification.

Do not compare chipcup against a deliberately incomplete baseline. Record tool versions, configuration, input commit, artifact digests, platform, and outputs for every run.

## 5. Benchmark corpus

Use real public Python projects with explicit permission or their public repositories, plus a controlled synthetic package for deterministic mutants. Include:

- pure-Python library with a public API;
- library with native/platform-specific wheels;
- library using optional extras and markers;
- library with deprecated public aliases;
- package with dynamic version or generated files;
- package with multiple license files or LicenseRef metadata.

For each project, select a stable base release and candidate revision. Preserve all source refs and produced artifact digests.

## 6. Mutant matrix

Create controlled defects one at a time and in selected combinations.

| Mutant | Expected finding |
|---|---|
| Remove a public API member | API diff identifies removal |
| Remove without valid warning history | Deprecation policy denies or requires approval |
| Warning missing on one required platform | Platform evidence incomplete |
| Alter one wheel source file | Artifact parity failure |
| Replace wheel after attestation | Subject digest mismatch |
| Change release tag only | Release identity failure |
| Add unknown SPDX identifier | License validation failure or UNVERIFIED |
| Remove declared license text | License coverage failure |
| Omit required marker row | Policy scope incomplete |
| Reuse old warning evidence for a new commit | Subject binding/freshness failure |
| Supply forged observation JSON | Provenance check rejects it |
| Delete evidence required by a prior decision | Ledger integrity failure |

## 7. Measurements

Measure:

- true-positive detection rate for seeded defects;
- false-positive rate on unmodified releases;
- false-negative count;
- defects uniquely detected by chipcup over the declared baseline;
- evidence completeness per finding;
- subject-binding accuracy;
- reproducibility of decisions;
- execution time and peak memory;
- adapter failure and unavailable rates;
- number and severity of unresolved contradictions.

Do not combine these into one opaque quality score. Report each metric and its denominator.

## 8. Acceptance criteria for a genuine improvement claim

A differentiation claim requires:

1. a public and reproducible benchmark corpus;
2. an explicitly versioned baseline toolchain;
3. all mutants and expected outcomes declared before the run;
4. raw results and artifact digests published;
5. independent reproduction of key findings;
6. false-positive and false-negative analysis;
7. at least one demonstrated cross-tool or cross-release defect relationship that the baseline does not report as a connected policy conclusion;
8. no critical seeded false-pass in the release decision path.

If the baseline detects all defects and chipcup adds only a duplicate dashboard, the unique improvement has not been demonstrated. The product may still be useful as an evidence-reporting integration, but the positioning must say so.

## 9. Reproducibility package

Each benchmark release should publish:

- corpus manifest and source references;
- mutant definitions and patch digests;
- tool versions and environment lock;
- commands and configuration;
- raw tool outputs;
- normalized evidence records;
- benchmark scripts and tests;
- result summary and limitations.

A reviewer must be able to reproduce the benchmark without access to private assistant context or undocumented state.
