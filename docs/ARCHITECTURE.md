# Architecture and evidence contract

## Problem

API snapshot tools, type checkers and archive validators prove different parts of a release. chipcup binds their evidence to the exact sdist and wheel so a removal decision can be traced to warnings emitted on the required platforms, typed contract files shipped in the wheel, and licence data present in both artifacts.

## Runtime dependency order

```text
build → licenses → types → markers → deprecations → imports → versions → build
```

The edges are runtime receipt dependencies, not evaluator imports. Each evaluator consumes a neutral immutable receipt from `chipcup._contracts` and returns its own receipt. The runtime orchestrator alone sequences evaluators.

| Edge | Receipt passed | Why the downstream boundary needs it |
|---|---|---|
| build → licenses | exact sdist/wheel member lists and Core Metadata | licence coverage must inspect the artifacts already built, not request a rebuild |
| licenses → types | validated license expression, License-File and LicenseRef coverage | typed stub files are accepted only when they exist in the distribution under resolved licence coverage |
| types → markers | declared contract-set IDs and wheel stub paths | marker rows may select only contracts present in the verified stub manifest |
| markers → deprecations | selected row IDs and target platforms | removal windows require actual warning observations on each selected required platform |
| deprecations → imports | verified warning-window state | import audit checks the public alias state only after the removal policy is known |
| imports → versions | canonical module identity and imported version source | PEP 440 compares the version attached to the imported package with installed metadata |
| versions → build | installed version and specifier verdict | the build boundary closes by checking that the exact artifacts identify the same release |

### Import boundaries

- Seven evaluators may import `chipcup._contracts`, standard-library modules and external libraries. They may not import another evaluator.
- `chipcup.runtime` imports evaluators inside `run_receipt_cycle`; it does not import them at module load.
- `chipcup.cli` imports `chipcup.runtime` only inside `main()`. CI asserts that importing the console module alone does not load the runtime or evaluator packages.
- PEP 562 remains the root package's lazy attribute mechanism. PEP 420 namespace discovery is separately exercised by the import evaluator.
- The only lazy module import required to launch the audit is the `main() → runtime` boundary. Removing it leaves the console entry point without its dispatcher while preserving an importable CLI module.

## Seven systems and verdicts

Each evaluator reports a named result: `BUILD_PROVENANCE`, `LICENSE_COVERAGE`, `TYPE_SURFACE`, `MARKER_MATRIX`, `DEPRECATION_WINDOW`, `IMPORT_AUDIT` and `VERSION_HISTORY`. A receipt state is `PASS`, `FAIL`, `UNVERIFIED` or `NOT_APPLICABLE`. Missing evidence is never silently promoted to PASS. All named boundary and fixture verdicts are members of `chipcup._contracts.AuditVerdict`, a closed `str` enum; `BoundaryReceipt` rejects unregistered strings and serializes the enum's stable value.

### Process exit selection

`chipcup.exit_codes` maps every required receipt state to a stable integer exit code. It does not overwrite the receipt state or the JSON verdict. The precedence order is a named, tested tuple and is deliberately independent of integer ordering. In lowest-to-highest order it is `AUDIT_ERROR`, `AUDIT_UNVERIFIED`, `DEPRECATION_UNPROVEN`, `TYPE_SURFACE_INVALID`, `MARKER_MATRIX_INVALID`, `IMPORT_AUDIT_FAILED`, `VERSION_MISMATCH`, `BUILD_RELEASE_IDENTITY`, `BUILD_DIVERGENT`, `LICENSE_UNRESOLVED`, `FIXTURE_GEOMETRY`, then `BUILD_UNAVAILABLE`. The last applicable condition wins. `PASS` and `NOT_APPLICABLE` are non-fatal; `FAIL`, `UNVERIFIED`, and a missing required receipt are non-zero. A build receipt without isolation evidence has its own fatal exit, and fixture geometry failures have a distinct code from general artifact divergence.

## Build and fixture geometry

The build evaluator inspects an sdist and wheel without extracting them. It compares project identity, version, `Requires-Dist`, package names, public exports, licence metadata and backend/version provenance. It reads `fixtures/chip.dat` from the source, sdist and wheel.

The golden rim is the line through `(-3, 12)` and `(3, 12)` mm. The notch apex is `(0, 9.6)` mm, giving depth 2.40 mm. The allowed point deviation is five percent of depth: 0.12 mm. Every notch point is compared by Euclidean distance with the reference profile. The wheel and sdist must also contain the golden reference. The tests perturb the apex by 0.05 mm and 0.13 mm and assert pass/fail respectively.

## Licences and typed stubs

The distribution expression is MIT. The fixture has a supplemental file-scoped grant mapping `LicenseRef-Fixture-Dual → LICENSES/Fixture-Dual.txt → fixtures/chip.dat`. The checker confirms the mapping text and subject file appear in source, sdist and wheel. It does not claim PEP 639 natively assigns an expression to an individual path.

`src/chipcup/stub-contracts.json` declares four contract sets. Every path must exist in source and wheel; `py.typed` must ship. The distribution-level MIT licence applies to those stub files. PEP 695 syntax is exercised in the Python 3.12+ test lane while the installed package retains its Python 3.10 floor.

## Warning chronology

A marker simulation is not a warning observation. The platform collector invokes the public deprecated alias on the native CI OS and records the release, matrix row, platform, and whether a warning was emitted. The removal policy uses the latest first-observed release among required rows. A required row without an emitted warning blocks the window.

PEP 387 describes CPython's compatibility policy. chipcup's third-party project rule is an explicitly chosen one-published-minor-cycle requirement.

## Degraded operation

Each evaluator exports a uniquely named degraded receipt helper: `degraded_build_receipt`, `degraded_license_receipt`, `degraded_type_receipt`, `degraded_marker_receipt`, `degraded_deprecation_receipt`, `degraded_import_receipt` and `degraded_version_receipt`. Each result carries its boundary verdict with `UNVERIFIED` state. A missing prerequisite receipt also produces the same boundary-specific unverified result. CI invokes each helper and verifies the state/verdict pair. The runtime refuses to interpret an upstream `UNVERIFIED` or `FAIL` receipt as a downstream pass.

## Falsification tests

- `test_reducibility_counterexamples_preserve_distinct_failure_modes` gives the marker, warning, import, version, build and SPDX checks independently varying evidence.
- `test_no_evaluator_imports_another_evaluator` and `scripts/check_import_boundary.py` detect hidden evaluator import edges.
- `test_cli_module_does_not_import_runtime_until_main_entry` verifies lazy CLI loading.
- `test_notch_perturbation_uses_derived_tolerance` verifies the fixture has a measurable effect.
- `test_each_boundary_has_an_explicit_degraded_verdict` forces all seven degraded states.
