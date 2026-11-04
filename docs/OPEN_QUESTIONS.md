# Open questions for maintainers

These questions describe evidence and policy decisions that remain open.

1. What evidence should be sufficient to trust a third-party plugin discovered through the PEP 420 namespace and entry-point mechanisms, and how should that evidence be revoked?
2. How should chipcup validate SPDX identifiers against the evolving SPDX License List while preserving offline builds?
3. What provenance should a supplemental LicenseRef mapping carry when a fixture's file-scoped grant changes independently of the distribution-level License-Expression?
4. Which release-history source is authoritative when source tags, package-index versions, and signed attestations disagree?
5. Which supported platforms and optional extras are required marker rows for each deprecated public name, and how are native CI observations retained and linked to a release?
6. How should dynamic PEP 517 version metadata be admitted without allowing an sdist and wheel to describe different distributions?
7. What properties must a type-audit receipt prove, and how can its provenance be checked without treating static typing as runtime-safety evidence?
8. Which additional tests could falsify the claim that the seven boundaries still perform distinct work as Python packaging evolves?
9. Which compatibility guarantees must be stable before chipcup leaves alpha?
10. What evidence should bind a GitHub release artifact, a package-index artifact, its source tag, and any build attestation?

## Warning-window question

**Question:** If a name's `DeprecationWarning` was only ever emitted on a platform the marker matrix never selected, does its removal window begin at the version that shipped the warning or the version that first evaluated the marker?

**Current policy answer:** Neither. The release that merely shipped the warning is insufficient evidence, and evaluating a marker without executing the deprecated name is insufficient evidence. The warning clock begins only after the warning has actually been emitted on every required, selected marker row for that public name. The effective start is the latest of those first-observed releases.

If a platform row was never selected, it contributes no warning evidence. If the row is required by the compatibility policy, removal remains blocked until that platform is selected and emits the warning. If the platform is not a supported target, the maintainer must explicitly remove it from the required matrix with a documented compatibility decision; the audit must not silently treat an unselected row as successful.

This is a chipcup project policy informed by compatibility practice. PEP 387 itself is CPython's policy, not a third-party PyPI package mandate.
