# -*- coding: utf-8 -*-
"""Türkçe metin işleme fonksiyonları."""

_TURKISH_ALPHABET = "0123456789abcçdefgğhıijklmnoöpqrsştuüvwxyz"
_CHAR_ORDER = {ch: i for i, ch in enumerate(_TURKISH_ALPHABET)}
_TR_LOWER_MAP = {'I': 'ı', 'İ': 'i'}
_TR_UPPER_MAP = {'ı': 'I', 'i': 'İ'}

def tr_lower(s: str) -> str:
    if not s:
        return s
    result = []
    for ch in s:
        if ch in _TR_LOWER_MAP:
            result.append(_TR_LOWER_MAP[ch])
        else:
            result.append(ch.lower())
    return ''.join(result)

def tr_upper(s: str) -> str:
    if not s:
        return s
    result = []
    for ch in s:
        if ch in _TR_UPPER_MAP:
            result.append(_TR_UPPER_MAP[ch])
        else:
            result.append(ch.upper())
    return ''.join(result)

def _tr_sort_key(word: str):
    lower_word = tr_lower(word)
    char_keys = []
    for ch in lower_word:
        if ch in _CHAR_ORDER:
            char_keys.append((1, _CHAR_ORDER[ch]))
        else:
            char_keys.append((0, ord(ch)))
    # word KALDIRILDI - Python sorted() stabil olduğu için eşit anahtarlarda girdi sırası korunur
    return (tuple(char_keys), len(lower_word))

def tr_sorted(words: list[str]) -> list[str]:
    if not words:
        return []
    return sorted(words, key=_tr_sort_key)

if __name__ == "__main__":
    print("tr_lower:", tr_lower('İSTANBUL'), tr_lower('IŞIK'))
    print("tr_upper:", tr_upper('istanbul'), tr_upper('ışık'))
    print("tr_sorted:", tr_sorted(["elma", "armut", "çilek", "üzüm", "İncir", "ıspanak"]))