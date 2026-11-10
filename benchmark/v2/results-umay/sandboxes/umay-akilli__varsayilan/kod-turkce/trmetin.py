# -*- coding: utf-8 -*-
"""
Türkçe metin işleme fonksiyonları.

İçerik:
- tr_lower(s): Türkçe kurallarına göre küçük harfe çevirir.
- tr_upper(s): Türkçe kurallarına göre büyük harfe çevirir.
- tr_sorted(words): Kelimeleri Türk alfabesine göre sıralar.
"""

# Türkçe karakter eşleştirmeleri
_TR_LOWER_MAP = {
    'I': 'ı',
    'İ': 'i',
}

_TR_UPPER_MAP = {
    'ı': 'I',
    'i': 'İ',
}

# Türkçe alfabet sırası (küçük harfler)
_TR_ALPHABET = '0123456789abcçdefgğhıijklmnoöpqrsştuüvwxyz'
_TR_CHAR_ORDER = {ch: idx for idx, ch in enumerate(_TR_ALPHABET)}


def tr_lower(s: str) -> str:
    """
    Türkçe kurallarına göre metni küçük harfe çevirir.
    I -> ı, İ -> i dönüşümlerini doğru yapar.
    """
    if not isinstance(s, str):
        return s
    result = []
    for ch in s:
        result.append(_TR_LOWER_MAP.get(ch, ch.lower()))
    return ''.join(result)


def tr_upper(s: str) -> str:
    """
    Türkçe kurallarına göre metni büyük harfe çevirir.
    ı -> I, i -> İ dönüşümlerini doğru yapar.
    """
    if not isinstance(s, str):
        return s
    result = []
    for ch in s:
        result.append(_TR_UPPER_MAP.get(ch, ch.upper()))
    return ''.join(result)


def tr_sorted(words: list[str]) -> list[str]:
    """
    Kelimeleri Türk alfabesine göre sıralar.

    Kurallar:
    - Büyük/küçük harf farkı gözetilmez (içerde Türkçe kurallarıyla küçültülür).
    - Karakter sırası: 0-9, a-z (Türkçe karakterlerle: ç, ğ, ı, ö, ş, ü).
    - Alfabe listesinde olmayan karakterler (boşluk, noktalama vb.) listedeki
      tüm karakterlerden önce gelir ve kendi aralarında Unicode kod noktasına göre sıralanır.
    - Bir kelime diğerinin önekiyse kısa olan önce gelir.
    - Eşit sayılan kelimeler girdideki sıralarını korur (stable sort).

    Args:
        words: Sıralanacak kelime listesi.

    Returns:
        Yeni bir liste (girdi listesi değiştirilmez).
    """
    if not isinstance(words, list):
        return list(words) if words else []

    def _sort_key(word: str):
        if not isinstance(word, str):
            word = str(word)
        lower_word = tr_lower(word)
        key_parts = []
        for ch in lower_word:
            if ch in _TR_CHAR_ORDER:
                # Alfabedeki karakterler: 1000 + sıra (0'dan başlar)
                key_parts.append(1000 + _TR_CHAR_ORDER[ch])
            else:
                # Alfabe dışı karakterler: Unicode kod noktası (0-999 arası)
                # Bu sayede alfabetik karakterlerden önce gelirler
                key_parts.append(ord(ch))
        return tuple(key_parts)

    # Stable sort: enumerate ile orijinal indeksi ekle
    indexed_words = list(enumerate(words))
    indexed_words.sort(key=lambda x: (_sort_key(x[1]), x[0]))
    return [word for _, word in indexed_words]


if __name__ == '__main__':
    # Basit testler
    print('tr_lower testleri:')
    print(f'  I -> {tr_lower("I")} (beklenen: ı)')
    print(f'  İ -> {tr_lower("İ")} (beklenen: i)')
    print(f'  KİTAP -> {tr_lower("KİTAP")} (beklenen: kitap)')
    print(f'  KİTAPLAR -> {tr_lower("KİTAPLAR")} (beklenen: kitaplar)')
    print(f'  DIŞARI -> {tr_lower("DIŞARI")} (beklenen: dışarı)')

    print('\ntr_upper testleri:')
    print(f'  ı -> {tr_upper("ı")} (beklenen: I)')
    print(f'  i -> {tr_upper("i")} (beklenen: İ)')
    print(f'  kitap -> {tr_upper("kitap")} (beklenen: KİTAP)')
    print(f'  kitaplar -> {tr_upper("kitaplar")} (beklenen: KİTAPLAR)')
    print(f'  dışarı -> {tr_upper("dışarı")} (beklenen: DIŞARI)')

    print('\ntr_sorted testleri:')
    test_words = ['elma', 'armut', 'çilek', 'üzüm', 'karpuz', 'ğaily', 'ıspanak', 'öğle', 'şeker', 'çiğ']
    print(f'  Girdi: {test_words}')
    print(f'  Çıktı: {tr_sorted(test_words)}')
    
    # Prefix testi
    prefix_test = ['elma', 'elması', 'elmalar', 'el']
    print(f'\nPrefix testi:')
    print(f'  Girdi: {prefix_test}')
    print(f'  Çıktı: {tr_sorted(prefix_test)}')
    
    # Büyük/küçük harf testi
    case_test = ['ELMA', 'elma', 'Elma', 'ElMa']
    print(f'\nBüyük/küçük harf testi:')
    print(f'  Girdi: {case_test}')
    print(f'  Çıktı: {tr_sorted(case_test)}')
    
    # Alfabe dışı karakter testi
    special_test = ['elma', '!elma', '?elma', '.elma', ' elma']
    print(f'\nAlfabe dışı karakter testi:')
    print(f'  Girdi: {special_test}')
    print(f'  Çıktı: {tr_sorted(special_test)}')
    
    # Rakam testi
    digit_test = ['elma2', 'elma1', 'elma10', 'elma0']
    print(f'\nRakam testi:')
    print(f'  Girdi: {digit_test}')
    print(f'  Çıktı: {tr_sorted(digit_test)}')
