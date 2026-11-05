# Status and implementation truth

**Review snapshot:** 2026-11-05  
**Reviewed main commit:** 7ef2c82fb2ebdf2e08376b154bd6e9f112b6a5ca  
**Distribution version:** 0.1.0  
**Package maturity:** Alpha

This document is the source of truth for what the current repository does and does not do. It prevents the target architecture from being mistaken for shipped functionality.

## Repository evidence

| Item | Observed state |
|---|---|
| Default branch | main |
| Latest inspected main commit | 7ef2c82fb2ebdf2e08376b154bd6e9f112b6a5ca |
| Main CI run | 42054977699, completed successfully |
| CI matrix | Python 3.10–3.14 on Ubuntu; Python 3.13 native platform jobs on Ubuntu, Windows, and macOS |
| Build audit | Builds an sdist, builds a wheel from the sdist, runs Twine description checks, then runs the receipt cycle |
| Open pull request at snapshot | #4, proposing stable audit exit codes; not merged into the reviewed main commit |
| GitHub Releases | None found |
| Git tags | None found |

The main CI result establishes that the jobs configured in that workflow passed for that commit. It does not establish that the full target architecture is implemented.

## Capability status

| Capability | Status | What the current source actually proves |
|---|---|---|
| Seven-boundary receipt cycle | IMPLEMENTED, prototype | Runtime composes build, license, type, marker, deprecation, import, version, and cycle-closure receipts |
| Closed verdict vocabulary | IMPLEMENTED | AuditVerdict is a string enum; BoundaryReceipt rejects non-enum verdict values |
| Measured teacup fixture | IMPLEMENTED, with robustness defect | Source, sdist, and wheel fixture copies are checked against a golden profile and a derived tolerance |
| Basic sdist/wheel metadata comparison | IMPLEMENTED, partial | Compares name, version, Requires-Dist, package names, literal public exports, and license metadata |
| Complete file-content equivalence | NOT IMPLEMENTED | No canonical hash comparison of every distributable source/data member across source, sdist, and wheel |
| License expression grammar | IMPLEMENTED, partial | A custom parser handles a subset of SPDX expression grammar and LicenseRef mapping |
| Authoritative SPDX identifier validation | NOT IMPLEMENTED | The parser does not validate identifiers and exceptions against a pinned SPDX License List |
| License file and fixture-subject coverage | IMPLEMENTED, partial | Checks declared license files and configured subject paths in source and archive manifests |
| Stub manifest and file presence | IMPLEMENTED, partial | Checks declared paths and py.typed presence; does not establish semantic agreement with runtime contracts |
| API snapshot comparison across releases | NOT IMPLEMENTED | No Griffe adapter or baseline API snapshot store |
| Version and environment marker evaluation | IMPLEMENTED, prototype | Uses packaging to evaluate version specifiers and marker rows |
| Native warning capture | IMPLEMENTED, limited | Captures DeprecationWarning observations on CI native platform jobs |
| Warning-evidence authenticity | NOT IMPLEMENTED | JSON fields are caller-editable; the loader does not authenticate collector identity or bind the observation to a published artifact |
| Marker selection validation | IMPLEMENTED, with scope defect | Unknown stub-set validation currently examines every version-in-scope row, including rows whose marker expression evaluates false |
| Historical deprecation eligibility | NOT IMPLEMENTED, end-to-end | The current CLI supplies only release 0.1.0 as published history and uses a no-removal schedule |
| Durable evidence history | NOT IMPLEMENTED | Evidence JSON is input/output, not a persistent append-only ledger |
| Independent build provenance verification | NOT IMPLEMENTED | A command-line flag controls the build-isolation claim; no attestation is verified |
| PyPI PEP 740 or SLSA verification | NOT IMPLEMENTED | No verifier or PyPI Integrity API adapter is present |
| Audit of exact installed wheel | NOT IMPLEMENTED | CI installs the checkout in editable mode before building artifacts; it does not install the newly produced wheel in a clean environment for the receipt cycle |
| Unified execution architecture | INCONSISTENT | runtime.py runs the receipt pipeline; gate.py exposes a separate legacy-style GateRequest/GateReport path |
| Release decision policy engine | NOT IMPLEMENTED | Current output is a Boolean passed field plus receipts; no distinct ALLOW / DENY / APPROVAL_REQUIRED layer |
| Comparative differentiation benchmark | NOT IMPLEMENTED | No controlled comparison against the existing ecosystem toolchain |
| Reusable GitHub Action | NOT IMPLEMENTED | GitHub Actions workflows exist for this repository, not as a reusable published action |

## Confirmed documentation contradictions

