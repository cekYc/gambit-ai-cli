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
    # Türkçe özel karakterleri küçük harflerine ve İngilizce karşılıklarına dönüştür
    mapping = {
        'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
        'Ç': 'c', 'Ğ': 'g', 'İ': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'
    }
    
    # Harfleri harf harf dönüştür
    translated_text = ''
    for char in text:
        if char in mapping:
            translated_text += mapping[char]
        else:
            translated_text += char
            
    # Tüm metni küçük harfe çevir (çeviri aşamasında zaten büyükleri de var ama yedek için)
    translated_text = translated_text.lower()
    
    # Harf ve rakam dışındaki her karakteri '-' ile değiştir
    slugified = re.sub(r'[^a-z0-9]+', '-', translated_text)
    
    # Baştaki ve sondaki '-' karakterlerini sil
    slugified = slugified.strip('-')
    
    return slugified
```

## Notlandırılan kod/komut

```
import re

def tr_slug(text: str) -> str:
    # Türkçe özel karakterleri küçük harflerine ve İngilizce karşılıklarına dönüştür
    mapping = {
        'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
        'Ç': 'c', 'Ğ': 'g', 'İ': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'
    }
    
    # Harfleri harf harf dönüştür
    translated_text = ''
    for char in text:
        if char in mapping:
            translated_text += mapping[char]
        else:
            translated_text += char
            
    # Tüm metni küçük harfe çevir (çeviri aşamasında zaten büyükleri de var ama yedek için)
    translated_text = translated_text.lower()
    
    # Harf ve rakam dışındaki her karakteri '-' ile değiştir
    slugified = re.sub(r'[^a-z0-9]+', '-', translated_text)
    
    # Baştaki ve sondaki '-' karakterlerini sil
    slugified = slugified.strip('-')
    
    return slugified
```
