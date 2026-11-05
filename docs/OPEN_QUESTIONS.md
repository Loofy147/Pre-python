# Open questions

1. Should license-to-stub policy be expanded from distribution-level MIT coverage to per-path policy attestations, and what interoperable format should carry those attestations?
2. What signed provenance should bind the uploaded wheel, sdist, source commit, build backend and release tag?
3. Which platforms and extras are required for each public deprecated name, and what change-control process removes a row from that policy?
4. Should the fixture's notch geometry be represented as raw measured coordinates only, or should the reference include an uncertainty model and instrument calibration?
5. What evidence is sufficient to trust a third-party entry point discovered from a namespace package, and how is that trust revoked?
6. Should offline SPDX validation vendor a versioned SPDX License List snapshot, or should it return UNVERIFIED when the list cannot be refreshed?
7. Which additional API compatibility semantics need to be tested beyond literal `__all__` comparison, including dynamic attributes and re-exports?
8. How should prerelease and local-version policy interact with the release gate for projects that publish nightly artifacts?

## Deprecation marker question

If an API's warning was emitted on a platform that a later marker matrix no longer selects, the old observation remains evidence that the warning executed on that platform in that release. It does not automatically prove that the platform remains a required compatibility target. The project must decide whether the platform remains in its supported set; if it does, the warning observation must be retained and the removal window must satisfy the policy for that required row. If it does not, a documented matrix-policy change is required. An unselected row is never silently counted as a successful observation.