1. README previously described exit code 1 as any failed or unverified verdict and code 3 as a missing module. An open pull request proposes a different detailed exit mapping. The current main CLI remains authoritative until that change is merged and verified.
2. The package describes seven lifecycle systems, but it has no cross-release API snapshot integration. It must not claim it detects arbitrary API removals across published releases.
3. The build receipt includes a build-isolation Boolean. That is not an attestation and does not prove provenance by itself. The CLI defaults it to false, but the direct evaluate_artifact_receipt() function currently defaults it to true, creating an unsafe API-level default discrepancy.
4. The type receipt checks manifest file presence, not semantic equality between .pyi declarations and runtime contract objects.
5. The deprecation receipt validates warning observations but the CLI hardcodes the published release list to 0.1.0 and uses a schedule with no removal release. Unit tests exercise some removal-window rules, but the end-to-end CLI does not establish a historical removal-eligibility decision. Warning JSON is editable, and the loader does not enforce consistency between emitted and warning_count (or authenticate the claimed native platform).
6. The release workflow accepts version-shaped tags but contains fixed 0.1.0 paths and warning-evidence arguments. The tag/version relationship is not derived and enforced generically.
7. Twine's check command should be described as a distribution-description rendering check, not a complete metadata or artifact-integrity validator.
8. gate.py and runtime.py are separate orchestration paths. The project has not yet declared one as the sole stable API.

## High-priority implementation defects identified by source review

These are code-review findings, not claims that fixes have already landed.

### P0 — Geometry must fail closed for invalid numbers

The geometry parser uses Python JSON decoding and numeric type checks that accept non-finite float values and Boolean values as numbers. NaN can produce comparison behavior that does not reliably fail a max-deviation check. Reject NaN, positive/negative infinity, booleans, invalid tolerance fractions, zero/negative depth, and malformed coordinates before arithmetic.

### P0 — Caller assertions must not become provenance proofs

The receipt builder accepts a Boolean build-isolation assertion. The CLI exposes this as a flag. Keep this evidence in an asserted/unverified class until build provenance is independently checked against a trusted CI identity and the artifact digest. Also change the direct evaluate_artifact_receipt() default from true to false so callers cannot obtain a verified receipt by omitting the argument.

### P1 — Compare actual distributable contents

Metadata and __all__ equality do not prove that package source files are byte-identical across the intended source, sdist, and wheel representations. Define canonical package-relative paths and compare file hashes, with explicit policy for generated files, metadata, and platform-specific artifacts.

### P1 — Audit the exact produced artifact

The current CI installs the checkout with editable mode before building the artifacts. Add a clean isolated environment that installs the exact wheel produced from the sdist, then verifies import origin, installed metadata, and tested public behavior against that wheel.

### P1 — Resolve the type-contract mismatch

The GPU stub declares GpuStubContract, while the runtime STUB_SETS mapping returns AuditReceipt and Reader for the gpu set. The current manifest checks presence, not semantic correspondence. Either implement semantic checks with clear scope or remove the stub system until it has real value.

### P1 — Unify the execution paths

Select one authoritative pipeline and define the other as a compatibility wrapper or remove it. The receipt pipeline and GateReport pipeline must not drift in release semantics.

### P1 — Fix marker row scope and validation

The marker receipt currently checks whether every version-in-scope row names a known stub set, even if its PEP 508 expression evaluates false. Validate contract-set availability only for selected rows, while separately enforcing that all policy-required rows are declared. Add false-marker rows with unknown contract names as regression cases.

### P1 — Authenticate and validate warning observations

The current JSON loader trusts editable emitted/platform/release fields and does not require emitted=true to agree with a positive warning_count. It also accepts booleans as integer warning_count values. Validate the data contract, reject duplicates and inconsistent fields, and bind observations to a trusted CI identity, source commit, release, native environment, and matrix row.

### P1 — Implement real release history

Load published releases and immutable warning observations for every policy-required row. Reject missing, duplicated, stale, forged, or scope-mismatched observations. Calculate a removal decision only after the policy's actual published-release requirements are met.

### P1 — Derive release identity from the tag

The release workflow must parse the tag, compare it to pyproject.toml, and use the validated version for every build, evidence, and publication step. A mismatched tag must block release.

### P2 — Validate SPDX identifiers

The current parser is not an authoritative SPDX identifier validator. Pin a License List version or return UNVERIFIED when the required authoritative data is unavailable. The official list is versioned and machine-readable.

## Exit-code status

On reviewed main, the CLI returns 0 for a passed report, 1 for a failed report or general audit exception, and 3 when a required module cannot be imported. Invalid argparse input uses argparse's own usage-error behavior. Pull request #4 proposes a more detailed contract; it must be reviewed against this status document and the agreed type-surface scope before merging.

## Review rule

A capability can move from NOT IMPLEMENTED or PARTIAL only when its code, tests, and reproducible evidence exist on a named commit. A passing unit test does not by itself prove provenance, cross-release history, or performance against existing tools.
