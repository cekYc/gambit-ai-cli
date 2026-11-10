# Umay Paket API Belgeleri

## paket.__init__
- `— Örnek paket.`

## paket.metin
- `AYIRICI — Metin ayıracı sabiti`
- `kisalt(metin: str, uzunluk: int = 20, son: str = "…") -> str — Metni verilen uzunluğa kısaltır.`
- `kelime_say(metin) — Metindeki kelime sayısını döndürür.`
- `_kelimeler(metin) — İç yardımcı.`
- `baslik(metin: str, *, kucuk_kelimeler=("ve", "ile")) -> str — Her kelimenin ilk harfini büyütür (bağlaçlar hariç).`
- `class Sablon — Basit metin şablonu.`
- `Sablon.doldur(self, **degerler) -> str — Şablondaki {ad} alanlarını doldurur.`
- `Sablon._ham() — İçeriği döndürür.`

## paket.sayi
- `yuvarla(x: float, basamak: int = 2) -> float — Yarımları yukarı yuvarlar.`
- `ortalama(*sayilar, bos=0) — Sayıların ortalaması; sayı yoksa bos döner.`
- `async topla_async(a, b) — Asenkron toplama.`
- `_gizli() — Docstring yok.`