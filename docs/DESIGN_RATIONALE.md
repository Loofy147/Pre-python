# Design rationale: seven auditors, not one score

This document records the design's motivating argument, the parts now implemented, and the places where the current evidence is still incomplete.

## Premise

chipcup is a CI auditor for a Python distribution's public-API lifecycle. It verifies the distribution through seven real packaging and compatibility systems. Its output is a multi-sorted evidence record because the seven results have different meanings and provenance: module identity, version relation and specifier membership, marker truth, static typing, artifact consistency, license/file coverage, and warning chronology.

The report does have a convenience `passed` property. That property is the conjunction CI needs; it is not a score, a ranking of risk, or a replacement for the independent results.

## The seven contracts

| Boundary | Rule enforced | Known loophole or limit | Observable signal | Downstream effect |
|---|---|---|---|---|
| imports | A canonical module name resolves through `sys.modules`; repeated import returns the same module object. PEP 562 exposes root names without mutating the root module dictionary. | A PEP 420 namespace's search locations are ordered; an earlier location can shadow a submodule from a later location. | ImportError / ModuleNotFoundError and the reported module origin/search locations. CLI maps a missing module to exit code 3. | Supplies the imported `__version__` and package identity compared with installed distribution metadata. |
| versions | PEP 440 parses the imported and installed versions and applies the configured specifier to each marker row. | Public-version equality can accept a local version: `1.0+local` satisfies `==1.0`. | `InvalidVersion` from `packaging.version.Version`; version-relation and membership fields in the report. | Determines which marker rows are in scope for this release. |
| markers | PEP 508 evaluates each platform/extra row against an explicit environment. | `extra == "gpu"` is false when no extra is selected; merely declaring the row does not make it true. | `marker-eval row=… result=False`. | Selects the actual contract sets loaded through `chipcup.types.load`. |
| types | Mypy checks the declared protocol/variance contracts; explicit `Any` is rejected and type-ignore comments need error codes. The audit compares source `__all__` names with the wheel's literal exported surface. | Runtime-checkable protocols are shallow. A structural check is not proof of method semantics or static type safety. | Mypy error codes, unknown stub-set names, missing wheel-export names, and variance result. | Supplies the names and contracts the archive audit must find in the wheel. |
| build | The sdist and wheel agree on identity, `Requires-Dist`, top-level packages, public `__all__`, and PEP 639 license metadata. Static versions are checked; dynamic versions need a recognized deterministic setuptools attribute/file hook that resolves to the metadata version. CI builds the wheel from the sdist. | The wheel alone does not attest which backend produced it. A backend declaration in the sdist is not a cryptographic build attestation. | `python -m build` failure, identity/metadata differences, or an indeterminate version hook. | Provides the archive member manifests consumed by license coverage. |
| licenses | The distribution SPDX expression is parsed; each `License-File` and supplemental custom LicenseRef text is checked in the source tree and both archives. A custom reference also names the file it covers. | A syntactically valid SPDX expression is not proof that an identifier is current or that a license grant is legally compatible. | Missing source/file/archive coverage, unresolved LicenseRef mapping, or missing subject-file coverage. | An unresolved license dependency blocks a deprecation schedule that names that LicenseRef. |
| deprecations | A removal schedule needs actual `DeprecationWarning` evidence on every required, selected native platform row. Its effective warning start is the latest first-observed release across those rows. | A warning shipped in a release, or a marker evaluated without calling the deprecated API, is not proof that a warning was emitted on that platform. | Native platform JSON observation, missing-row report, unpublished-release or platform mismatch issue. | Supplies a warning chronology to the console audit; the CLI runs the composition in a fresh process rather than adding an import edge back into imports. |

The dependency graph and implementation boundaries are documented in [ARCHITECTURE.md](ARCHITECTURE.md). The subpackages are useful only while these concrete checks remain separate and testable.

## A boundary scene

A version maintainer and a marker maintainer discuss adding an optional GPU contract:

> **Versions:** "The GPU extra widens the supported contract set; it does not add a version condition by itself."
>
> **Markers:** "The marker is true only when the GPU extra is selected. The version policy decides whether this release is in scope."
>
> **Versions:** "Then the compatibility floor should be a lower bound, not an exact pin."

