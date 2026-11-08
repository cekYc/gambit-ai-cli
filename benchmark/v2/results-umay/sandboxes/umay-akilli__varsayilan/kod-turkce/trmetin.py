"""
Türkçe metin işleme fonksiyonları.
"""

# Türkçe alfabesi sıralaması için karakter haritası
# Karakter sırası: 0123456789abcçdefgğhıijklmnoöpqrsştuüvwxyz
_TR_ALPHABET = "0123456789abcçdefgğhıijklmnoöpqrsştuüvwxyz"
_TR_CHAR_ORDER = {ch: i for i, ch in enumerate(_TR_ALPHABET)}


def tr_lower(s: str) -> str:
    """
    Türkçe kurallarıyla küçük harfe çevirir.
    I -> ı, İ -> i, diğer harfler normal kurallarla.
    """
    # Önce Türkçe özel dönüşümleri yap
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
    """
    Türkçe kurallarıyla büyük harfe çevirir.
    ı -> I, i -> İ, diğer harfler normal kurallarla.
    """
    result = []
    for ch in s:
        if ch == 'ı':
            result.append('I')
        elif ch == 'i':
            result.append('İ')
        else:
            result.append(ch.upper())
    return ''.join(result)


def _tr_sort_key(word: str):
    """
    Türkçe sıralama için anahtar üretir.
    - Alfabedeki karakterler kendi sıralarına göre
    - Alfabede olmayan karakterler (boşluk, noktalama vb.) alfabetten önce gelir
    - Alfabede olmayanlar kendi aralarında Unicode kod noktasına göre sıralanır
    - Kelime öneki kuralı: kısa olan önce gelir (tuple doğal olarak bunu yapar)
    """
    lower_word = tr_lower(word)
    key_parts = []
    for ch in lower_word:
        if ch in _TR_CHAR_ORDER:
            # Alfabedeki karakterler: 1 + sırası (0'dan başlar, ama alfabet dışı -1 olacak)
            key_parts.append((1, _TR_CHAR_ORDER[ch]))
        else:
            # Alfabe dışı karakterler: (0, unicode_kod_noktası)
            # Böylece alfabetten önce gelirler ve kendi aralarında unicode sırasına göre sıralanır
            key_parts.append((0, ord(ch)))
    return tuple(key_parts)


def tr_sorted(words: list[str]) -> list[str]:
    """
    Kelimeleri Türk alfabesine göre sıralar.
    - Büyük/küçük harf farkı gözetmez (Türkçe kurallarla küçültür)
    - Girdi listesi değişmez, yeni liste döner
    - Karakter sırası: 0123456789abcçdefgğhıijklmnoöpqrsştuüvwxyz
    - Alfabede olmayan karakterler (boşluk, noktalama vb.) listedeki tüm karakterlerden önce gelir
    - Bir kelime diğerinin önekiyse kısa olan önce gelir
    - Eşit sayılan kelimeler girdideki sıralarını korur (stable sort)
    """
    # Stable sort için enumerate kullanıp orijinal indeksi de key'e ekle
    indexed_words = list(enumerate(words))
    indexed_words.sort(key=lambda iw: (_tr_sort_key(iw[1]), iw[0]))
    return [w for _, w in indexed_words]


if __name__ == "__main__":
    # Basit testler
    print("tr_lower testleri:")
    print(f"  'İSTANBUL' -> '{tr_lower('İSTANBUL')}'")
    print(f"  'IŞIK' -> '{tr_lower('IŞIK')}'")
    print(f"  'Merhaba' -> '{tr_lower('Merhaba')}'")
    
    print("\ntr_upper testleri:")
    print(f"  'istanbul' -> '{tr_upper('istanbul')}'")
    print(f"  'ışık' -> '{tr_upper('ışık')}'")
    print(f"  'merhaba' -> '{tr_upper('merhaba')}'")
    
    print("\ntr_sorted testleri:")
    test_words = ["elma", "armut", "çilek", "üzüm", "İstanbul", "istanbul", "Istanbul", "ıslak"]
    print(f"  Girdi: {test_words}")
    print(f"  Çıktı: {tr_sorted(test_words)}")
    
    # Önek testi
    test_prefix = ["elma", "el", "eleman", "elmas"]
    print(f"\n  Önek testi - Girdi: {test_prefix}")
    print(f"  Önek testi - Çıktı: {tr_sorted(test_prefix)}")
    
    # Alfabe dışı karakter testi
    test_special = ["!elma", "elma", "-armut", "armut"]
    print(f"\n  Alfabe dışı - Girdi: {test_special}")
    print(f"  Alfabe dışı - Çıktı: {tr_sorted(test_special)}")
    
    # Sayı testi
    test_numbers = ["elma2", "elma1", "elma10", "elma"]
    print(f"\n  Sayı testi - Girdi: {test_numbers}")
    print(f"  Sayı testi - Çıktı: {tr_sorted(test_numbers)}")