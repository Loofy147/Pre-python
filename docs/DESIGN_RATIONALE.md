# Design rationale and adversarial review

## Why seven evaluators remain separate

The seven boundaries consume different evidence and emit distinct failure modes: module identity, version ordering/specifier membership, marker truth, static type judgments, artifact metadata and payload facts, SPDX/file coverage, and warning chronology. A shared receipt envelope permits orchestration but does not collapse these verdicts into one score.

## Delta over existing tools

- Griffe reports API additions/removals; chipcup binds an API change to native warning observations and the exact wheel that ships the replacement.
- mypy proves static typing judgments; chipcup additionally checks the declared stub set is physically present in the wheel and within the licence coverage evidence.
- Twine validates distribution metadata; chipcup compares source/wheel payloads and joins the results to marker-selected warnings and API lifecycle state.
- packaging implements PEP 440/508; chipcup retains version and marker decisions as linked receipts that select subsequent evidence checks.

## Reducibility counterexamples

- An identical marker matrix can have missing or emitted warning observations; marker truth does not encode deprecation chronology.
- One module object can retain identity while its imported version violates a release specifier; import identity does not encode PEP 440 matching.
- An identical archive member list can have different SPDX expressions; build inventory does not encode licence semantics.
- A passing SPDX declaration can coexist with a missing stub file; licence resolution does not prove a typed API exists.
- A passing type contract can coexist with a false platform marker; typing does not encode environment evaluation.
- An identical release schedule can coexist with two different module identities; PEP 387-style chronology does not encode import cache identity.
- A passing version specifier can describe an artifact whose sdist/wheel metadata diverges; PEP 440 does not encode PEP 517 build consistency.

These are testable counterexamples, not a claim that the governing PEPs mandate chipcup's software decomposition.

## Geometry as a load-bearing fixture

The golden fixture is not a metaphor. `fixtures/chip.dat` contains measured rim and notch coordinates. The golden depth is 2.40 mm, and five percent of that depth gives a 0.12 mm tolerance. Source, sdist and wheel payloads are checked against the same golden coordinates. CI proves that a 0.05 mm perturbation remains in tolerance and a 0.13 mm perturbation fails.

## License paradox

PEP 639's archive-level `License-Expression` cannot by itself express a separate per-file grant. The distribution remains MIT. A supplemental SPDX `LicenseRef-Fixture-Dual` record resolves to shipped text and identifies the fixture subject; CI validates both the License-File and subject path in both artifacts. This is project metadata, not a claim that the core metadata field scopes expressions to paths.

## Breaking-change boundary

The version floor and the marker environment can be changed without renaming a symbol. A new release can raise a dependency specifier while a PEP 508 row controls which supported environment receives that dependency. The stable public name remains available through the compatibility window.

## Weakest edge and likely collapse

The weakest edge is licenses → types: an archive-level distribution expression may be too coarse to answer a future organization’s file-level policy. The typed evaluator therefore requires an explicit stub manifest and a verified license receipt before considering contract sets available.

The most likely collapse is deprecations into versions. Both observe release chronology, but they differ whenever a warning shipped without being executed on a required target platform. A falsification test holds release history constant while varying native warning observations; if the deprecation verdict does not change, the boundary has no distinct operational value.

## Open-ended research question

If a platform marker stops selecting an environment while its previously emitted warning remains in the release history, can the import evaluator safely expose a PEP 562 deprecated alias, or does the removal clock remain blocked by the PEP 387-informed project policy?
