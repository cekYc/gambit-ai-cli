"""
Türkçe metin işleme fonksiyonları.
"""

# Türkçe alfabesi sıralaması için karakter öncelik haritası
# 0-9, a-z, ç, ğ, ı, ö, ş, ü
_TR_ALPHABET = "0123456789abcçdefgğhıijklmnoöpqrsştuüvwxyz"
_TR_CHAR_ORDER = {ch: i for i, ch in enumerate(_TR_ALPHABET)}

# Türkçe özel büyük/küçük harf eşleşmeleri
_TR_UPPER_MAP = {
    'i': 'İ',
    'ı': 'I',
    'ç': 'Ç',
    'ğ': 'Ğ',
    'ö': 'Ö',
    'ş': 'Ş',
    'ü': 'Ü',
}
_TR_LOWER_MAP = {v: k for k, v in _TR_UPPER_MAP.items()}
_TR_LOWER_MAP['I'] = 'ı'
_TR_LOWER_MAP['İ'] = 'i'


def tr_lower(s: str) -> str:
    """Türkçe kurallarıyla string'i küçük harfe çevirir.
    I -> ı, İ -> i, diğerleri normal lower().
    """
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
    """Türkçe kurallarıyla string'i büyük harfe çevirir.
    i -> İ, ı -> I, diğerleri normal upper().
    """
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
    """Türkçe alfabesine göre sıralama anahtarı üretir.
    - Listede olmayan karakterler: listedeki tüm karakterlerden önce gelir (priority 0)
    - Listedeki karakterler: kendi sıraları (priority 1)
    - Kendi aralarında Unicode kod noktasına / alfabedeki sıraya göre sıralanır
    - Kısa kelime önek ise önce gelir (tuple karşılaştırması bunu yapar)
    """
    lower_word = tr_lower(word)
    key_parts = []
    for ch in lower_word:
        if ch in _TR_CHAR_ORDER:
            # Listedeki karakterler: priority 1 (sonra gelir), value = alfabe indeksi
            key_parts.append((1, _TR_CHAR_ORDER[ch]))
        else:
            # Listede olmayan karakterler: priority 0 (önce gelir), value = Unicode kod noktası
            key_parts.append((0, ord(ch)))
    return tuple(key_parts)


def tr_sorted(words: list[str]) -> list[str]:
    """Kelimeleri Türk alfabesine göre sıralar.
    - Büyük/küçük harf farkı gözetmez (içinde tr_lower kullanır)
    - Listede olmayan karakterler (boşluk, noktalama vb.) listedekilerden önce gelir
    - Kendi aralarında Unicode kod noktasına göre sıralanır
    - Bir kelime diğerinin önekiyse kısa olan önce gelir
    - Eşit sayılan kelimeler girdideki sıralarını korur (stable sort)
    - Girdi listesi değişmez, yeni liste döner
    """
    if not words:
        return []
    # enumerate ile orijinal indeksleri sakla (stable sort için tie-breaker)
    indexed = list(enumerate(words))
    # sorted stable olduğu için, key'e (tr_sort_key, original_index) vererek
    # eşitlik durumunda orijinal sırayı koruruz
    indexed.sort(key=lambda x: (_tr_sort_key(x[1]), x[0]))
    return [word for _, word in indexed]
