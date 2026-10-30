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

## Düşünme

Kullanıcı Türkçe metin işleme ve kelime sıkılığı hesabı yapan bir fonksiyon yazmamı istiyor. İşte gereksinimler:

1. `top_k_words(text: str, k: int) -> list[tuple[str, int]]` tipi
2. Büyük/küçük harf farkı önemsiz (küçültme)
3. Kelime sadece alfabetik karakterlerden oluşur (rakamlar ve noktalama dahil değil)
4. Sıralama: Frekans azalan, eşit frekans için alfabetik
5. k > kelime sayısı ise tüm kelimeleri döndür

Python'da bunu yapmak için:
- Kelimeleri ayırma için regex kullanabilirim (`\w+` veya `\w` Türkçe için uygun değil)
- Sadece harfleri tutmak lazım, rakam ve noktalama hariç

Türkçe karakterler için regex biraz dikkatli olmalı. Tüm alfabetik karakterleri bulmam gerekiyor. Python'un `isalnum()` kontrolü sayıları da kabul ediyor ama ben sadece harfli kelimeler istiyorum.

Basit bir yaklaşım:
1. Texti küçük harfe çevir
2. Kelimeleri ayır (sadece harfler)
3. Sıklık hesapla
4. Sırala ve döndür

Regex ile `\w` harf ve rakam dahil, ama ben sadece harfli istiyorum. Türkçe karakterleri de dahil edeceğim.

Python'da regex'de `[a-zçğıöüş]` gibi özel karakterler yazabilir veya basitçe tüm alfabetik karakterleri kabul eden bir yaklaşım kullanabilirim.


## Cevap

```python
import re
from collections import Counter

def top_k_words(text: str, k: int) -> list[tuple[str, int]]:
    # Metni küçük harfe çevir ve kelimeye dönüştürmek için sadece harfli karakterleri tut
    words = re.findall(r'[a-zçğıöşü]', text.lower())
    
    if not words:
        return []
    
    # Sıklık hesapla
    word_counts = Counter(words)
    
    # (kelime, sayı) çiftlerini sırala: sayı azalan, eşitlikte alfabetik
    sorted_words = sorted(
        word_counts.items(),
        key=lambda x: (-x[1], x[0])
    )
    
    # İlk k'yi al
    return sorted_words[:k] if len(sorted_words) >= k else sorted_words
```

## Notlandırılan kod/komut

```
import re
from collections import Counter

def top_k_words(text: str, k: int) -> list[tuple[str, int]]:
    # Metni küçük harfe çevir ve kelimeye dönüştürmek için sadece harfli karakterleri tut
    words = re.findall(r'[a-zçğıöşü]', text.lower())
    
    if not words:
        return []
    
    # Sıklık hesapla
    word_counts = Counter(words)
    
    # (kelime, sayı) çiftlerini sırala: sayı azalan, eşitlikte alfabetik
    sorted_words = sorted(
        word_counts.items(),
        key=lambda x: (-x[1], x[0])
    )
    
    # İlk k'yi al
    return sorted_words[:k] if len(sorted_words) >= k else sorted_words
```
