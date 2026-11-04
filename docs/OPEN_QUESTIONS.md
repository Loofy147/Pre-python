# Open questions for maintainers

These questions are deliberately open-ended. They describe decisions that need evidence, not checkboxes with predetermined answers.

1. What evidence should be sufficient to trust a third-party plugin discovered through the PEP 420 namespace and entry-point mechanism, and how should that evidence be revoked?
2. How should the package validate SPDX license identifiers against the evolving SPDX License List without making offline builds dependent on a network lookup?
3. When a LicenseRef is introduced, what documentation and file-level evidence should be required before a release can claim complete license coverage?
4. Which release-history source should become authoritative if tags, package-index versions and signed attestations disagree?
5. Under what conditions should a deprecation be soft rather than regular, and what observable evidence should justify keeping it indefinitely?
6. How should dynamic PEP 517 metadata be admitted without allowing the sdist and wheel to describe different projects?
7. Which properties should a type-audit receipt prove, and how can the build backend verify its provenance without pretending that static typing proves runtime safety?
8. What additional tests would falsify the claim that the seven contracts remain non-reducible in a future Python packaging environment?
9. Which compatibility guarantees should become stable before the package leaves alpha status?
10. What should constitute a trustworthy first-party release when a GitHub artifact, package-index artifact and source tag are not byte-identical?
