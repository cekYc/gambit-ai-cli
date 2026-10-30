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
    # Türkçe harfleri ASCII karşılıklarına çevir (küçük ve büyük halleri dahil)
    translation_table = str.maketrans({
        'ç': 'c', 'Ç': 'C',
        'ğ': 'g', 'Ğ': 'G',
        'ı': 'i', 'İ': 'I',
        'ö': 'o', 'Ö': 'O',
        'ş': 's', 'Ş': 'S',
        'ü': 'u', 'Ü': 'U'
    })
    
    # Türkçe harf dönüşümü yap
    text = text.translate(translation_table)
    
    # Tüm karakterleri küçük harfe çevir
    text = text.lower()
    
    # Harf ve rakam dışındaki tüm karakterleri tek bir '-' ile değiştir
    text = re.sub(r'[^a-z0-9]+', '-', text)
    
    # Baştaki ve sondaki '-' karakterlerini sil
    text = text.strip('-')
    
    return text
```

## Notlandırılan kod/komut

```
import re

def tr_slug(text: str) -> str:
    # Türkçe harfleri ASCII karşılıklarına çevir (küçük ve büyük halleri dahil)
    translation_table = str.maketrans({
        'ç': 'c', 'Ç': 'C',
        'ğ': 'g', 'Ğ': 'G',
        'ı': 'i', 'İ': 'I',
        'ö': 'o', 'Ö': 'O',
        'ş': 's', 'Ş': 'S',
        'ü': 'u', 'Ü': 'U'
    })
    
    # Türkçe harf dönüşümü yap
    text = text.translate(translation_table)
    
    # Tüm karakterleri küçük harfe çevir
    text = text.lower()
    
    # Harf ve rakam dışındaki tüm karakterleri tek bir '-' ile değiştir
    text = re.sub(r'[^a-z0-9]+', '-', text)
    
    # Baştaki ve sondaki '-' karakterlerini sil
    text = text.strip('-')
    
    return text
```
