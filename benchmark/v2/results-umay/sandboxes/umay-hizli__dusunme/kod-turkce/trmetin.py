# -*- coding: utf-8 -*-
"""Türkçe metin işleme yardımcıları (sadece standart kitaplık)."""

_TURKISH_ORDER = "0123456789abcçdefgğhıijklmnoöpqrsştuüvwxyz"
_TURKISH_RANK = {ch: idx for idx, ch in enumerate(_TURKISH_ORDER)}

def tr_lower(s: str) -> str:
    """s'i Türkçe kurallara göre küçük harfe çevirir (I->ı, İ->i)."""
    out = []
    for ch in s:
        if ch == "I":
            out.append("ı")
        elif ch == "İ":
            out.append("i")
        else:
            out.append(ch.lower())
    return "".join(out)

def tr_upper(s: str) -> str:
    """s'i Türkçe kurallara göre büyük harfe çevirir (i->İ, ı->I)."""
    out = []
    for ch in s:
        if ch == "i":
            out.append("İ")
        elif ch == "ı":
            out.append("I")
        else:
            out.append(ch.upper())
    return "".join(out)

def _sort_key(word: str):
    lowered = tr_lower(word)
    key = []
    for ch in lowered:
        rank = _TURKISH_RANK.get(ch)
        if rank is None:
            key.append((0, ord(ch)))
        else:
            key.append((1, rank))
    return key

def tr_sorted(words: list[str]) -> list[str]:
    """Kelimeleri Türk alfabesine göre sıralar; orijinal listeyi değiştirmez."""
    return sorted(words, key=_sort_key)
