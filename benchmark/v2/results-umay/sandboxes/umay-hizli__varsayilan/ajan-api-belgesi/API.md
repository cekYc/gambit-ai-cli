# API Dokümanı

## paket.metin

- `AYIRICI = "-"` — Ayrıcı sabidi.
- `kisalt(metin: str, uzunluk: int = 20, son: str = "…") -> str` — Metni verilen uzunluğa kısaltır.
- `kelime_say(metin) -> int` — Metindeki kelime sayısını döndürür.
- `baslik(metin: str, *, kucuk_kelimeler=('ve', 'ile')) -> str` — Her kelimenin ilk harfini büyütür (bağlaçlar hariç).
- `Sablon` — Basit metin şablonu.
- `Sablon.doldur(self, **degerler) -> str` — Şablondaki {ad} alanlarını doldurur.

## paket.sayi

- `yuvarla(x: float, basamak: int = 2) -> float` — Yarımları yukarı yuvarlar.
- `ortalama(*sayilar, bos=0) -> float` — Sayıların ortalaması; sayı yoksa bos döner.
- `async topla_async(a, b) -> int` — Asenkron toplama.

## paket.__init__

- Boş veya sadece dize sabiti içerir; genel kod veya sabit bulunamadı.
