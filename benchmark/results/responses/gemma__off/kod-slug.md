# kod-slug · puan 1.00

**Not:** 8/8 test

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
    # Türkçe karakter dönüşüm tablosu
    mapping = {
        'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
        'Ç': 'c', 'Ğ': 'g', 'I': 'i', 'İ': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'
    }
    
    # Karakterleri değiştir ve küçük harfe çevir
    for tr_char, en_char in mapping.items():
        text = text.replace(tr_char, en_char)
    
    text = text.lower()
    
    # Harf ve rakam dışındaki karakter dizilerini '-' ile değiştir
    text = re.sub(r'[^a-z0-9]+', '-', text)
    
    # Baştaki ve sondaki '-' işaretlerini temizle
    return text.strip('-')
```

## Notlandırılan kod/komut

```
import re

def tr_slug(text: str) -> str:
    # Türkçe karakter dönüşüm tablosu
    mapping = {
        'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
        'Ç': 'c', 'Ğ': 'g', 'I': 'i', 'İ': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'
    }
    
    # Karakterleri değiştir ve küçük harfe çevir
    for tr_char, en_char in mapping.items():
        text = text.replace(tr_char, en_char)
    
    text = text.lower()
    
    # Harf ve rakam dışındaki karakter dizilerini '-' ile değiştir
    text = re.sub(r'[^a-z0-9]+', '-', text)
    
    # Baştaki ve sondaki '-' işaretlerini temizle
    return text.strip('-')
```
