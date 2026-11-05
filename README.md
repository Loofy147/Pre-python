# chipcup

**chipcup audits Python distribution lifecycle evidence across seven independent systems.** It is designed for the gap between API-diff tools, static type checkers, archive validators and platform CI: no one of those tools alone proves that a removal was warned on every required platform, that the replacement stubs exist in the exact wheel, and that the shipped files have resolvable licence evidence.

Closest tools remain useful:
- **Griffe** compares Python API surfaces; chipcup adds native warning chronology and binds it to exact built artifacts.
- **mypy** checks static typing; chipcup verifies that the declared stub contract files are present in the shipped wheel and have licence coverage.
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

Exit codes: **0** means every required verdict is verified; **1** means a failed or unverified required verdict; **3** means a required module could not be imported.

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
