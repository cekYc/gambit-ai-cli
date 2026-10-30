# kod-kelime · puan 0.86

**Not:** 6/7 test; başarısız: norm(S.top_k_words("yıl 2026 yıl 2025 ay", 5)) == [("yıl", 2), ("ay", 1)]

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
    # Küçük harfe çevir ve kelime ayırmayı sağla (sadece harf ve rakam olanları al)
    words = re.findall(r'[a-zA-ZğüşıöçĞÜŞİÖÇ0-9]+', text.lower())
    # Kelimeleri say
    word_counts = Counter(words)
    # Sıralama: önce sayıya göre azalan, sonra kelimeye göre alfabetik
    sorted_words = sorted(word_counts.items(), key=lambda x: (-x[1], x[0]))
    # İlk k tanesini döndür
    return sorted_words[:k]
```

## Notlandırılan kod/komut

```
import re
from collections import Counter

def top_k_words(text: str, k: int) -> list[tuple[str, int]]:
    # Küçük harfe çevir ve kelime ayırmayı sağla (sadece harf ve rakam olanları al)
    words = re.findall(r'[a-zA-ZğüşıöçĞÜŞİÖÇ0-9]+', text.lower())
    # Kelimeleri say
    word_counts = Counter(words)
    # Sıralama: önce sayıya göre azalan, sonra kelimeye göre alfabetik
    sorted_words = sorted(word_counts.items(), key=lambda x: (-x[1], x[0]))
    # İlk k tanesini döndür
    return sorted_words[:k]
```
