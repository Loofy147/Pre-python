# chipcup

**chipcup audits Python distribution lifecycle evidence across seven independent systems.** It is designed for the gap between API-diff tools, static type checkers, archive validators and platform CI: no one of those tools alone proves that a removal was warned on every required platform, that the replacement stubs exist in the exact wheel, and that the shipped files have resolvable licence evidence.

Closest tools remain useful:
- **Griffe** compares Python API surfaces; chipcup adds native warning chronology and binds it to exact built artifacts.
- **mypy** checks static typing; chipcup verifies that the declared stub contract files are present in the exact wheel and have licence coverage.
- **Twine** validates distribution metadata presentation; chipcup additionally compares the sdist and wheel payloads and evaluates the API lifecycle.
- **packaging** evaluates PEP 440 versions and PEP 508 markers; chipcup preserves those results as evidence linked to warning and artifact receipts.

## Install and run

```bash
python -m pip install "chipcup[test]"
python -m chipcup.cli --sdist dist/chipcup-0.1.0.tar.gz \
  --wheel dist/chipcup-0.1.0-py3-none-any.whl \
  --matrix fixtures/audit-matrix.json \
  --warning-evidence warning-evidence/ --project-root . \
  --build-isolation-verified
```

Without `--build-isolation-verified`, artifact metadata and contents are still inspected but `BUILD_PROVENANCE=UNVERIFIED`; the flag is an explicit caller attestation that the archives were built in isolation. CI supplies it only after its isolated build steps. The installed console command is `chipcup.audit`. Its module imports only the standard library until `main()` is entered. The entry point then lazily imports `chipcup.runtime`, which loads the seven evaluators and passes immutable receipts between them.

### Stable process exit codes

The JSON report remains multi-sorted: every boundary keeps its own verdict, state, evidence and issues. The process status is a deterministic summary only; it never replaces the report.

| Exit | Meaning |
|---:|---|
| 0 | Every required receipt is verified (`PASS` or `NOT_APPLICABLE`) |
| 1 | Unexpected audit/runtime error or malformed receipt state |
| 2 | Required deprecation warning was not observed on every selected platform row |
| 3 | SPDX expression, LicenseRef mapping or shipped license coverage failed |
| 4 | Golden fixture is missing, malformed or outside its geometry tolerance |
| 5 | Typed public surface or selected stub contract failed |
| 6 | sdist/wheel metadata, exports or build provenance diverged |
| 7 | Required build artifact/provenance is unavailable or unverified |
| 8 | Required marker matrix or contract-set selection failed |
| 9 | Canonical import identity or public import surface failed |
| 10 | Imported/installed version identity or PEP 440 policy failed |
| 11 | Built artifact and installed distribution release identities differ |
| 12 | Required audit module could not be imported |
| 13 | A required receipt is missing or remains unverified |

When multiple fatal outcomes coexist, the later entry wins in this **lowest-to-highest precedence order**:

`AUDIT_ERROR (1) < AUDIT_UNVERIFIED (13) < DEPRECATION_UNPROVEN (2) < TYPE_SURFACE_INVALID (5) < MARKER_MATRIX_INVALID (8) < IMPORT_AUDIT_FAILED (9) < VERSION_MISMATCH (10) < BUILD_RELEASE_IDENTITY (11) < BUILD_DIVERGENT (6) < LICENSE_UNRESOLVED (3) < FIXTURE_GEOMETRY (4) < BUILD_UNAVAILABLE (7)`.

The order is explicit and intentionally independent of numeric exit-code order. Missing receipts never count as success. The JSON report is printed before the selected exit is returned. The mapping and precedence are implemented in `chipcup.exit_codes` and exercised by unit and CLI tests.

## Seven receipt boundaries

`build → licenses → types → markers → deprecations → imports → versions → build`

| Evaluator | Governing mechanism | Required evidence |
|---|---|---|
| `build` | PEP 517/621 | sdist/wheel metadata, contents, backend provenance, fixture geometry |
| `licenses` | SPDX / PEP 639 | SPDX expression, declared License-Files, LicenseRef text and archive manifests |
| `types` | PEP 484/544/695 and PEP 561 | variance, stub-contract manifest, wheel stub files, `py.typed` |
| `markers` | PEP 508 | explicit environment and extra evaluations selecting only known contract sets |
| `deprecations` | project policy informed by PEP 387 | actual `DeprecationWarning` observations for every selected required platform |
| `imports` | PEP 420/562 and `sys.modules` | namespace resolution, public names, canonical module identity and alias state |
| `versions` | PEP 440 | imported/installed version equality, ordering and specifier membership |

Each receipt has its own named verdict and one of `PASS`, `FAIL`, `UNVERIFIED` or `NOT_APPLICABLE`. Unverified evidence never counts as passing. The JSON report retains the evidence per boundary; it does not compress unlike results into a score. Every named verdict is a member of the closed `AuditVerdict(str, Enum)` vocabulary, and each boundary exposes a distinct degradation helper.

## Load-bearing golden fixture

`fixtures/chip.dat` contains measured rim/notch coordinates for a chipped teacup. Its golden notch depth is 2.40 mm. The tolerance is derived as five percent of that depth: **0.12 mm**. The build evaluator validates the source fixture and the copies embedded in both the sdist and wheel. A 0.05 mm perturbation passes; a 0.13 mm perturbation fails with `FIXTURE_GEOMETRY_OUT_OF_TOLERANCE`.

The golden geometry reference is `fixtures/golden-profile.json`; both files are shipped in the sdist and wheel.

## Receipt edges and import isolation

Evaluators do not import one another. They exchange neutral records from `chipcup._contracts`; the runtime orders those receipts along the declared cycle. The single module-load boundary is `chipcup.cli:main → chipcup.runtime`, imported inside `main()`. CI rejects evaluator-to-evaluator imports and verifies that importing `chipcup.cli` does not load the runtime.

## Degraded operation

If a prerequisite receipt or evidence source is absent, that boundary emits its named `UNVERIFIED` verdict. The downstream boundary cannot turn missing evidence into a pass. CI forces each missing-prerequisite path and asserts the seven verdict names.

## Standards and scope

PEP 387 is CPython's compatibility policy. The requirement for one published project minor cycle after the required warning observations is chipcup's explicit project policy, not a claim that PEP 387 mandates that schedule for third-party distributions.

PEP 639's distribution-level `License-Expression` does not assign a separate expression to each file. chipcup declares the distribution as MIT and tracks the fixture-specific alternative grant through a supplemental `LicenseRef-Fixture-Dual` mapping and shipped text. This is checked independently of archive-level metadata.

See [Architecture](docs/ARCHITECTURE.md), [Design rationale](docs/DESIGN_RATIONALE.md), and [open questions](docs/OPEN_QUESTIONS.md).
