"""PEP 639 file coverage and a small SPDX expression grammar parser."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

_TOKEN = re.compile(
    r"\s*(\(|\)|AND\b|OR\b|WITH\b|[A-Za-z0-9][A-Za-z0-9.+:-]*)",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class LicenseNode:
    kind: str
    value: str | None = None
    children: tuple["LicenseNode", ...] = ()


def _tokens(expression: str) -> list[str]:
    result: list[str] = []
    position = 0
    while position < len(expression):
        if not expression[position:].strip():
            break
        match = _TOKEN.match(expression, position)
        if match is None:
            raise ValueError(f"invalid SPDX expression near {expression[position:]!r}")
        result.append(match.group(1))
        position = match.end()
    if not result:
        raise ValueError("SPDX expression cannot be empty")
    return result


def parse_license_expression(expression: str) -> LicenseNode:
    """Parse SPDX AND/OR/WITH grouping; identifier-list validation is separate."""
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


def check_license_files(root: str | Path, license_files: Iterable[str]) -> tuple[str, ...]:
    base = Path(root).resolve()
    missing: list[str] = []
    for filename in license_files:
        candidate = (base / filename).resolve()
        if base not in candidate.parents or not candidate.is_file() or candidate.stat().st_size == 0:
            missing.append(filename)
    return tuple(missing)


def validate_compatibility(
    expression: str,
    artifacts: Mapping[str, Iterable[str]],
    license_files: Sequence[str],
    *,
    root: str | Path,
    license_refs: Mapping[str, str] | None = None,
    deprecations: Sequence[object] = (),
    published_releases: Sequence[str] = (),
) -> LicenseNode:
    """Validate syntax, LicenseRef mapping, artifact coverage and shim schedules."""
    tree = parse_license_expression(expression)
    refs = license_references(tree)
    reference_map = dict(license_refs or {})
    unmapped = [reference for reference in refs if reference not in reference_map]
    if unmapped:
        raise ValueError(f"unmapped SPDX LicenseRef identifiers: {', '.join(unmapped)}")
    required = tuple(dict.fromkeys((*license_files, *reference_map.values())))
    missing_on_disk = check_license_files(root, required)
    if missing_on_disk:
        raise ValueError(f"license files missing from source tree: {', '.join(missing_on_disk)}")
    for artifact_name, members in artifacts.items():
        missing = check_artifact_license_coverage(members, required)
        if missing:
            raise ValueError(f"{artifact_name} is missing license files: {', '.join(missing)}")
    from chipcup.deprecations import validate_schedules

    validate_schedules(deprecations, published_releases)
    return tree
