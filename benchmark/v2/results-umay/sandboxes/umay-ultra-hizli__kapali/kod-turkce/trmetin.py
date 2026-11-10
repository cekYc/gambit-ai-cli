import re
from functools import cmp_to_key

def tr_lower(s: str) -> str:
    """Türkçe kurallarıyla küçük harfe çevirir (I<->ı, İ<->i)."""
    s = s.replace('İ', 'i').replace('I', 'ı')
    return s.lower()

def tr_upper(s: str) -> str:
    """Türkçe kurallarıyla büyük harfe çevirir (ı<->I, i<->İ)."""
    s = s.replace('i', 'İ').replace('ı', 'I')
    return s.upper()

def tr_sorted(words: list[str]) -> list[str]:
    """Kelimeleri Türk alfabesine göre sıralar (büyük/küçük harf duyarsız, orijinal liste değişmez)."""
    
    # Türkçe alfabe sırası: 0123456789abcçdefgğhıijklmnoöpqrsştuüvwxyz
    # Listede olmayanlar önce gelir ve Unicode'a göre sıralanır.
    # Kelime ön eki kuralı uygulanır.
    
    def custom_compare(a: str, b: str) -> int:
        # 1. Ön ek kuralı: Kısa olan önce gelir
        len_a = len(a)
        len_b = len(b)
        if a.startswith(b) and len_a > len_b: return 1
        if b.startswith(a) and len_b > len_a: return -1
        
        # Karşılaştırmadan önce sadece alfabedeki karakterleri (ve sayıları) tutacak bir ön işlem yapalım.
        # Alfabede olmayanlar Unicode'a göre sıralanacak, alfabedeki ise özel sıraya göre.
        
        # Alfabe sırası için haritalama (önce sayısal, sonra alfabetik)
        # Karakter sırası: 0123456789abcçdefgğhıijklmnoöpqrsştuüvwxyz
        turkish_order = "0123456789abcçdefgğhıijklmnoöpqrsştuüvwxyz"
        
        def get_sort_key(word: str) -> tuple:
            # Alfabede olmayanları (noktalama, boşluk) önce ve Unicode sırasına göre sıralamak için.
            # Alfabedeki karakterleri ise özel sıraya göre sıralamak için.
            
            # Kelimeyi temizleyip (alfabetik/sayısal kısım) ve diğer karakterleri ayırıyoruz.
            # Bu karmaşık kural için, önce temizlenmiş versiyonu alıp, sonra temizlenmemiş orijinalini kullanmak daha doğru.
            
            # Basitleştirme: Tüm kelimeleri önce tr_lower ile normalize et.
            lower_word = tr_lower(word)
            
            # Sıralama anahtarı: (Öncelik Tipi, Sıra Değeri, Orijinal İndeks)
            
            # 1. Alfabedeki/Sayısal karakterler için sıralama
            key_chars = []
            for char in lower_word:
                if char in turkish_order:
                    key_chars.append(turkish_order.index(char))
                else:
                    # Alfabede olmayanlar, özel karakterler grubunda toplanacak. 
                    # Unicode değerine göre sıralanacaklar, bu yüzden Unicode değerini kullanıyoruz.
                    key_chars.append(ord(char))
            
            # Anahtar: (Karakter Türü Önceliği, Karakter Sırası Listesi, Orijinal Word)
            # Karakter Türü Önceliği: 0=Alfabesel/Sayısal, 1=Diğer (Unicode)
            return (0, key_chars, word) if any(c in turkish_order for c in lower_word) else (1, [ord(c) for c in lower_word], word)

        # Girdi listesini korumak için kopyasını alıyoruz ve orijinal indeksi saklıyoruz.
        indexed_words = list(enumerate(words))
        
        def final_compare(item_a, item_b):
            # item = (index, word)
            word_a = item_a[1]
            word_b = item_b[1]
            
            # Ön ek kontrolü (tekrar kontrol ediyoruz, çünkü key bazen yeterli olmayabilir)
            if word_a.startswith(word_b) and len(word_a) > len(word_b): return 1
            if word_b.startswith(word_a) and len(word_b) > len(word_a): return -1

            # Anahtar tabanlı sıralama (büyük/küçük harf duyarsız)
            key_a = get_sort_key(word_a)
            key_b = get_sort_key(word_b)
            
            if key_a < key_b: return -1
            if key_a > key_b: return 1
            
            # Eşitse orijinal indeksi koru (girdideki sırayı koru)
            return item_a[0] - item_b[0]

    # Karşılaştırma fonksiyonunu cmp_to_key ile sıralama anahtarına çeviriyoruz
    sorted_indexed = sorted(indexed_words, key=cmp_to_key(final_compare))
    
    # Sadece kelimeleri döndürüyoruz
    return [item[1] for item in sorted_indexed]
