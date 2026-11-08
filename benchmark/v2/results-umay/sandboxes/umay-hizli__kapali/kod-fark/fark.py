from __future__ import annotations

from difflib import SequenceMatcher


def satir_farki(a: list[str], b: list[str]) -> list[tuple[str, str]]:
    """a listesini b'ye çeviren minimal düzenleme dizisini döndürür.

    Her eleman şunlardan biridir:
      (" ", satır)  -> iki tarafta ortak
      ("-", satır)  -> a'dan silinen
      ("+", satır)  -> b'ye eklenen

    " " ve "-" sırasıyla a'yı, " " ve "+" sırasıyla b'yi verir.
    Ortak satır sayısı en fazla olur (LCS). Ardışık değişikliklerde
    silmeler eklemelerden önce gelir.
    """
    if not a:
        return [("+", x) for x in b]
    if not b:
        return [("-", x) for x in a]

    matcher = SequenceMatcher(None, a, b, autojunk=False)
    sonuc = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
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
            # replace bloğunu silme-önce-ekle sırasıyla ayır.
            for k in range(i1, i2):
                sonuc.append(("-", a[k]))
            for k in range(j1, j2):
                sonuc.append(("+", b[k]))

    return sonuc

