# kod-kelime · puan 0.29

**Not:** 2/7 test; başarısız: norm(S.top_k_words("elma armut elma kiraz armut elma", 2)) == [("elma", 3), ("armut", 2)] | norm(S.top_k_words("Çay, çay! ÇAY kahve?", 1)) == [("çay", 3)] | norm(S.top_k_words("yıl 2026 yıl 2025 ay", 5)) == [("yıl", 2), ("ay", 1)] | norm(S.top_k_words("göğüs-ağrısı göğüs", 2)) == [("göğüs", 2), ("ağrısı", 1)] | norm(S.top_k_words("bir iki", 10)) == [("bir", 1), ("iki", 1)]

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
    # Sadece harflerden oluşan kelimeleri al (Türkçe karakterler de dahil), küçük harfe çevir
    tokens = [word.lower() for word in re.findall(r'[a-zA-ZçÇğĞıİöÖşŞüÜ]', text)]
    counts = Counter(tokens)

    # Sıralama: önce frekans azalan (-count), sonra alfabetik artan (key)
    sorted_items = sorted(counts.items(), key=lambda x: (-x[1], x[0]))

    return sorted_items[:k]
```

## Notlandırılan kod/komut

```
import re
from collections import Counter


def top_k_words(text: str, k: int) -> list[tuple[str, int]]:
    # Sadece harflerden oluşan kelimeleri al (Türkçe karakterler de dahil), küçük harfe çevir
    tokens = [word.lower() for word in re.findall(r'[a-zA-ZçÇğĞıİöÖşŞüÜ]', text)]
    counts = Counter(tokens)

    # Sıralama: önce frekans azalan (-count), sonra alfabetik artan (key)
    sorted_items = sorted(counts.items(), key=lambda x: (-x[1], x[0]))

    return sorted_items[:k]
```
