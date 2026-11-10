import re

# Türkçe harf sırası (0-9, a-z, özel Türkçe harfler)
TR_ALPHABET = "0123456789abcçdefgğhıijklmnoöpqrsştuüvwxyz"

# Harf sırasına göre bir sözlüğe dönüştürme
TR_ORDER = {char: i for i, char in enumerate(TR_ALPHABET)}

def tr_lower(s: str) -> str:
    """Türkçe kurallarıyla metni küçük harfe çevirir (İ↔i, I↔ı)."""
    # Unicode'dan bağımsız ve kesin Türkçe dönüşümler
    s = s.replace('İ', 'i')
    s = s.replace('I', 'ı')
    # Geri kalan harfler için standart lower kullanmak güvenlidir.
    return s.lower()

def tr_upper(s: str) -> str:
    """Türkçe kurallarıyla metni büyük harfe çevirir (i↔İ, ı↔I)."""
    # Unicode'dan bağımsız ve kesin Türkçe dönüşümler
    s = s.replace('i', 'İ')
    s = s.replace('ı', 'I')
    return s.upper()

def tr_sorted(words: list[str]) -> list[str]:
    """Kelime listesini Türk alfabesine göre sıralar (büyük/küçük harf farkı gözetmeksizin)."""

    def sort_key(word: str) -> tuple:
        # 1. Normalizasyon (küçük harf ve Türkçe kurallara uygun)
        normalized_word = tr_lower(word)

        # 2. Karakterleri iki tipe ayır: Non-Alpha ve Alpha.
        # Non-alpha karakterler başta (tip 0), alfabedekiler sonra (tip 1) gelmelidir.
        chars = []
        non_alpha = []
        
        for char in normalized_word:
            if char in TR_ORDER:
                # Alfabedeki karakter: (1, TR_ORDER[char], char)
                chars.append((1, TR_ORDER[char], char))
            else:
                # Alfabede olmayan karakter: (0, Unicode pozisyonu, char)
                # Non-alpha karakterler önce gelir ve Unicode kod noktasına göre sıralanır.
                non_alpha.append((0, ord(char), char))

        # Karakter listesini birleştir.
        full_key = non_alpha + chars
        
        # 3. Sıralama tuple'ı: 
        # (Kelime Uzunluğu (önce kısa olan), Tüm Karakter Tuple'ı)
        # Uzunluk, önek kuralını sağlar. Tuple, karaktere göre sıralanır.
        return (len(word), tuple(full_key))

    # Python'un sorted fonksiyonu stabil olduğu için eşit kelimeler girdideki sırasını korur.
    return sorted(words, key=sort_key)
