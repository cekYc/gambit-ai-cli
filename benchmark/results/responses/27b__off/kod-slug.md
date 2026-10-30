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
    # Türkçe karakter haritası (büyük ve küçük harfler dahil)
    turkish_map = {
        'ç': 'c', 'Ç': 'c',
        'ğ': 'g', 'Ğ': 'g',
        'ı': 'i', 'İ': 'i',
        'ö': 'o', 'Ö': 'o',
        'ş': 's', 'Ş': 's',
        'ü': 'u', 'Ü': 'u',
    }

    # Türkçe karakterleri yerine koy
    for old, new in turkish_map.items():
        text = text.replace(old, new)

    # Tamamen küçük harfe çevir
    text = text.lower()

    # Harf ve rakam dışındaki her karakter dizisini tek '-' ile değiştir
    text = re.sub(r'[^a-z0-9]+', '-', text)

    # Baştaki ve sondaki '-' karakterlerini sil
    text = text.strip('-')

    return text
```

## Notlandırılan kod/komut

```
import re


def tr_slug(text: str) -> str:
    # Türkçe karakter haritası (büyük ve küçük harfler dahil)
    turkish_map = {
        'ç': 'c', 'Ç': 'c',
        'ğ': 'g', 'Ğ': 'g',
        'ı': 'i', 'İ': 'i',
        'ö': 'o', 'Ö': 'o',
        'ş': 's', 'Ş': 's',
        'ü': 'u', 'Ü': 'u',
    }

    # Türkçe karakterleri yerine koy
    for old, new in turkish_map.items():
        text = text.replace(old, new)

    # Tamamen küçük harfe çevir
    text = text.lower()

    # Harf ve rakam dışındaki her karakter dizisini tek '-' ile değiştir
    text = re.sub(r'[^a-z0-9]+', '-', text)

    # Baştaki ve sondaki '-' karakterlerini sil
    text = text.strip('-')

    return text
```
