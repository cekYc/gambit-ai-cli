"""Semantic Versioning 2.0.0 uyumlu karşılaştırma ve sıralama işlemleri.

Yalnızca Python standart kütüphanesini kullanır.
"""

from __future__ import annotations

import re
from typing import List, Tuple


# Geçerli bir sürüm metninin detaylı yakalanması.
# Kalıp parçaları:
#   ^v?           - isteğe bağlı tek 'v' öneki
#   (?P<major>...) - MAJOR (0 veya sıfır ile başlamayan pozitif tamsayı)
#   \.(?P<minor>...) - MINOR
#   \.(?P<patch>...) - PATCH
#   (?:-(?P<prerelease>...))?   - isteğe bağlı ön sürüm
#   (?:\+(?P<build>...))?      - isteğe bağlı derleme bilgisi
#   $
_VERSION_RE = re.compile(
    r"^v?"
    r"(?P<major>0|[1-9]\d*)"
    r"\.(?P<minor>0|[1-9]\d*)"
    r"\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+(?P<build>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"$"
)


def _split_prerelease_identifiers(prerelease: str) -> List[Tuple[bool, int | str]]:
    """Ön sürüm kimliklerini SemVer 2.0.0 karşılaştırma kurallarıyla ayırır.

    Her kimlik:
      - sadece rakamlarsa sayı olarak (sayısal kimlik)
      - aksi halde karakter dizisi olarak (alfanümerik kimlik)

    Döndürdüğü listedeki her eleman (is_numeric, value) ikilisidir.
    """
    result: List[Tuple[bool, int | str]] = []
    for ident in prerelease.split("."):
        if ident.isdigit():
            result.append((True, int(ident)))
        else:
            result.append((False, ident))
    return result


def _compare_prerelease(a: str | None, b: str | None) -> int:
    """İki ön sürüm dizisini karşılaştırır.

    None (yok) her zaman var olanımdan büyük kabul edilir (1.0.0 > 1.0.0-alpha).
    """
    if a is None and b is None:
        return 0
    if a is None:
        return 1
    if b is None:
        return -1

    a_idents = _split_prerelease_identifiers(a)
    b_idents = _split_prerelease_identifiers(b)

    for a_ident, b_ident in zip(a_idents, b_idents):
        if a_ident == b_ident:
            continue

        a_is_num, a_val = a_ident
        b_is_num, b_val = b_ident

        if a_is_num and b_is_num:
            if a_val < b_val:
                return -1
            if a_val > b_val:
                return 1
        elif a_is_num and not b_is_num:
            # Sayısal kimlikler alfanümerik kimliklerden daha düşüktür.
            return -1
        elif not a_is_num and b_is_num:
            return 1
        else:
            if a_val < b_val:
                return -1
            if a_val > b_val:
                return 1

    # Tüm ortak kimlikler eşitse, daha uzun olan daha büyük kabul edilir.
    if len(a_idents) < len(b_idents):
        return -1
    if len(a_idents) > len(b_idents):
        return 1
    return 0


class _Version:
    """Ayrıştırılmış ve doğrulanmış bir SemVer 2.0.0 sürümü."""

    __slots__ = ("major", "minor", "patch", "prerelease", "build", "raw")

    def __init__(self, raw: str) -> None:
        if not isinstance(raw, str):
            raise ValueError(f"Geçersiz sürüm metni: {raw!r}")

        match = _VERSION_RE.fullmatch(raw)
        if match is None:
            raise ValueError(f"Geçersiz sürüm metni: {raw!r}")

        self.major = int(match.group("major"))
        self.minor = int(match.group("minor"))
        self.patch = int(match.group("patch"))
        self.prerelease: str | None = match.group("prerelease")
        self.build: str | None = match.group("build")
        self.raw = raw

    def core_key(self) -> Tuple[int, int, int]:
        return (self.major, self.minor, self.patch)

    def precedence_key(self) -> tuple:
        """Sıralama için güvenli ve doğru öncelik anahtarı döndürür.

        Derleme bilgisi yok sayılır. Ön sürüm yoksa (None), boş olmayan
        her ön sürümden önce kabul edilir (1.0.0 < 1.0.0-alpha).
        """
        if self.prerelease is None:
            pre_key = (0, [])
        else:
            pre_key = (1, _split_prerelease_identifiers(self.prerelease))
        return (self.major, self.minor, self.patch, pre_key)

    def __lt__(self, other: "_Version") -> bool:
        if not isinstance(other, _Version):
            return NotImplemented
        return self.precedence_key() < other.precedence_key()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _Version):
            return NotImplemented
        return self.precedence_key() == other.precedence_key()



def parse(version: str) -> _Version:
    """Bir sürüm metnini ayrıştırır ve doğrular.

    Geçersiz bir metin için ValueError fırlatır.
    """
    return _Version(version)


def compare(a: str, b: str) -> int:
    """İki SemVer 2.0.0 sürümünü karşılaştırır.

    a < b ise -1, öncelik eşitse 0, a > b ise 1 döndürür.
    Derleme bilgisi önceliği etkilemez. Geçersiz metinler ValueError fırlatır.
    """
    va = parse(a)
    vb = parse(b)

    if va < vb:
        return -1
    if va == vb:
        return 0
    return 1


def sort_versions(versions: list[str]) -> list[str]:
    """Sürümleri önceliğe göre artan sıralar.

    Yeni bir liste döndürür. Eşit öncelikli sürümler girdideki sıralarını korur
    (stabil sıralama). Geçersiz metinler ValueError fırlatır.
    """
    parsed = [parse(v) for v in versions]
    parsed.sort(key=lambda v: v.precedence_key())
    return [v.raw for v in parsed]
