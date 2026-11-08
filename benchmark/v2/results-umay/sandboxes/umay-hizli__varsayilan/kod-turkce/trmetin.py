from __future__ import annotations

_TURKISH_ORDER = "0123456789abcçdefgğhıijklmnoöpqrsştuüvwxyz"
_CHAR_INDEX = {ch: i for i, ch in enumerate(_TURKISH_ORDER)}


def tr_lower(s: str) -> str:
    """s'i Türkçe kurallarla küçük harfe çevirir (I->ı, İ->i)."""
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
    """s'i Türkçe kurallarla büyük harfe çevirir (i->İ, ı->I)."""
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
        if ch in _CHAR_INDEX:
            key.append((1, _CHAR_INDEX[ch]))
        else:
            # Alfabede olmayan karakterler (boşluk, noktalama vb.)
            # listedeki tüm karakterlerden önce gelir; kendi aralarında
            # Unicode kod noktasına göre sıralanır.
            key.append((0, ord(ch)))
    return tuple(key)


def tr_sorted(words: list[str]) -> list[str]:
    """Kelimeleri Türk alfabesine göre, büyük/küçük harf farkı
    gözetmeksizin sıralanmış yeni bir liste döndürür.

    Girdi listesi değiştirilmez. Alfabede olmayan karakterler listedeki
    tüm karakterlerden önce gelir ve kendi aralarında Unicode kod
    noktasına göre sıralanır. Önek kısayı önce gelir; eşit sayılan
    kelimeler girdisindeki sıralarını korur (kararlı sıralama).
    """
    return sorted(words, key=_sort_key)


__all__ = ["tr_lower", "tr_upper", "tr_sorted"]
