# kod-kelime · puan 1.00

**Not:** 7/7 test

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
import re
from collections import Counter

def top_k_words(text: str, k: int) -> list[tuple[str, int]]:
    # Metni küçük harfe çevir ve sadece kelime karakterlerini (harfleri) içeren bir liste al
    # [a-zA-Z\u00C0-\u017F] gibi geniş kapsamlı regex yerine \w kullanarak 
    # ancak rakamları/alt çizgileri dışlayarak Türkçe dahil harfleri yakalıyoruz.
    words = re.findall(r'[a-zçğışüöğıİĞİŞÜÖÇ]+', text.lower())
    
    # Kelimelerin frekansını hesapla
    counts = Counter(words)
    
    # Sıralama kriteri: 
    # 1. Sayısal değer (azalan olması için -x[1])
    # 2. Alfabetik sıra (artan olması için x[0])
    sorted_words = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    
    # İlk k elemanı döndür
    return sorted_words[:k]
```

## Notlandırılan kod/komut

```
import re
from collections import Counter

def top_k_words(text: str, k: int) -> list[tuple[str, int]]:
    # Metni küçük harfe çevir ve sadece kelime karakterlerini (harfleri) içeren bir liste al
    # [a-zA-Z\u00C0-\u017F] gibi geniş kapsamlı regex yerine \w kullanarak 
    # ancak rakamları/alt çizgileri dışlayarak Türkçe dahil harfleri yakalıyoruz.
    words = re.findall(r'[a-zçğışüöğıİĞİŞÜÖÇ]+', text.lower())
    
    # Kelimelerin frekansını hesapla
    counts = Counter(words)
    
    # Sıralama kriteri: 
    # 1. Sayısal değer (azalan olması için -x[1])
    # 2. Alfabetik sıra (artan olması için x[0])
    sorted_words = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    
    # İlk k elemanı döndür
    return sorted_words[:k]
```
