"""Minimal düzenleme dizisi üreten yardımcı modül.

Ana arayüz:
    satir_farki(a: list[str], b: list[str]) -> list[tuple[str, str]]
"""

from __future__ import annotations

import difflib
from typing import List, Tuple


def satir_farki(a: list[str], b: list[str]) -> list[tuple[str, str]]:
    """``a`` listesini ``b`` listesine çeviren minimal düzenleme dizisi.

    Her eleman:
      - (" ", satir): a ve b'de ortak satır
      - ("-", satir): sadece a'daki silinen satır
      - ("+", satir): sadece b'deki eklenen satır

    Kısıtlamalar:
      - " " ve "-" elemanları sırayla ``a``'yı verir.
      - " " ve "+" elemanları sırayla ``b``'yi verir.
      - Ortak satır sayısı maksimum olur (en uzun ortak alt dizi).
      - Ardışık bir ekleme sonrasına silme gelmez: "+" ardından "-" olmaz.
    """

    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    sonuc: list[tuple[str, str]] = []

    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i1, i2):
                sonuc.append((" ", a[k]))
        elif tag == "delete":
            for k in range(i1, i2):
                sonuc.append(("-", a[k]))
        elif tag == "insert":
            for k in range(j1, j2):
                sonuc.append(("+", b[k]))
        elif tag == "replace":
            # Kural: "+" elemanının hemen ardından "-" gelmemeli.
            # Bu yüzden önce tüm silmeler, sonra tüm eklemeler eklenir.
            for k in range(i1, i2):
                sonuc.append(("-", a[k]))
            for k in range(j1, j2):
                sonuc.append(("+", b[k]))

    return sonuc
"""
"""