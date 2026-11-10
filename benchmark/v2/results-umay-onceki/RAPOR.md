# Gambit Bench v2 sonuçları

_Güncelleme: 2026-11-10 08:25 · 39 görev · toplam ağırlık 116 · her görev gambit-cli'nin ajan döngüsüyle (sistem istemi, araçlar, düşünme modu) çalıştırıldı._

**Genel puan zorluk ağırlıklıdır** (kolay ×1, orta ×2, zor ×3, çok zor ×4); her görev rubrikle kısmi puan alır.

## Sıralama

| # | Yapılandırma | Model | Genel (ağırlıklı) | Basit ort. | Zor+ görevler | Tam puan / sıfır | Süre (dk) | Token (bin) | Düşünülen adım | Süre aşımı | Görev |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **umay-ultra-hizli · düşünme kapalı** | umay-ultra-hizli | **73,7** | 72,8 | 74,9 | 15 / 2 | 209 | 0,0 | 0/272 | 0 | 39/39 |
| 2 | **umay-ultra-hizli · düşünme açık** | umay-ultra-hizli | **52,1** | 55,6 | 47,5 | 12 / 14 | 101 | 0,0 | 202/202 | 0 | 39/39 |
| 3 | **umay-daha-zeki · düşünme açık** | umay-daha-zeki | **47,9** | 49,9 | 44,1 | 3 / 8 | 55 | 0,0 | 226/226 | 0 | 39/39 |
| 4 | **umay-daha-zeki · düşünme kapalı** | umay-daha-zeki | **40,4** | 43,0 | 36,8 | 6 / 12 | 20 | 0,0 | 0/193 | 0 | 39/39 |

## Kategoriler (kategori içinde ağırlıklı)

| Yapılandırma | Kod yazma | Hata ayıklama | Kod okuma | SQL | Terminal | Ajan | Mantık | Talimat | Kod inceleme |
|---|---|---|---|---|---|---|---|---|---|
| umay-ultra-hizli · düşünme kapalı | 71 | 59 | 88 | 72 | 67 | 45 | 100 | 97 | 83 |
| umay-ultra-hizli · düşünme açık | 39 | 91 | 36 | 31 | 45 | 32 | 100 | 94 | 69 |
| umay-daha-zeki · düşünme açık | 31 | 37 | 39 | 41 | 18 | 65 | 87 | 95 | 77 |
| umay-daha-zeki · düşünme kapalı | 16 | 38 | 41 | 34 | 37 | 21 | 90 | 82 | 79 |

## Görevler

