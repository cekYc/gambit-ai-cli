def tr_lower(s):
    # Türkçe harf dönüşümlerini (İ->i, I->ı) standart kütüphane ile uygular
    s = s.replace("İ", "i")
    s = s.replace("I", "ı")
    return s.lower()

def tr_upper(s):
    # Türkçe harf dönüşümlerini (i->İ, ı->I) standart kütüphane ile uygular
    s = s.replace("i", "İ")
    s = s.replace("ı", "I")
    return s.upper()

# Türkçe alfabenin sırası (0-9, a-z, ç, ğ, h, ı, ö, ş, ü) ve özel kurallar
TR_CHARS = "0123456789abcçdefgğhıijklmnoöpqrsştuüvwxyz"
TR_CHAR_MAP = {char: i for i, char in enumerate(TR_CHARS)}

def get_sort_key(word):
    """Kelime için Türkçe sıralamaya uygun tuple anahtarını döndürür."""
    word_lower = tr_lower(word)
    
    key_parts = []
    
    for char in word_lower:
        if char in TR_CHAR_MAP:
            # 1: Alfabetik, TR_CHARS indeksi
            key_parts.append((1, TR_CHAR_MAP[char])) 
        else:
            # 0: Alfabetik olmayan (öncelikli), Unicode değeri
            key_parts.append((0, ord(char)))
    
    # Prefix kuralı için kelime uzunluğunu son eleman olarak ekle (kısa olan önce gelmeli)
    return tuple(key_parts) + (len(word),)


def tr_sorted(words) -> list[str]:
    """Kelime listesini Türk alfabesine göre, büyük/küçük harf farkı gözetmeden sıralar.
    Girdi listesini değiştirmez.
    """
    return sorted(words, key=get_sort_key)
