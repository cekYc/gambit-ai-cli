# kod-slug · puan 0.62

**Not:** 5/8 test; başarısız: S.tr_slug("ŞEKER  --  ĞÜÖ") == "seker-guo" | S.tr_slug("2026 Yılı: %50 İndirim!") == "2026-yili-50-indirim" | S.tr_slug("a__b..c") == "a-b-c"

## Prompt

Python'da `tr_slug(text: str) -> str` fonksiyonunu yaz. Metni URL'de kullanılacak kısa ada (slug) çevirsin:
- Türkçe harfler dönüşsün: ç→c, ğ→g, ı→i, ö→o, ş→s, ü→u; büyük halleri (Ç, Ğ, I, İ, Ö, Ş, Ü) de aynı şekilde.
- Sonuç tamamen küçük harf olsun.
- Harf ve rakam dışındaki her karakter dizisi tek bir '-' olsun.
- Baştaki ve sondaki '-' karakterleri silinsin.
Örnek: tr_slug("Merhaba Dünya!") == "merhaba-dunya"
Sadece Python kodunu tek bir ```python bloğu içinde ver.

## Cevap

```python
import re

def tr_slug(text: str) -> str:
    # Türkçe karakterleri yer değiştirmek için özel karakter dizisi oluşturma
    turkish_to_ascii = {
        'ç': 'c', 'Ç': 'C',
        'ğ': 'g', 'Ğ': 'G',
        'ı': 'i', 'İ': 'I',
        'ö': 'o', 'Ö': 'O',
        'ş': 's', 'Ş': 'S',
        'ü': 'u', 'Ü': 'U'
    }
    
    # Metni özel karakter dizisiyle değiştirme
    for turkish_char, ascii_char in turkish_to_ascii.items():
        text = text.replace(turkish_char, ascii_char)
    
    # Sonuç tamamen küçük harf olsun
    result = text.lower()
    
    # Harf ve rakam dışındaki her karakter dizisi tek bir '-' olsun
    result = re.sub(r'[^a-z0-9]', '-', result)
    
    # Baştaki ve sondaki '-' karakterleri silinsin
    result = result.strip('-')
    
    return result
```

## Notlandırılan kod/komut

```
import re

def tr_slug(text: str) -> str:
    # Türkçe karakterleri yer değiştirmek için özel karakter dizisi oluşturma
    turkish_to_ascii = {
        'ç': 'c', 'Ç': 'C',
        'ğ': 'g', 'Ğ': 'G',
        'ı': 'i', 'İ': 'I',
        'ö': 'o', 'Ö': 'O',
        'ş': 's', 'Ş': 'S',
        'ü': 'u', 'Ü': 'U'
    }
    
    # Metni özel karakter dizisiyle değiştirme
    for turkish_char, ascii_char in turkish_to_ascii.items():
        text = text.replace(turkish_char, ascii_char)
    
    # Sonuç tamamen küçük harf olsun
    result = text.lower()
    
    # Harf ve rakam dışındaki her karakter dizisi tek bir '-' olsun
    result = re.sub(r'[^a-z0-9]', '-', result)
    
    # Baştaki ve sondaki '-' karakterleri silinsin
    result = result.strip('-')
    
    return result
```
