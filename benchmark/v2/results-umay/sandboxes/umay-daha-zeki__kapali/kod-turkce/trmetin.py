import re
from typing import List

# Türkçe alfabetik sıralama tanımı
# Sıralama: 0123456789abcçdefgğhıijklmnoöpqrsştuüvwxyz
TR_ALPHABET = "0123456789abcçdefgğhıijklmnoöpqrsştuüvwxyz"

def tr_lower(s: str) -> str:
    """Türkçe kurallarıyla küçük harfe çevirir (I<->ı, İ<->i)."""
    s = s.replace('İ', 'i').replace('I', 'ı').replace('İ', 'i')
    return s.lower().replace('İ', 'i').replace('I', 'ı')

def tr_upper(s: str) -> str:
    """Türkçe kurallarıyla büyük harfe çevirir (ı<->I, i<->İ)."""
    s = s.replace('ı', 'I').replace('i', 'İ').replace('ı', 'I')
    return s.upper().replace('ı', 'I').replace('i', 'İ')

def tr_sorted(words: List[str]) -> List[str]:
    """Kelimeleri Türkçe alfabesine göre, büyük/küçük harf farkı gözetmeden sıralar.
    Listede olmayan karakterler en başta, sonra Unicode kod noktasına göre sıralanır.
    Öneklik kuralı: Kısa kelime önce gelir.
    Eşitlik kuralı: Orijinal sıralama korunur (stabil sıralama).
    """
    
    # Karşılaştırma anahtarını oluşturmak için bir fonksiyon
    def custom_sort_key(word: str) -> tuple:
        # 1. Kelimeyi Türkçe kurallarla küçük harfe çevir
        lower_word = tr_lower(word)
        
        # 2. Karakterleri sıralanabilir bir formata dönüştür (Alfabedeki yeri, sonra Unicode değeri)
        key_parts = []
        for char in lower_word:
            try:
                # Alfabe içindeyse, alfabetik sırasını kullan
                index = TR_ALPHABET.find(char)
                key_parts.append((0, index))
            except AttributeError:
                # Alfabe dışında ise (noktalama, boşluk vb.), öncelik 1 ver ve Unicode'u kullan
                key_parts.append((1, ord(char)))
        
        # 3. Öneklik kuralı: Kelime uzunluğu (kısa önce)
        # 4. Stabil sıralama için orijinal indeksini (ancak bu lambda ile sağlamak zor, Python'ın sort stabil olduğu için yeterli)
        return (len(lower_word), tuple(key_parts))

    # Python'ın sort metodu stabildir, bu yüzden sadece anahtara göre sıralama yapmalıyız.
    # Ancak orijinal sıralamayı korumak için zip/sorted kullanıp, anahtar üzerinden sıralama yapmalıyız.
    # Orijinal sıralamayı korumak için indeksleri tutalım.
    indexed_words = list(enumerate(words))
    
    # Anahtar fonksiyonu, sadece kelimeyi alır ve yukarıdaki tuple'ı döndürür.
    def sort_key_wrapper(item): 
        # item: (orijinal_index, kelime)
        _, word = item
        return custom_sort_key(word)

    # Stabil sıralama: Anahtara göre sırala, orijinal indeks kaybolmasın
    sorted_indexed_words = sorted(indexed_words, key=sort_key_wrapper)
    
    # Sonuç listesini oluştur ve sadece kelimeleri al
    result = [word for index, word in sorted_indexed_words]
    
    return result

# Örnek kullanım (Test amaçlı, çalıştırmayın):
# print(tr_lower("İSTANBUL"))
# print(tr_upper("istanbul"))
# test_words = ["elma", "Ayşe", "ıhlamur", "ağaç", "elma.", "Ağaç"] 
# print(tr_sorted(test_words))