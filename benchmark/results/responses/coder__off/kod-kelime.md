# kod-kelime · puan 0.14

**Not:** 1/7 test; başarısız: norm(S.top_k_words("elma armut elma kiraz armut elma", 2)) == [("elma", 3), ("armut", 2)] | norm(S.top_k_words("Çay, çay! ÇAY kahve?", 1)) == [("çay", 3)] | norm(S.top_k_words("b a c b a c d", 3)) == [("a", 2), ("b", 2), ("c", 2)] | norm(S.top_k_words("yıl 2026 yıl 2025 ay", 5)) == [("yıl", 2), ("ay", 1)] | norm(S.top_k_words("göğüs-ağrısı göğüs", 2)) == [("göğüs", 2), ("ağrısı", 1)]

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
from collections import Counter

def top_k_words(text: str, k: int) -> list[tuple[str, int]]:
    # Küçük harfe çevirme ve rakamlar ve noktalama işaretleri hariç tutma
    cleaned_text = ''.join(c.lower() for c in text if c.isalpha())
    
    # Kelime sayısını hesaplama
    word_count = Counter(cleaned_text.split())
    
    # En sık geçen k kelimesi çiftlerini döndürme
    return sorted(word_count.items(), key=lambda x: (-x[1], x[0]))[:k]

```

## Notlandırılan kod/komut

```
from collections import Counter

def top_k_words(text: str, k: int) -> list[tuple[str, int]]:
    # Küçük harfe çevirme ve rakamlar ve noktalama işaretleri hariç tutma
    cleaned_text = ''.join(c.lower() for c in text if c.isalpha())
    
    # Kelime sayısını hesaplama
    word_count = Counter(cleaned_text.split())
    
    # En sık geçen k kelimesi çiftlerini döndürme
    return sorted(word_count.items(), key=lambda x: (-x[1], x[0]))[:k]
```
