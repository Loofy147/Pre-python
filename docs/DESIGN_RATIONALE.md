# Design rationale

## 1. The product thesis

The project began as a seven-boundary Python packaging/lifecycle experiment. The more valuable direction is an evidence-driven release-assurance coordinator.

The key question is not whether a package has seven checks. It is whether the project can prove that a particular release satisfies the compatibility and supply-chain policy declared for it.

The product's differentiator, if demonstrated, will be the relationship among API changes, warning history, supported environments, artifacts, provenance, and policy. Individual tools already perform many underlying checks.

## 2. Why evidence before implementation breadth

A check is valuable only when its subject and limitations are explicit. For example:

- “Twine check passed” means the relevant description-rendering check passed; it does not prove complete artifact integrity.
- “The wheel contains the stub file” proves file presence; it does not prove semantic agreement with runtime contracts.
- “A warning was recorded in JSON” proves that the JSON contains an observation; it does not authenticate the collector or the environment.
- “Build isolation was asserted” is not a cryptographic provenance proof.
- “The sdist and wheel metadata match” does not prove all distributable source files match.

The evidence contract must preserve these distinctions.

## 3. Why results remain multi-dimensional

API compatibility, warning chronology, license validity, marker selection, version policy, artifact integrity, and provenance are different kinds of judgments.

One score hides important failures. A release report should preserve each rule result, its evidence, and its scope. A final decision may be single-valued, but the underlying report must not be.

## 4. Existing tools are dependencies, not competitors to rewrite

Griffe provides API snapshot comparison. pydistcheck and other packaging tools inspect archive quality. packaging implements PEP 440 and PEP 508. Twine provides description rendering checks. SPDX publishes license identifiers. PyPI exposes PEP 740 attestations.

chipcup should use these capabilities and add the missing relationships between their outputs. Reimplement a mechanism only when a tested gap requires it.

## 5. The teacup fixture

The teacup is deliberately load-bearing. fixtures/chip.dat contains the measured payload, and the notch geometry determines a numeric tolerance. The 2.40 mm golden notch produces a 0.12 mm tolerance. This gives the project one simple, falsifiable artifact mutation test.

The fixture proves that the geometry checker responds to a controlled perturbation. It does not prove artifact parity, provenance, API compatibility, or license correctness. Those claims need their own evidence.

## 6. Seven evaluators are not the final product constraint

The current seven evaluator modules are useful isolated experiments. The final architecture should be driven by the evidence and dependency model. A new evidence adapter should be added when it contributes a distinct, testable fact or relationship—not because a seven-system taxonomy needs an eighth system.

## 7. Why an evidence graph is justified

A deprecation-removal claim depends on more than a warning function:

- the API existed in a base release;
- the candidate changes or removes the API;
- the project's policy defines required environments;
- warning observations exist for those environments;
- the observations refer to published releases or permitted pre-release evidence;
- the required release interval elapsed;
- the candidate artifact corresponds to the reviewed source;
- an approved exception does not alter the decision.

These facts have different subjects and timestamps. A graph of evidence and claims is a natural representation.

## 8. Known architectural debt

The current repository has two orchestration paths: runtime receipt-cycle orchestration and gate.py's GateReport path. It has a type-stub presence system whose manifest does not semantically match its GPU runtime mapping. It relies on a caller-supplied build-isolation flag. It does not retain historical release evidence. The current CI does not install the exact wheel it just built.

These are implementation gaps, not reasons to abandon the product. They are Stage 0 work and must be resolved before the project claims release assurance.

## 9. How to judge whether the project succeeds

The project succeeds only if a reproducible comparative benchmark demonstrates that it adds practical value over the toolchain already available to a Python maintainer.

A distinct result could be a connected finding such as:

- a specific API removal;
- the exact policy-required platform that did not emit the warning;
- the release history that fails the removal interval;
- the candidate wheel digest that would be published;
- the provenance record or lack of one;
- the exact policy rule that blocks release.

If the existing tools already detect all the same issues and chipcup adds no useful relationship, the differentiation claim is not established. A convenient aggregator can still be useful, but should be positioned honestly.