| Görev | Kategori | Seviye (ağırlık) | umay-ultra-hizli · düşünme kapalı | umay-ultra-hizli · düşünme açık | umay-daha-zeki · düşünme açık | umay-daha-zeki · düşünme kapalı |
|---|---|---|---|---|---|---|
| kod-semver — SemVer 2.0 karşılaştırma | Kod yazma | zor (×3) | 85 | 0 | 0 | 0 |
| kod-yorumlayici — Mini dil yorumlayıcısı | Kod yazma | çok zor (×4) | 24 | 0 | 18 | 18 |
| kod-csv — CSV ayrıştırıcı (RFC 4180) | Kod yazma | zor (×3) | 19 | 0 | 0 | 0 |
| kod-bagimlilik — Bağımlılık sırası ve döngü | Kod yazma | zor (×3) | 95 | 95 | 32 | 38 |
| kod-kova-js — Token bucket hız sınırlayıcı (JS) | Kod yazma | zor (×3) | 100 | 0 | 55 | 55 |
| kod-turkce — Türkçe harf ve sıralama | Kod yazma | orta (×2) | 95 | 95 | 0 | 0 |
| kod-fark — Minimal satır farkı (diff) | Kod yazma | çok zor (×4) | 95 | 95 | 87 | 0 |
| hata-envanter — Stok modülü (5 hata) | Hata ayıklama | orta (×2) | 28 | 94 | 94 | 80 |
| hata-tarih — Tarih yardımcıları (4 hata) | Hata ayıklama | zor (×3) | 32 | 76 | 32 | 0 |
| hata-async-js — Async JS yardımcıları (4 hata) | Hata ayıklama | zor (×3) | 100 | 100 | 53 | 0 |
| hata-onbellek — Önbellek dekoratörü (6 hata) | Hata ayıklama | çok zor (×4) | 65 | 95 | 0 | 73 |
| okuma-mro — Çoklu kalıtım ve super() | Kod okuma | zor (×3) | 100 | 100 | 35 | 64 |
| okuma-uretec — Üreteçler, send ve yield from | Kod okuma | çok zor (×4) | 100 | 0 | 38 | 42 |
| okuma-dekorator — Dekoratör sırası ve geç bağlama | Kod okuma | zor (×3) | 100 | 0 | 57 | 39 |
| okuma-asyncio — asyncio görev sırası | Kod okuma | çok zor (×4) | 66 | 0 | 30 | 31 |
| okuma-js-this — this, kapsam ve hoisting (JS) | Kod okuma | zor (×3) | 74 | 71 | 29 | 46 |
| okuma-js-tip — Tür dönüşümleri (JS) | Kod okuma | orta (×2) | 91 | 81 | 57 | 21 |
| sql-sehir-ciro — Şehir cirosu (sıfırlar dahil) | SQL | orta (×2) | 26 | 100 | 69 | 100 |
| sql-net-satis — İade düşülmüş net satış | SQL | zor (×3) | 0 | 100 | 0 | 100 |
| sql-kategori-pay — Kategori payı ve sıralama | SQL | zor (×3) | 100 | 0 | 28 | 15 |
| sql-ardisik-ay — Ardışık aylar (gaps & islands) | SQL | çok zor (×4) | 100 | 0 | 67 | 0 |
| sql-medyan — Şehir bazında medyan sipariş | SQL | çok zor (×4) | 100 | 0 | 44 | 0 |
| term-log-rapor — Log seviyelerini sayıp CSV rapor | Terminal | orta (×2) | 86 | 100 | 82 | 100 |
| term-arsiv — Fotoğrafları tarihe göre arşivleme | Terminal | zor (×3) | 0 | 0 | 0 | 0 |
| term-ini — INI dosyalarında bölüme özel değişiklik | Terminal | zor (×3) | 100 | 0 | 0 | 70 |
| term-kopyalar — İçeriği aynı dosyaları bulma | Terminal | zor (×3) | 89 | 100 | 11 | 0 |
| ajan-kutuphane — Projeye gecikme cezası özelliği ekleme | Ajan | zor (×3) | 1 | 1 | 91 | 89 |
| ajan-yeniden-adlandir — Kod tabanında güvenli yeniden adlandırma | Ajan | zor (×3) | 76 | 100 | 81 | 2 |
| ajan-veri-temizle — Dağınık JSONL verisini temizleyip özetleme | Ajan | zor (×3) | 64 | 0 | 81 | 0 |
| ajan-hata-izi — Hatanın kaynağını bulup düzeltme | Ajan | zor (×3) | 63 | 47 | 0 | 0 |
| ajan-api-belgesi — Kaynaktan API belgesi çıkarma | Ajan | orta (×2) | 10 | 0 | 77 | 9 |
| mantik-olasilik — Olasılık ve kombinatorik | Mantık | zor (×3) | 100 | 100 | 78 | 69 |
| mantik-algoritma — Algoritma analizi | Mantık | zor (×3) | 100 | 100 | 82 | 100 |
| mantik-bulmaca — Mantık bulmacası | Mantık | zor (×3) | 100 | 100 | 100 | 100 |
| talimat-cikarim — E-postadan yapılandırılmış veri | Talimat | orta (×2) | 100 | 100 | 100 | 92 |
| talimat-kisitli-metin — Çok kısıtlı tanıtım metni | Talimat | zor (×3) | 100 | 100 | 95 | 64 |
| talimat-commit — Kurallara uygun commit mesajı | Talimat | orta (×2) | 90 | 80 | 90 | 100 |
| inceleme-guvenlik — Güvenlik açıklarını bulma (Python) | Kod inceleme | zor (×3) | 100 | 86 | 100 | 86 |
| inceleme-mantik-js — Mantık hatalarını bulma (JS) | Kod inceleme | zor (×3) | 66 | 52 | 53 | 71 |

## Notlar

- Puanlar 0–100. Her görevin puanı rubrik maddelerinin ağırlıklı ortalamasıdır (gizli testler, dosya durumu, biçim kuralları, satır satır çıktı benzerliği vb.); yanlış dosya adı, test dosyasını değiştirme gibi durumlar çarpan cezası alır.
- Kod/SQL görevleri gizli testlerle (SQL ayrıca farklı verili gizli bir veritabanında) puanlanır.
- Düşünülen adım: düşünmenin açık olduğu model çağrısı / toplam çağrı (otomatik modda gambit'in kendi kuralı).
- Ayrıntılı notlar ve her görevin tam dökümü: `responses/<model>__<mod>/<görev>.json` ve `.log`.
