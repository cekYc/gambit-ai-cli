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
    # Türkçe harfleri destekleyen kelime çıkarımı
    words = re.findall(r"[a-zA-ZçÇğĞıİöÖşŞüÜ]+", text.lower())
    
    counter = Counter(words)
    
    # Sıralama: sayıya göre azalan, eşitse kelimeye göre alfabetik
    sorted_items = sorted(counter.items(), key=lambda x: (-x[1], x[0]))
    
    return sorted_items[:k]
```

## Notlandırılan kod/komut

```
import re
from collections import Counter


def top_k_words(text: str, k: int) -> list[tuple[str, int]]:
    # Türkçe harfleri destekleyen kelime çıkarımı
    words = re.findall(r"[a-zA-ZçÇğĞıİöÖşŞüÜ]+", text.lower())
    
    counter = Counter(words)
    
    # Sıralama: sayıya göre azalan, eşitse kelimeye göre alfabetik
    sorted_items = sorted(counter.items(), key=lambda x: (-x[1], x[0]))
    
    return sorted_items[:k]
```
