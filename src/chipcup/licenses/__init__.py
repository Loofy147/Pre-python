"""PEP 639 License-Expression, License-File and custom LicenseRef checks."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from chipcup.deprecations import (
    DeprecationSchedule,
    validate_license_dependencies,
)

__all__ = [
    "DEFAULT_LICENSE_REFS",
    "LicenseAuditResult",
    "LicenseNode",
    "check_artifact_license_coverage",
    "check_license_files",
    "license_references",
    "parse_license_expression",
    "validate_compatibility",
]

_TOKEN = re.compile(
    r"\s*(\(|\)|AND\b|OR\b|WITH\b|[A-Za-z0-9][A-Za-z0-9.+:-]*)",
    re.IGNORECASE,
)
_LICENSE_REF_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.-]*$")

DEFAULT_LICENSE_REFS: Mapping[str, str] = {
    "LicenseRef-Fixture-Dual": "LICENSES/Fixture-Dual.txt",
}


@dataclass(frozen=True, slots=True)
class LicenseNode:
    kind: str
    value: str | None = None
    children: tuple["LicenseNode", ...] = ()


@dataclass(frozen=True, slots=True)
class LicenseAuditResult:
    expression: str
    references: tuple[str, ...]
    declared_files: tuple[str, ...]
    missing_source_files: tuple[str, ...]
    missing_artifact_files: Mapping[str, tuple[str, ...]]
    dependency_issues: tuple[str, ...]
    issues: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.issues


def _tokens(expression: str) -> list[str]:
    result: list[str] = []
    position = 0
    while position < len(expression):
        if not expression[position:].strip():
            break
        match = _TOKEN.match(expression, position)
        if match is None:
            raise ValueError(f"invalid SPDX expression near {expression[position:]!r}")
        token = match.group(1)
        if token.startswith("LicenseRef-") and not _LICENSE_REF_ID.fullmatch(token[len("LicenseRef-"):]):
            raise ValueError(f"invalid SPDX LicenseRef identifier {token!r}")
        result.append(token)
        position = match.end()
    if not result:
        raise ValueError("SPDX expression cannot be empty")
    return result


def parse_license_expression(expression: str) -> LicenseNode:
    """Parse SPDX AND/OR/WITH grammar; identifier-list validation is separate."""
    tokens = _tokens(expression)
    index = 0

    def peek() -> str | None:
        return tokens[index] if index < len(tokens) else None

    def take() -> str:
        nonlocal index
        if index >= len(tokens):
            raise ValueError("unexpected end of SPDX expression")
        token = tokens[index]
        index += 1
        return token

    def atom() -> LicenseNode:
        token = take()
        if token == "(":
            node = parse_or()
            if take() != ")":
                raise ValueError("missing closing parenthesis")
            return node
        if token.upper() in {"AND", "OR", "WITH", ")"}:
            raise ValueError(f"expected license identifier, got {token!r}")
        return LicenseNode("id", token)

    def with_expression() -> LicenseNode:
        left = atom()
        if peek() is not None and peek().upper() == "WITH":
            take()
            right = atom()
            if left.kind != "id" or right.kind != "id":
                raise ValueError("SPDX WITH must join a license identifier and exception")
            return LicenseNode("with", children=(left, right))
        return left

    def parse_and() -> LicenseNode:
        children = [with_expression()]
        while peek() is not None and peek().upper() == "AND":
            take()
            children.append(with_expression())
        return children[0] if len(children) == 1 else LicenseNode("and", children=tuple(children))

    def parse_or() -> LicenseNode:
        children = [parse_and()]
        while peek() is not None and peek().upper() == "OR":
            take()
            children.append(parse_and())
        return children[0] if len(children) == 1 else LicenseNode("or", children=tuple(children))

    result = parse_or()
    if index != len(tokens):
        raise ValueError(f"unexpected token {tokens[index]!r}")
    return result


def license_references(node: LicenseNode) -> tuple[str, ...]:
    found: list[str] = []
    if node.kind == "id" and node.value and node.value.startswith("LicenseRef-"):
        found.append(node.value)
    for child in node.children:
        found.extend(license_references(child))
    return tuple(sorted(set(found)))


def _covered(member: str, requested: str) -> bool:
    normalized = member.replace("\\", "/").lstrip("./")
    target = requested.replace("\\", "/").lstrip("./")
    basename = Path(target).name
    return (
        normalized == target
        or normalized.endswith("/" + target)
        or normalized.endswith(".dist-info/licenses/" + basename)
    )


def check_artifact_license_coverage(
    members: Iterable[str], license_files: Iterable[str]
) -> tuple[str, ...]:
    paths = tuple(members)
    return tuple(
        filename for filename in license_files
        if not any(_covered(member, filename) for member in paths)
    )


def check_license_files(
    root: str | Path, license_files: Iterable[str]
) -> tuple[str, ...]:
    base = Path(root).resolve()
    missing: list[str] = []
    for filename in license_files:
        candidate = (base / filename).resolve()
        if (
            base not in candidate.parents
            or not candidate.is_file()
            or candidate.stat().st_size == 0
        ):
            missing.append(filename)
    return tuple(missing)


def validate_compatibility(
    expression: str,
    artifacts: Mapping[str, Iterable[str]],
    license_files: Sequence[str],
    *,
    root: str | Path,
    license_refs: Mapping[str, str] | None = None,
    deprecations: Sequence[DeprecationSchedule] = (),
) -> LicenseAuditResult:
    """Validate SPDX syntax, LicenseRef mapping and file coverage per artifact."""
    tree = parse_license_expression(expression)
    expression_refs = license_references(tree)
    reference_map = dict(DEFAULT_LICENSE_REFS if license_refs is None else license_refs)
    # Supplemental refs describe file-scoped grants that PEP 639's single
    # distribution-level License-Expression cannot scope to individual files.
    refs = tuple(sorted(set(expression_refs) | set(reference_map)))
    issues: list[str] = []

    unresolved = tuple(reference for reference in expression_refs if reference not in reference_map)
    if unresolved:
        issues.append(f"unmapped SPDX LicenseRef identifiers: {', '.join(unresolved)}")

    declared = tuple(dict.fromkeys(license_files))
    for reference in refs:
        mapped_path = reference_map.get(reference)
        if mapped_path is not None and mapped_path not in declared:
            issues.append(
                f"{reference} maps to {mapped_path}, which is not declared as License-File"
            )

    required_files = tuple(
        dict.fromkeys((*declared, *(reference_map[item] for item in refs if item in reference_map)))
    )
    missing_source = check_license_files(root, required_files)
    missing_artifacts: dict[str, tuple[str, ...]] = {}
    for artifact_name, members in artifacts.items():
        missing = check_artifact_license_coverage(members, required_files)
        if missing:
            missing_artifacts[artifact_name] = missing
            issues.append(
                f"{artifact_name} is missing License-File coverage: {', '.join(missing)}"
            )
    if missing_source:
        issues.append(
            f"source tree is missing license text files: {', '.join(missing_source)}"
        )

    dependency_issues = validate_license_dependencies(
        deprecations, reference_map, declared
    )
    issues.extend(dependency_issues)
    return LicenseAuditResult(
        expression=expression,
        references=refs,
        declared_files=declared,
        missing_source_files=missing_source,
        missing_artifact_files=missing_artifacts,
        dependency_issues=dependency_issues,
        issues=tuple(issues),
    )
