"""Semantic Versioning 2.0.0 karsilastirma ve siralama.

Kurallar: https://semver.org
Yalnızca standart kitaplik kullanilir (re, functools).
"""

from __future__ import annotations

import re
from functools import cmp_to_key
from typing import List, Optional, Tuple

# MAJOR.MINOR.PATCH: her bolum "0" veya bastaki sifira bagli olmayan pozitif tamsayidir.
# Istege bagli on surum (-ident.ident) ve derleme metadata (+ident.ident).
# Basta tek kucuk harfli "v" olabilir ("V" degil).
_VERSION_RE = re.compile(
    r"^(v)?"
    r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:\-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)


class _Version:
    """Ayrilmis SemVer parcalarini tutan ic sinif."""

    __slots__ = ("major", "minor", "patch", "pre", "build", "raw")

    def __init__(
        self,
        major: int,
        minor: int,
        patch: int,
        pre: Optional[Tuple[str, ...]],
        build: Optional[str],
        raw: str,
    ) -> None:
        self.major = major
        self.minor = minor
        self.patch = patch
        self.pre = pre  # None -> on surum yok; tuple -> kimlikler
        self.build = build  # onceligi etkilemez
        self.raw = raw


def parse(version: str) -> _Version:
    """SemVer metnini ayristir; gecersizse ValueError firlatir."""
    if not isinstance(version, str):
        raise ValueError(f"Gecersiz surum: {version!r}")

    m = _VERSION_RE.match(version)
    if m is None:
        raise ValueError(f"Gecersiz surum: {version!r}")

    major = int(m.group(2))
    minor = int(m.group(3))
    patch = int(m.group(4))

    pre_raw = m.group(5)
    pre: Optional[Tuple[str, ...]] = None
    if pre_raw is not None:
        pre = tuple(pre_raw.split("."))

    build = m.group(6)  # onceligi etkilemez

    return _Version(major, minor, patch, pre, build, version)


def _compare_pre(
    a: Optional[Tuple[str, ...]], b: Optional[Tuple[str, ...]]
) -> int:
    """On surum kimliklerini karsilastir.

    Yokluk > herhangi bir on surum.
    Sayisal kimlik < alfanumerik kimlik.
    Sayisal sayisal olarak, alfanumerik lexikografik (ASCII) karsilastirilir.
    Kisa on surum listesi, uzununun on ekiyse daha kucuktur.
    """
    if a is None and b is None:
        return 0
    if a is None:
        return 1  # on surum yok = oncelikli (buyuk)
    if b is None:
        return -1

    for x, y in zip(a, b):
        x_num = x.isdigit()
        y_num = y.isdigit()
        if x_num and y_num:
            ix, iy = int(x), int(y)
            if ix != iy:
                return -1 if ix < iy else 1
        elif x_num and not y_num:
            return -1  # sayisal < alfanumerik
        elif not x_num and y_num:
            return 1  # alfanumerik > sayisal
        else:
            if x != y:
                return -1 if x < y else 1

    if len(a) != len(b):
        return -1 if len(a) < len(b) else 1
    return 0


def compare(a: str, b: str) -> int:
    """a < b ise -1, esit ise 0, a > b ise 1 dondurur.

    Derleme bilgisi (+build) onceligi etkilemez.
    Gecersiz surum metninde ValueError firlatilir.
    """
    va = parse(a)
    vb = parse(b)

    for x, y in ((va.major, vb.major), (va.minor, vb.minor), (va.patch, vb.patch)):
        if x != y:
            return -1 if x < y else 1

    return _compare_pre(va.pre, vb.pre)


def sort_versions(versions: List[str]) -> List[str]:
    """Oncelige gore artan sirali yeni liste dondurur.

    Esit oncelikli surumler girdideki siralarini korur (stabil siralama).
    Gecersiz surum metninde ValueError firlatilir.
    """
    # Tum girisleri once dogrula (bir hata varsa hepsi icin ValueError)
    for v in versions:
        parse(v)

    return sorted(versions, key=cmp_to_key(compare))


if __name__ == "__main__":
    # Hizli manuel deneme
    tests = [
        ("1.0.0", "2.0.0", -1),
        ("2.0.0", "1.0.0", 1),
        ("1.0.0", "1.0.0", 0),
        ("1.0.0-alpha", "1.0.0", -1),
        ("1.0.0", "1.0.0-alpha", 1),
        ("1.0.0-alpha.1", "1.0.0-alpha.2", -1),
        ("1.0.0-alpha.1", "1.0.0-alpha.11", -1),
        ("1.0.0-alpha.1", "1.0.0-alpha.beta", -1),
        ("1.0.0-alpha.beta", "1.0.0-alpha.1", 1),
        ("1.0.0-rc.1+build.1", "1.0.0-rc.1+build.2", 0),
        ("v1.2.3", "1.2.3", 0),
        ("1.0.0-x", "1.0.0-x", 0),
        ("1.0.0-x.7", "1.0.0-x.8-beta", -1),
        ("1.0.0-y", "1.0.0-x", 1),
    ]
    for x, y, expected in tests:
        got = compare(x, y)
        assert got == expected, f"compare({x!r}, {y!r}) = {got}, bekleneni {expected}"

    data = ["1.0.0", "2.0.0", "1.0.0-alpha", "1.0.0-alpha.1", "1.0.0+build", "v1.0.0"]
    assert sort_versions(data) == [
        "1.0.0-alpha",
        "1.0.0-alpha.1",
        "1.0.0",
        "1.0.0+build",
        "v1.0.0",
        "2.0.0",
    ]

    # Cok basamakli sayisal on-surum kimlikleri (string karsilastirma hatasi kontrolu)
    assert sort_versions(["1.0.0-alpha.10", "1.0.0-alpha.2", "1.0.0-alpha.1"]) == [
        "1.0.0-alpha.1",
        "1.0.0-alpha.2",
        "1.0.0-alpha.10",
    ]

    # Gecersiz girisler
    for bad in ["1.0", "01.0.0", "1.0.0-", "1.0.0.0", "v1.2.3-extra+ok ok", "1.0.0+build ok"]:
        try:
            compare(bad, "1.0.0")
            raise AssertionError(f"ValueError bekleniyordu: {bad!r}")
        except ValueError:
            pass
        try:
            sort_versions([bad])
            raise AssertionError(f"ValueError bekleniyordu: {bad!r}")
        except ValueError:
            pass

    print("tum manuel testler gecti")
