# -*- coding: utf-8 -*-
"""
Türkçe metin işleme yardımcı fonksiyonları.
"""
from __future__ import annotations

# Türkçe alfabesi sıralaması için karakter -> sıra eşlemesi
_TR_ALPHABET = "0123456789abcçdefgğhıijklmnoöpqrsştuüvwxyz"
_TR_ORDER = {ch: i for i, ch in enumerate(_TR_ALPHABET)}

# Türkçe özel büyük/küçük harf eşleştirmeleri
# lower(): Büyük -> Küçük
_TR_LOWER_MAP = {
    'I': 'ı',   # Büyük I -> küçük ı
    'İ': 'i',   # Büyük İ -> küçük i
}
# upper(): Küçük -> Büyük
_TR_UPPER_MAP = {
    'ı': 'I',   # Küçük ı -> Büyük I
    'i': 'İ',   # Küçük i -> Büyük İ
    'I': 'İ',   # ASCII Büyük I -> Türkçe Büyük İ (ISTANBUL -> İSTANBUL)
}


def tr_lower(s: str) -> str:
    """
    Türkçe kurallarıyla metni küçük harfe çevirir.
    I -> ı, İ -> i dönüşümlerini yapar; diğer harfler için str.lower() kullanır.
    Özel harfler ÖNCE işlenir (lower() çağrılmadan), sonra geriye kalanlar için lower().
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
    """
    Türkçe kurallarıyla metni büyük harfe çevirir.
    ı -> I, i -> İ, I -> İ dönüşümlerini yapar; diğer harfler için str.upper() kullanır.
    Özel harfler ÖNCE işlenir (upper() çağrılmadan), sonra geriye kalanlar için upper().
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
    """
    Türkçe alfabetik sıralama için sort key üretir.
    - Alfabedeki karakterler için _TR_ORDER indeksi kullanılır (0+)
    - Alfabede olmayan karakterler için -1000 + ord(ch) kullanılır
    - Bu sayede hepsi alfabedekilerden (0+) önce gelir
    - Kendi aralarında Unicode kod noktasına göre artan sırada sıralanır
    - Kelime uzunluğu tie-breaker olarak eklenir (prefix kuralı için)
    """
    lower_word = tr_lower(word)
    key_parts = []
    for ch in lower_word:
        if ch in _TR_ORDER:
            key_parts.append(_TR_ORDER[ch])
        else:
            # Alfabede olmayan karakterler: negatif offset + Unicode değeri
            key_parts.append(-1000 + ord(ch))
    # Kelime uzunluğunu son tie-breaker olarak ekle (prefix kuralı için)
    key_parts.append(len(lower_word))
    return tuple(key_parts)


def tr_sorted(words: list[str]) -> list[str]:
    """
    Kelimeleri Türk alfabesine göre sıralar.
    
    Kurallar:
    - Büyük/küçük harf farkı gözetilmez (içinde tr_lower kullanılır)
    - Karakter sırası: 0123456789abcçdefgğhıijklmnoöpqrsştuüvwxyz
    - Bu listede olmayan karakterler (boşluk, noktalama vb.) listedeki tüm karakterlerden önce gelir
    - Kendi aralarında Unicode kod noktasına göre sıralanır
    - Bir kelime diğerinin önekiyse kısa olan önce gelir
    - Eşit sayılan kelimeler girdideki sıralarını korur (stable sort)
    - Girdi listesi değiştirilmez, yeni liste döndürülür
    """
    # Python'un sorted() stable'dır, bu yüzden eşit kelimeler sırasını korur
    return sorted(words, key=_tr_sort_key)


if __name__ == "__main__":
    # Basit testler
    print("tr_lower testleri:")
    print(f"  'İSTANBUL' -> '{tr_lower('İSTANBUL')}'")
    print(f"  'IŞIK' -> '{tr_lower('IŞIK')}'")
    print(f"  'istanbul' -> '{tr_lower('istanbul')}'")
    print(f"  'Iıİi' -> '{tr_lower('Iıİi')}'")
    
    print("\ntr_upper testleri:")
    print(f"  'istanbul' -> '{tr_upper('istanbul')}'")
    print(f"  'ışık' -> '{tr_upper('ışık')}'")
    print(f"  'ISTANBUL' -> '{tr_upper('ISTANBUL')}'")
    print(f"  'ıİiI' -> '{tr_upper('ıİiI')}'")
    
    print("\ntr_sorted testleri:")
    test_list = ["elma", "armut", "çilek", "üzüm", "İncir", "ıspanak", "İzmir", "istanbul"]
    print(f"  Girdi: {test_list}")
    print(f"  Çıktı: {tr_sorted(test_list)}")
    
    # Prefix test
    test_prefix = ["elma", "elmaci", "el", "elm"]
    print(f"\nPrefix test: {test_prefix}")
    print(f"  Çıktı: {tr_sorted(test_prefix)}")
    
    # Alfabede olmayan karakterler test
    test_special = ["!elma", "?armut", "elma", "1elma", " elma"]
    print(f"\nÖzel karakter test: {test_special}")
    print(f"  Çıktı: {tr_sorted(test_special)}")
    
    # Stability test
    test_stable = ["elma", "Elma", "ELMA"]
    print(f"\nStability test: {test_stable}")
    print(f"  Çıktı: {tr_sorted(test_stable)}")