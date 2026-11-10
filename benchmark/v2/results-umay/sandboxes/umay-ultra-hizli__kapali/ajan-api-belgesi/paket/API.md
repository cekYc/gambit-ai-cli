## paket.metin
- kisalt(metin: str, uzunluk: int = 20, son: str = "…") -> str — Metni verilen uzunluğa kısaltır.
- kelime_say(metin) — Metindeki kelime sayısını döndürür.
- baslik(metin: str, kucuk_kelimeler: list[str] = ["ve", "ile"]) -> str — Her kelimenin ilk harfini büyütür (bağlaçlar hariç).
- class Sablon — Basit metin şablonu.
  Sablon.doldur(degerler: dict) -> str — Şablondaki {ad} alanlarını doldurur.

## paket.sayi
- yuvarla(x: float, basamak: int = 2) -> float — Yarımları yukarı yuvarlar.
- ortalama(*sayilar, bos: int = 0) -> float — Sayıların ortalaması; sayı yoksa bos döner.
- async topla_async(a, b) -> int — Asenkron toplama.