The implemented resolution is: a PEP 440 row specifier admits the release, the PEP 508 marker selects the GPU row, and the type boundary calls `chipcup.types.load("gpu")`. The public API is unchanged; a future minimum can be expressed as `>=1.4` instead of over-constraining consumers to `==1.4`.

This is an executable dependency, not just a dialogue: tests verify the marker result and that the selected name loads the actual `AuditReceipt` and covariant `Reader` protocols.

## The license paradox

The Python package is MIT. The fixture's alternative grant is limited to `fixtures/chip.dat`.

The tempting metadata expression `MIT AND LicenseRef-Fixture-Dual` would state that the distribution as a whole has both grants. PEP 639's `License-Expression` is distribution-level metadata; it does not attach an independent expression to one file. chipcup therefore leaves the distribution expression as MIT and uses a supplemental, auditable mapping:

```text
LicenseRef-Fixture-Dual
  → LICENSES/Fixture-Dual.txt
  → fixtures/chip.dat
```

The audit verifies the license text is declared as `License-File`, exists in the source tree and both archives, and that the subject fixture itself exists in the source tree, sdist, and wheel. The custom file is not represented as a nested SPDX expression and is not claimed to change the distribution-level MIT expression.

## Reducibility: where a reduction stops

The systems are not substitutes for one another:

- Import identity is process-local state; PEP 440 defines an order and specifier predicate.
- A version specifier cannot express `sys_platform == "linux"`.
- A marker Boolean cannot express static variance or a type judgment.
- A type judgment cannot establish a PEP 517 isolated build or archive contents.
- A build hook cannot replace SPDX expression and file-coverage checks.
- An SPDX expression has no release chronology or warning-emission event.
- A warning class has no semantics for rebinding `sys.modules`.

There is one partial reduction: a removal target can be represented by a PEP 440 specifier such as `>=2.0`. That records the intended version boundary. It cannot establish that the warning was actually emitted on required platforms, nor when that happened. The event evidence remains a separate sort.

PEP 440 versions are totally ordered; the Boolean specifier result and the temporal warning record must not be described as a partial order of PEP 440 versions.

## Counterfactual origin story

A plausible motivating team had repeatedly broken downstream consumers and could not tell from one artifact whether a public name had been warned about, on which platforms, with which typing contract, or under which license-file coverage. They kept a deformed reference fixture, `fixtures/chip.dat`, and added one audit boundary for each question.

This is a counterfactual design story, not a claim about the actual history of this repository. The fixture is a small reproducible subject for the file-coverage test; the chipped-teacup reference is only its name and data, not a technical argument.

## Falsification and weakest coupling

**Genuine couplings:** imports→versions, versions→markers, markers→types, build→licenses, and licenses→deprecations all pass data needed by the next boundary. The types↔build relationship is also real: build consumes the runtime `AuditReceipt`, while types exposes `BuildEvidence` through the PEP 562 lazy export.

**Weakest coupling:** build→licenses. The license boundary consumes actual sdist/wheel manifests, which is stronger than source-only assumptions, but backend provenance is not attested by the wheel itself. Building the wheel from the sdist narrows that uncertainty; a signed build attestation would be stronger evidence.

**Most likely to collapse:** the deprecation schedule's version interval is partly expressible as a version specifier. The residual work is not: confirming that a warning was emitted on every required platform and recording when. A downstream dependency that pins a minor version can still break when a public name is removed; this audit does not infer downstream adoption or consumer constraints.

**Decorative element:** the chipped teacup is not a governing formal system. It survives only as the fixture data in `fixtures/chip.dat`.

A boundary should be removed if tests show another boundary can prove the same fact with the same provenance and without changing the report's meaning. A boundary should be split if it starts combining verdicts with incompatible evidence.

## Removal-window question

If a name's warning was emitted only on a platform row the current marker matrix never selected, the removal window does **not** begin at the release that merely shipped the warning, nor at the release that only evaluated a marker. Under chipcup's policy, it begins only after actual `DeprecationWarning` emission has been observed for every required, selected native row. The effective start is the latest first-observed release across those rows. A required row that never emitted the warning keeps removal blocked.

If the platform is no longer supported, maintainers must explicitly revise the required matrix and record that compatibility decision. The audit must not treat an unselected row as successful.

This schedule is chipcup's project policy informed by compatibility practice. PEP 387 governs CPython; it does not impose this interval on third-party packages. Its detailed rules should not be misquoted as a universal third-party deprecation period.
