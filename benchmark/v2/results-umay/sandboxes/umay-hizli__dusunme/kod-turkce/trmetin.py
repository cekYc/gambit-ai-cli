from __future__ import annotations

"""Türkçe metin işleme yardımcı fonksiyonları (sadece standart kütüphane)."""

_TURKISH_ORDER = "0123456789abcçdefgğhıijklmnoöpqrsştuüvwxyz"
_TURKISH_INDEX = {ch: idx for idx, ch in enumerate(_TURKISH_ORDER)}


def tr_lower(s: str) -> str:
    """s'yi Türkçe kurallarla küçük harfe çevirir (I -> ı, İ -> i)."""
    result = []
    for ch in s:
        if ch == 'I':
            result.append('ı')
        elif ch == 'İ':
            result.append('i')
        else:
            result.append(ch.lower())
    return ''.join(result)


def tr_upper(s: str) -> str:
    """s'yi Türkçe kurallarla büyük harfe çevirir (i -> İ, ı -> I)."""
    result = []
    for ch in s:
        if ch == 'i':
            result.append('İ')
        elif ch == 'ı':
            result.append('I')
        else:
            result.append(ch.upper())
    return ''.join(result)


def _sort_key(word: str):
    lowered = tr_lower(word)
    key = []
    for ch in lowered:
        if ch in _TURKISH_INDEX:
            key.append((1, _TURKISH_INDEX[ch]))
        else:
            # Alfabe dışındaki karakterler (boşluk, noktalama vb.)
            # tüm alfabedeki karakterlerden önce gelir ve kendi aralarında
            # Unicode kod noktasına göre sıralanır.
            key.append((0, ord(ch)))
    return key


def tr_sorted(words: list[str]) -> list[str]:
    """Kelimeleri Türk alfabesine göre (büyük/küçük harf farkı görmezden
    gelinerek, Türkçe kurallarla küçültülerek) sıralanmış yeni bir liste
    döndürür. Girdi listesi değiştirilmez.

    Sıralama kuralı:
      - Alfabe: 0123456789abcçdefgğhıijklmnoöpqrsştuüvwxyz
      - Alfabe dışı karakterler önce, kendi aralarında Unicode kod noktasıyla
      - Önek olan kısa kelime önce gelir
      - Eşit anahtarlar girdisindeki sıralamayı korur (stabil)
    """
    return sorted(words, key=_sort_key)
