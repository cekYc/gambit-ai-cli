"""Semantic Versioning 2.0.0 kiyaslama ve sirala ma.

Yalnca standart kitaplik kullanilir.
"""

from __future__ import annotations

import re
from functools import cmp_to_key

_VERSION_RE = re.compile(
    r"^v?(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"
    r"(?:-(?P<pre>[^+]*))?"
    r"(?:\+(?P<build>.+))?$"
)

_IDENT_RE = re.compile(r"[A-Za-z0-9-]+")


def _split_identifiers(part):
    """Nokta ile ayrilmis tanimlayici listesini dondurur; yoksa None."""
    if part is None:
        return None
    ids = part.split(".")
    for ident in ids:
        if ident == "":
            raise ValueError(f"Bos surum tanimlayicisi: {part!r}")
        if not _IDENT_RE.fullmatch(ident):
            raise ValueError(f"Gecersiz surum tanimlayicisi: {ident!r}")
    return ids


def _parse(version):
    if not isinstance(version, str):
        raise ValueError(f"Surum metni olmalidir: {version!r}")
    m = _VERSION_RE.fullmatch(version)
    if m is None:
        raise ValueError(f"Gecersiz surum: {version!r}")

    major = int(m.group("major"))
    minor = int(m.group("minor"))
    patch = int(m.group("patch"))

    for val in (m.group("major"), m.group("minor"), m.group("patch")):
        if len(val) > 1 and val[0] == "0":
            raise ValueError(f"Bastaki sifirli sayi: {version!r}")

    pre = _split_identifiers(m.group("pre"))
    if pre is not None:
        for ident in pre:
            if ident.isdigit() and len(ident) > 1 and ident[0] == "0":
                raise ValueError(f"Bastaki sifirli on surum tanimlayicisi: {version!r}")

    _split_identifiers(m.group("build"))

    return (major, minor, patch, pre)


def _cmp_pre(a, b):
    if a is None and b is None:
        return 0
    if a is None:
        return 1
    if b is None:
        return -1
    for x, y in zip(a, b):
        x_digit = x.isdigit()
        y_digit = y.isdigit()
        if x_digit and y_digit:
            xi = int(x)
            yi = int(y)
            if xi < yi:
                return -1
            if xi > yi:
                return 1
        elif x_digit != y_digit:
            return -1 if x_digit else 1
        else:
            if x < y:
                return -1
            if x > y:
                return 1
    if len(a) < len(b):
        return -1
    if len(a) > len(b):
        return 1
    return 0


def compare(a: str, b: str) -> int:
    pa = _parse(a)
    pb = _parse(b)
    for xa, xb in zip(pa[:3], pb[:3]):
        if xa < xb:
            return -1
        if xa > xb:
            return 1
    return _cmp_pre(pa[3], pb[3])


def sort_versions(versions: list[str]) -> list[str]:
    return sorted(versions, key=cmp_to_key(compare))
