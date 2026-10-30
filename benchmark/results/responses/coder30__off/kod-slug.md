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
def tr_slug(text: str) -> str:
    # Türkçe harf dönüşümü
    turkce_harfler = {
        'Ç': 'c', 'Ğ': 'g', 'I': 'i', 'İ': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u',
        'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u'
    }
    
    # Harf ve rakam dışındaki karakterleri '-' ile değiştir
    result = ""
    for char in text:
        if char.isalnum():
            result += char
        else:
            result += '-'
    
    # Türkçe harfleri dönüştür
    for eski, yeni in turkce_harfler.items():
        result = result.replace(eski, yeni)
    
    # Küçük harfe çevir
    result = result.lower()
    
    # Başındaki ve sonundaki '-' karakterlerini sil
    result = result.strip('-')
    
    # Ardırdan gelen '-' karakterlerini tek '-' yap
    while '--' in result:
        result = result.replace('--', '-')
    
    return result
```

## Notlandırılan kod/komut

```
def tr_slug(text: str) -> str:
    # Türkçe harf dönüşümü
    turkce_harfler = {
        'Ç': 'c', 'Ğ': 'g', 'I': 'i', 'İ': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u',
        'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u'
    }
    
    # Harf ve rakam dışındaki karakterleri '-' ile değiştir
    result = ""
    for char in text:
        if char.isalnum():
            result += char
        else:
            result += '-'
    
    # Türkçe harfleri dönüştür
    for eski, yeni in turkce_harfler.items():
        result = result.replace(eski, yeni)
    
    # Küçük harfe çevir
    result = result.lower()
    
    # Başındaki ve sonundaki '-' karakterlerini sil
    result = result.strip('-')
    
    # Ardırdan gelen '-' karakterlerini tek '-' yap
    while '--' in result:
        result = result.replace('--', '-')
    
    return result
```
