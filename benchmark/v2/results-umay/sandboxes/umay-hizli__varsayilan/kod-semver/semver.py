from __future__ import annotations

import re

_PRE_ID = re.compile(r"(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)")

_VERSION_RE = re.compile(
    r"^v?(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-(" + _PRE_ID.pattern + r"(?:\.+" + _PRE_ID.pattern + r")*))?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


def _pre_key(pre):
    """Sıralama için güvenli ön-sürüm anahtarı (None en yüksek)."""
    if pre is None:
        return (1,)
    return (0,) + pre


def _parse_version(version: str):
    if not isinstance(version, str):
        raise ValueError(f"Geçersiz sürüm: {version!r}")

    match = _VERSION_RE.match(version.strip())
    if not match:
        raise ValueError(f"Geçersiz sürüm: {version!r}")

    major = int(match.group(1))
    minor = int(match.group(2))
    patch = int(match.group(3))
    pre_raw = match.group(4)

    if pre_raw is None:
        pre = None
    else:
        pre = []
        for ident in pre_raw.split("."):
            if ident.isdigit():
                pre.append((0, int(ident)))
            else:
                pre.append((1, ident))
        pre = tuple(pre)

    return (major, minor, patch, pre)


def _compare_pre(pre_a, pre_b) -> int:
    if pre_a is None and pre_b is None:
        return 0
    if pre_a is None:
        return 1
    if pre_b is None:
        return -1

    for ident_a, ident_b in zip(pre_a, pre_b):
        if ident_a < ident_b:
            return -1
        if ident_a > ident_b:
            return 1

    if len(pre_a) < len(pre_b):
        return -1
    if len(pre_a) > len(pre_b):
        return 1
    return 0


def compare(a: str, b: str) -> int:
    major_a, minor_a, patch_a, pre_a = _parse_version(a)
    major_b, minor_b, patch_b, pre_b = _parse_version(b)

    if (major_a, minor_a, patch_a) != (major_b, minor_b, patch_b):
        if (major_a, minor_a, patch_a) < (major_b, minor_b, patch_b):
            return -1
        return 1

    return _compare_pre(pre_a, pre_b)


def sort_versions(versions: list[str]) -> list[str]:
    if not isinstance(versions, list):
        raise ValueError("versions bir liste olmalıdır")

    parsed = []
    for item in versions:
        major, minor, patch, pre = _parse_version(item)
        parsed.append(((major, minor, patch, _pre_key(pre)), item))

    parsed.sort(key=lambda x: x[0])
    return [item for _, item in parsed]
