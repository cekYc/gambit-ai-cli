# kod-slug · puan 0.00

**Not:** 0/8 test; başarısız: S.tr_slug("Merhaba Dünya!") == "merhaba-dunya" -> TypeError('maketrans expected at most 3 arguments, got 4') | S.tr_slug("  İstanbul'da Çay Saati  ") == "istanbul-da-cay-saati" -> TypeError('maketrans expected at most 3 arguments, got 4') | S.tr_slug("ŞEKER  --  ĞÜÖ") == "seker-guo" -> TypeError('maketrans expected at most 3 arguments, got 4') | S.tr_slug("Iğdır ve Ilgın") == "igdir-ve-ilgin" -> T

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

def tr_slug(text):
    translation = str.maketrans(
        "çğışü", "cgisu",
        "ÇĞİÖŞÜ", "CGIOSU"
    )
    text = text.translate(translation).lower()
    text = "".join(c if c.isalnum() else "-" for c in text)
    return re.sub(r"-+", "-", text).strip("-")
```

## Notlandırılan kod/komut

```
import re

def tr_slug(text):
    translation = str.maketrans(
        "çğışü", "cgisu",
        "ÇĞİÖŞÜ", "CGIOSU"
    )
    text = text.translate(translation).lower()
    text = "".join(c if c.isalnum() else "-" for c in text)
    return re.sub(r"-+", "-", text).strip("-")
```
