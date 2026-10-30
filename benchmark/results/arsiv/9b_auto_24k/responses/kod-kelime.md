# kod-kelime · puan 0.86

**Not:** 6/7 test; başarısız: norm(S.top_k_words("b a c b a c d", 3)) == [("a", 2), ("b", 2), ("c", 2)]

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
from typing import List, Tuple

def top_k_words(text: str, k: int) -> List[Tuple[str, int]]:
    # Metni küçük harfe çevir ve Türkçe karakterleri (ç, ğ, ı, ö, ş, ü ve büyük halleri) koruyarak
    # sadece harflerden oluşan kelimeleri ayır. Rakamlar ve noktalama işaretlerini filtrele.
    text_lower = text.lower()
    
    # Türkçe karakterleri de dahil eden harf dizisi: a-z ve ç, ğ, ı, ö, ş, ü
    turkish_letters = "abcdefghijklmnopqrstuvwxyzçğıöşü"
    
    words = []
    current_word = []
    
    for char in text_lower:
        if char in turkish_letters:
            current_word.append(char)
        else:
            if current_word:
                words.append("".join(current_word))
                current_word = []
    
    # Son kelimeyi ekle (string sonu boşluk veya noktalama olabilir)
    if current_word:
        words.append("".join(current_word))
        
    # Kelimelerin sayımını yap ve en sık k tanesini al
    counter = Counter(words)
    most_common = counter.most_common(k)
    
    return most_common
```

## Notlandırılan kod/komut

```
import re
from collections import Counter
from typing import List, Tuple

def top_k_words(text: str, k: int) -> List[Tuple[str, int]]:
    # Metni küçük harfe çevir ve Türkçe karakterleri (ç, ğ, ı, ö, ş, ü ve büyük halleri) koruyarak
    # sadece harflerden oluşan kelimeleri ayır. Rakamlar ve noktalama işaretlerini filtrele.
    text_lower = text.lower()
    
    # Türkçe karakterleri de dahil eden harf dizisi: a-z ve ç, ğ, ı, ö, ş, ü
    turkish_letters = "abcdefghijklmnopqrstuvwxyzçğıöşü"
    
    words = []
    current_word = []
    
    for char in text_lower:
        if char in turkish_letters:
            current_word.append(char)
        else:
            if current_word:
                words.append("".join(current_word))
                current_word = []
    
    # Son kelimeyi ekle (string sonu boşluk veya noktalama olabilir)
    if current_word:
        words.append("".join(current_word))
        
    # Kelimelerin sayımını yap ve en sık k tanesini al
    counter = Counter(words)
    most_common = counter.most_common(k)
    
    return most_common
```
