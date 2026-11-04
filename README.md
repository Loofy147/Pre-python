# chipcup

**chipcup** is a CI auditor for a Python distribution's public-API lifecycle. It evaluates seven packaging and compatibility systems in sequence and retains their results as a multi-sorted report. A report contains independent import, version, marker, typing, build, license, and deprecation evidence; it does not collapse those different verdicts into a numerical score.

The reference fixture is deliberately small: [fixtures/chip.dat](fixtures/chip.dat). The chipped teacup is data used by the audit, not a second product metaphor.

## Install and run

For a source checkout:

```bash
python -m pip install -e ".[test]"
python -m pytest
python -m mypy
python -m build
python -m twine check dist/*
```

Run the distribution audit after building an sdist and a wheel from that sdist:

```bash
python -m chipcup.cli \
  --sdist dist/chipcup-0.1.0.tar.gz \
  --wheel dist/chipcup-0.1.0-py3-none-any.whl \
  --matrix fixtures/audit-matrix.json \
  --warning-evidence warning-evidence/ \
  --project-root .
```

The `--warning-evidence` directory contains one JSON observation captured by each native platform job. It is required: marker simulations alone do not prove that a `DeprecationWarning` was emitted on a real target. The platform collector is `scripts/capture_warning_evidence.py`.

The installed command is `chipcup.audit`. It returns exit code **0** when all boundaries pass, **1** when the audit fails or cannot establish a required contract, and **3** when a required module cannot be imported.

The package requires Python 3.10 or newer and currently declares version `0.1.0` as an alpha implementation. The version is static in `pyproject.toml`; the audit checks that the imported `chipcup.__version__` equals `importlib.metadata.version("chipcup")`.

## The seven boundaries

| Subpackage | Governing system | Work performed |
|---|---|---|
| `imports` | Python import machinery, PEP 420, PEP 562, `sys.modules` | Checks repeat-import object identity, declared public names, namespace-package behavior, and version-filtered entry-point discovery. |
| `versions` | PEP 440 | Parses versions, checks specifiers, compares imported and installed distribution versions, and selects in-scope marker rows. PEP 440 versions have a total ordering; specifier matching is a predicate. |
| `markers` | PEP 508 | Evaluates marker rows against explicit environments and requested extras. Each result records its row, Boolean verdict, stub set, and diagnostic line. |
| `types` | PEP 484/544 and PEP 561 | Defines typed public contracts and a covariant generic protocol, identifies selected contract sets, and compares source `__all__` surfaces with exports found in the wheel. It uses Python 3.10-compatible `TypeVar` syntax; PEP 695 type-parameter syntax is deliberately not used while Python 3.10 remains supported. `py.typed` marks the package as typed. |
| `build` | PEP 517/621 and Core Metadata | Inspects sdist/wheel metadata and contents; checks project identity, `Requires-Dist`, package names, literal `__all__` exports, license metadata, and static version provenance. |
| `licenses` | PEP 639 and SPDX expression grammar | Parses the distribution's SPDX expression, checks declared license files in source/sdist/wheel, and resolves custom file-scoped LicenseRef evidence. |
| `deprecations` | Project policy informed by PEP 387 | Records actual `DeprecationWarning` observations for selected marker rows and derives the effective warning start only after all required rows have emitted. |

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the dependency graph and result types, and [docs/DESIGN_RATIONALE.md](docs/DESIGN_RATIONALE.md) for the boundary scene, counterfactual motivation, reducibility test, and falsification targets.

## The dependency chain

```text
imports → versions → markers → types → build → licenses → deprecations
                               ↖__________↗
                                  lazy edge
```

The static chain expresses data dependencies: each boundary consumes evidence from the preceding one. The `types` to `build` edge is lazy through the types module's PEP 562 `__getattr__`, because build imports the runtime `AuditReceipt` protocol from types. This prevents an import-time cycle while retaining a real two-way type/build contract.

The final `chipcup.audit` console entry point invokes the full audit in a fresh process. It is the composition boundary; `deprecations` does not import `imports` to close a Python module cycle.

## Why the report keeps separate verdicts

The underlying results have different shapes: module identity, PEP 440 order and specifier membership, marker Booleans, structural typing judgments, artifact metadata comparisons, SPDX/file-coverage evidence, and warning chronology. The JSON report preserves each of these records. Its convenience `passed` property is only the conjunction needed by CI; it does not replace or rank the individual findings.

## License model

The Python package is licensed under MIT. The distribution declares `License-Expression: MIT` and includes both `LICENSE` and `LICENSES/Fixture-Dual.txt` as `License-File` entries.

The fixture's alternative grant is tracked separately by chipcup's supplemental mapping:

```text
LicenseRef-Fixture-Dual → LICENSES/Fixture-Dual.txt
```

The audit requires that mapped text to exist in the source tree and both archives. This is intentionally not presented as PEP 639 file-scoping syntax: Core Metadata's `License-Expression` describes the distribution archive, not a per-file assignment of expressions. The supplemental mapping records the fixture-specific grant without changing the package's MIT expression.

## Scope limits

- The SPDX parser checks the expression grammar and custom-reference mapping. It does not embed the complete, time-varying SPDX License List and is not legal advice.
- The PEP 517 backend is read from the sdist's `pyproject.toml`. A built wheel alone does not attest which backend produced it. CI narrows that gap by building the wheel from the sdist in the same job.
- Type checks use inline annotations and explicit protocol contracts. The current wheel audit compares literal `__all__` surfaces; it is not a complete API compatibility checker for arbitrary dynamic exports.
- Runtime-checkable protocols are shallow structural checks. Mypy provides the static judgment; runtime protocol success does not prove implementation semantics.
- The removal-window rule is chipcup's own policy. PEP 387 governs CPython's compatibility policy, not third-party packages on PyPI.
- The audit's environment matrix is only as complete as its configured rows and CI jobs. A simulated marker row is not evidence that a warning was emitted on a real target platform; warning observations must come from the corresponding platform execution.

## Open design question

When a required marker row never emits the warning, the current policy keeps the removal blocked. The warning clock begins only after the warning has actually been observed on every required row. See [docs/OPEN_QUESTIONS.md](docs/OPEN_QUESTIONS.md) for the rationale and remaining questions.
