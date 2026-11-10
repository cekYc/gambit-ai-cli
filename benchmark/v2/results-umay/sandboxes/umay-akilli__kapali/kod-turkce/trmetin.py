# -*- coding: utf-8 -*-
"""
Türkçe metin işlemleri için yardımcı fonksiyonlar.
"""

# Türkçe alfabesi sırası (küçük harfler)
_TR_ALPHABET = "0123456789abcçdefgğhıijklmnoöpqrsştuüvwxyz"
_TR_CHAR_ORDER = {ch: i for i, ch in enumerate(_TR_ALPHABET)}

# Türkçe özel büyük/küçük harf eşlemeleri
_TR_UPPER_MAP = {
    'i': 'İ',
    'ı': 'I',
}
_TR_LOWER_MAP = {
    'İ': 'i',
    'I': 'ı',
}


def tr_lower(s: str) -> str:
    """Türkçe kurallarıyla küçük harfe çevirir."""
    result = []
    for ch in s:
        if ch in _TR_LOWER_MAP:
            result.append(_TR_LOWER_MAP[ch])
        elif 'A' <= ch <= 'Z':
            # Standart ASCII büyük harfler
            result.append(chr(ord(ch) + 32))
        else:
            result.append(ch)
    return ''.join(result)


def tr_upper(s: str) -> str:
    """Türkçe kurallarıyla büyük harfe çevirir."""
    result = []
    for ch in s:
        if ch in _TR_UPPER_MAP:
            result.append(_TR_UPPER_MAP[ch])
        elif 'a' <= ch <= 'z':
            # Standart ASCII küçük harfler
            result.append(chr(ord(ch) - 32))
        else:
            result.append(ch)
    return ''.join(result)


def _tr_sort_key(word: str):
    """Türkçe sıralama için sort key üretir."""
    lower_word = tr_lower(word)
    key_parts = []
    for ch in lower_word:
        if ch in _TR_CHAR_ORDER:
            # Alfabedeki karakterler: (0, sıralama indeksi)
            key_parts.append((0, _TR_CHAR_ORDER[ch]))
        else:
            # Alfabede olmayan karakterler: (1, unicode kod noktası)
            # Kendi aralarında Unicode sırasına göre sıralanır
            key_parts.append((1, ord(ch)))
    return tuple(key_parts)


def tr_sorted(words: list[str]) -> list[str]:
    """Kelimeleri Türk alfabesine göre sıralanmış yeni liste döndürür.
    
    - Büyük/küçük harf farkı gözetmez (Türkçe kurallarla küçültür).
    - Karakter sırası: 0123456789abcçdefgğhıijklmnoöpqrsştuüvwxyz
    - Bu listede olmayan karakterler (boşluk, noktalama vb.) listedeki
      tüm karakterlerden önce gelir ve kendi aralarında Unicode kod
      noktasına göre sıralanır.
    - Bir kelime diğerinin önekiyse kısa olan önce gelir.
    - Eşit sayılan kelimeler girdideki sıralarını korur (stable sort).
    """
    # Python's sort is stable, so equal elements keep their original order
    return sorted(words, key=_tr_sort_key)
