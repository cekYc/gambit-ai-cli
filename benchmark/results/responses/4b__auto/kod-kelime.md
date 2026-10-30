# kod-kelime · puan 0.86

**Not:** 6/7 test; başarısız: norm(S.top_k_words("göğüs-ağrısı göğüs", 2)) == [("göğüs", 2), ("ağrısı", 1)]

## Prompt

Python'da `top_k_words(text: str, k: int) -> list[tuple[str, int]]` fonksiyonunu yaz. Metinde en sık geçen
k kelimeyi (kelime, sayı) çiftleri olarak döndürsün.
- Büyük/küçük harf farkı önemsiz; kelimeler küçük harfe çevrilsin.
- Kelime ardışık harflerden oluşur (Türkçe harfler dahil); rakamlar ve noktalama işaretleri kelimeye dahil değildir.
- Sıralama: sayıya göre azalan; sayılar eşitse kelimeye göre alfabetik (Python'un normal string sıralaması).
- k, farklı kelime sayısından büyükse hepsini döndürsün.
Sadece Python kodunu tek bir ```python bloğu içinde ver.

## Cevap

```python
def top_k_words(text: str, k: int) -> list[tuple[str, int]]:
    import string
    
    # Noktalama işaretlerini ve boşlukları ayırmak için bir regex kullanalım.
    # Rakamlar kelime dizgini değil, kelime içindeki karakterler değildir (soruda belirtilmiş).
    # Ancak "Kelime ardışık harflerden oluşur... rakamlar ve noktalama işaretleri kelimeye dahil değildir" 
    # ifadesi, metindeki rakamları ve noktaları ayrıştırıp kelimelerden çıkarmak gerektiğini ima ediyor.
    # Regex ile bunu yapacağımız en temiz yol:
    
    import re
    
    # Noktalama işareti karakterlerini bulma
    punctuation_pattern = re.compile(f"[{re.escape(''.join(string.punctuation))}]+", re.UNICODE)
    
    words_count = {}
    
    for word in text.split():
        # Kelimeyi temizle: Büyük/küçük harf farkını ortadan kaldırmak ve noktalama/rahasları çıkarmak
        
        # 1. Büyük/küçük harfe çevir
        clean_word = word.lower()
        
        # 2. Noktalama işaretlerini ve rakamları kaldır (kelimeye dahil olmaması için)
        # Soruda "Türkçe harfler dahil" denmiş, bu yüzden unicode pattern kullanmak daha güvenli ama 
        # genel noktalama + rakam silme yeterli olacaktır.
        filtered_word = clean_word.strip(string.punctuation)
        
        # Rakamları da kaldıralım çünkü soru "rakamlar... kelimeye dahil değildir" diyor.
        if not re.match(r'^[a-züöçşğı]+$', filtered_word):
             # Eğer rakam içeriyorsa veya başka özel karakter varsa (Türkçe harfler hariç), temizleyelim
             filtered_word = "".join(char for char in filtered_word if char.isalpha() or char in "üöçşğı")
        
        if not filtered_word:
            continue
            
        words_count[filtered_word] = words_count.get(filtered_word, 0) + 1
        
    # Sıralama: sayıya göre azalan (reverse=True), sonra kelimeye göre alfabetik
    sorted_words = sorted(words_count.items(), key=lambda x: (-x[1], x[0]))
    
    return sorted_words[:k]
```

## Notlandırılan kod/komut

```
def top_k_words(text: str, k: int) -> list[tuple[str, int]]:
    import string
    
    # Noktalama işaretlerini ve boşlukları ayırmak için bir regex kullanalım.
    # Rakamlar kelime dizgini değil, kelime içindeki karakterler değildir (soruda belirtilmiş).
    # Ancak "Kelime ardışık harflerden oluşur... rakamlar ve noktalama işaretleri kelimeye dahil değildir" 
    # ifadesi, metindeki rakamları ve noktaları ayrıştırıp kelimelerden çıkarmak gerektiğini ima ediyor.
    # Regex ile bunu yapacağımız en temiz yol:
    
    import re
    
    # Noktalama işareti karakterlerini bulma
    punctuation_pattern = re.compile(f"[{re.escape(''.join(string.punctuation))}]+", re.UNICODE)
    
    words_count = {}
    
    for word in text.split():
        # Kelimeyi temizle: Büyük/küçük harf farkını ortadan kaldırmak ve noktalama/rahasları çıkarmak
        
        # 1. Büyük/küçük harfe çevir
        clean_word = word.lower()
        
        # 2. Noktalama işaretlerini ve rakamları kaldır (kelimeye dahil olmaması için)
        # Soruda "Türkçe harfler dahil" denmiş, bu yüzden unicode pattern kullanmak daha güvenli ama 
        # genel noktalama + rakam silme yeterli olacaktır.
        filtered_word = clean_word.strip(string.punctuation)
        
        # Rakamları da kaldıralım çünkü soru "rakamlar... kelimeye dahil değildir" diyor.
        if not re.match(r'^[a-züöçşğı]+$', filtered_word):
             # Eğer rakam içeriyorsa veya başka özel karakter varsa (Türkçe harfler hariç), temizleyelim
             filtered_word = "".join(char for char in filtered_word if char.isalpha() or char in "üöçşğı")
        
        if not filtered_word:
            continue
            
        words_count[filtered_word] = words_count.get(filtered_word, 0) + 1
        
    # Sıralama: sayıya göre azalan (reverse=True), sonra kelimeye göre alfabetik
    sorted_words = sorted(words_count.items(), key=lambda x: (-x[1], x[0]))
    
    return sorted_words[:k]
```
