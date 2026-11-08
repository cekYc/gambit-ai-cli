# Gambit Bench v2 sonuçları

_Güncelleme: 2026-11-08 13:34 · 39 görev · toplam ağırlık 116 · her görev gambit-cli'nin ajan döngüsüyle (sistem istemi, araçlar, düşünme modu) çalıştırıldı._

**Genel puan zorluk ağırlıklıdır** (kolay ×1, orta ×2, zor ×3, çok zor ×4); her görev rubrikle kısmi puan alır.

## Sıralama

| # | Yapılandırma | Model | Genel (ağırlıklı) | Basit ort. | Zor+ görevler | Tam puan / sıfır | Süre (dk) | Token (bin) | Düşünülen adım | Süre aşımı | Görev |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **umay-akilli · düşünme açık** | umay-akilli | **87,6** | 88,3 | 86,5 | 21 / 1 | 45 | 0,0 | 234/234 | 0 | 39/39 |
| 2 | **umay-akilli · düşünme alanı gönderilmedi** | umay-akilli | **83,2** | 84,4 | 82,1 | 18 / 1 | 41 | 0,0 | 0/211 | 0 | 39/39 |
| 3 | **umay-hizli · düşünme açık** | umay-hizli | **81,4** | 83,4 | 78,6 | 26 / 5 | 29 | 0,0 | 143/143 | 0 | 39/39 |
| 4 | **umay-hizli · düşünme alanı gönderilmedi** | umay-hizli | **79,4** | 81,4 | 76,4 | 27 / 6 | 29 | 0,0 | 0/151 | 0 | 39/39 |
| 5 | **umay-hizli · düşünme kapalı** | umay-hizli | **68,7** | 69,9 | 66,7 | 11 / 2 | 25 | 0,0 | 0/261 | 1 | 39/39 |
| 6 | **umay-akilli · düşünme kapalı** | umay-akilli | **65,2** | 66,4 | 63,5 | 12 / 7 | 35 | 0,0 | 0/204 | 0 | 39/39 |

## Kategoriler (kategori içinde ağırlıklı)

| Yapılandırma | Kod yazma | Hata ayıklama | Kod okuma | SQL | Terminal | Ajan | Mantık | Talimat | Kod inceleme |
|---|---|---|---|---|---|---|---|---|---|
| umay-akilli · düşünme açık | 85 | 100 | 90 | 86 | 95 | 90 | 96 | 51 | 77 |
| umay-akilli · düşünme alanı gönderilmedi | 68 | 100 | 87 | 86 | 93 | 70 | 96 | 78 | 86 |
| umay-hizli · düşünme açık | 35 | 93 | 100 | 84 | 100 | 76 | 100 | 100 | 90 |
| umay-hizli · düşünme alanı gönderilmedi | 36 | 99 | 93 | 100 | 73 | 62 | 100 | 100 | 100 |
| umay-hizli · düşünme kapalı | 75 | 65 | 57 | 63 | 69 | 62 | 84 | 76 | 90 |
| umay-akilli · düşünme kapalı | 55 | 100 | 68 | 44 | 68 | 28 | 100 | 93 | 80 |

## Görevler

| Görev | Kategori | Seviye (ağırlık) | umay-akilli · düşünme açık | umay-akilli · düşünme alanı gönderilmedi | umay-hizli · düşünme açık | umay-hizli · düşünme alanı gönderilmedi | umay-hizli · düşünme kapalı | umay-akilli · düşünme kapalı |
|---|---|---|---|---|---|---|---|---|
| kod-semver — SemVer 2.0 karşılaştırma | Kod yazma | zor (×3) | 97 | 97 | 95 | 97 | 80 | 97 |
| kod-yorumlayici — Mini dil yorumlayıcısı | Kod yazma | çok zor (×4) | 29 | 21 | 0 | 0 | 86 | 26 |
| kod-csv — CSV ayrıştırıcı (RFC 4180) | Kod yazma | zor (×3) | 96 | 93 | 0 | 0 | 78 | 96 |
| kod-bagimlilik — Bağımlılık sırası ve döngü | Kod yazma | zor (×3) | 95 | 100 | 0 | 0 | 46 | 0 |
| kod-kova-js — Token bucket hız sınırlayıcı (JS) | Kod yazma | zor (×3) | 100 | 96 | 100 | 100 | 96 | 100 |
| kod-turkce — Türkçe harf ve sıralama | Kod yazma | orta (×2) | 100 | 95 | 95 | 95 | 37 | 87 |
| kod-fark — Minimal satır farkı (diff) | Kod yazma | çok zor (×4) | 95 | 13 | 0 | 0 | 83 | 12 |
| hata-envanter — Stok modülü (5 hata) | Hata ayıklama | orta (×2) | 100 | 100 | 100 | 100 | 94 | 100 |
| hata-tarih — Tarih yardımcıları (4 hata) | Hata ayıklama | zor (×3) | 100 | 100 | 100 | 95 | 95 | 100 |
| hata-async-js — Async JS yardımcıları (4 hata) | Hata ayıklama | zor (×3) | 100 | 100 | 100 | 100 | 100 | 100 |
| hata-onbellek — Önbellek dekoratörü (6 hata) | Hata ayıklama | çok zor (×4) | 100 | 100 | 78 | 100 | 0 | 100 |
| okuma-mro — Çoklu kalıtım ve super() | Kod okuma | zor (×3) | 80 | 80 | 100 | 100 | 47 | 47 |
| okuma-uretec — Üreteçler, send ve yield from | Kod okuma | çok zor (×4) | 100 | 100 | 100 | 100 | 78 | 89 |
| okuma-dekorator — Dekoratör sırası ve geç bağlama | Kod okuma | zor (×3) | 100 | 100 | 100 | 100 | 53 | 69 |
| okuma-asyncio — asyncio görev sırası | Kod okuma | çok zor (×4) | 68 | 68 | 100 | 68 | 67 | 68 |
| okuma-js-this — this, kapsam ve hoisting (JS) | Kod okuma | zor (×3) | 100 | 86 | 100 | 100 | 29 | 51 |
| okuma-js-tip — Tür dönüşümleri (JS) | Kod okuma | orta (×2) | 100 | 91 | 100 | 100 | 54 | 82 |
| sql-sehir-ciro — Şehir cirosu (sıfırlar dahil) | SQL | orta (×2) | 100 | 100 | 100 | 100 | 100 | 0 |
| sql-net-satis — İade düşülmüş net satış | SQL | zor (×3) | 100 | 100 | 15 | 100 | 100 | 100 |
| sql-kategori-pay — Kategori payı ve sıralama | SQL | zor (×3) | 28 | 28 | 100 | 100 | 15 | 0 |
| sql-ardisik-ay — Ardışık aylar (gaps & islands) | SQL | çok zor (×4) | 100 | 100 | 100 | 100 | 15 | 0 |
| sql-medyan — Şehir bazında medyan sipariş | SQL | çok zor (×4) | 100 | 100 | 100 | 100 | 100 | 100 |
| term-log-rapor — Log seviyelerini sayıp CSV rapor | Terminal | orta (×2) | 90 | 90 | 100 | 100 | 77 | 90 |
| term-arsiv — Fotoğrafları tarihe göre arşivleme | Terminal | zor (×3) | 100 | 100 | 100 | 100 | 0 | 0 |
| term-ini — INI dosyalarında bölüme özel değişiklik | Terminal | zor (×3) | 100 | 100 | 100 | 0 | 100 | 100 |
| term-kopyalar — İçeriği aynı dosyaları bulma | Terminal | zor (×3) | 90 | 81 | 100 | 100 | 100 | 90 |
| ajan-kutuphane — Projeye gecikme cezası özelliği ekleme | Ajan | zor (×3) | 100 | 100 | 96 | 100 | 91 | 1 |
| ajan-yeniden-adlandir — Kod tabanında güvenli yeniden adlandırma | Ajan | zor (×3) | 90 | 90 | 95 | 100 | 86 | 90 |
| ajan-veri-temizle — Dağınık JSONL verisini temizleyip özetleme | Ajan | zor (×3) | 74 | 0 | 0 | 0 | 21 | 0 |
| ajan-hata-izi — Hatanın kaynağını bulup düzeltme | Ajan | zor (×3) | 100 | 100 | 100 | 32 | 26 | 0 |
| ajan-api-belgesi — Kaynaktan API belgesi çıkarma | Ajan | orta (×2) | 87 | 56 | 97 | 90 | 100 | 56 |
| mantik-olasilik — Olasılık ve kombinatorik | Mantık | zor (×3) | 100 | 100 | 100 | 100 | 100 | 100 |
| mantik-algoritma — Algoritma analizi | Mantık | zor (×3) | 88 | 88 | 100 | 100 | 53 | 100 |
| mantik-bulmaca — Mantık bulmacası | Mantık | zor (×3) | 100 | 100 | 100 | 100 | 100 | 100 |
| talimat-cikarim — E-postadan yapılandırılmış veri | Talimat | orta (×2) | 100 | 100 | 100 | 100 | 100 | 100 |
| talimat-kisitli-metin — Çok kısıtlı tanıtım metni | Talimat | zor (×3) | 0 | 56 | 100 | 100 | 55 | 91 |
| talimat-commit — Kurallara uygun commit mesajı | Talimat | orta (×2) | 80 | 90 | 100 | 100 | 85 | 90 |
| inceleme-guvenlik — Güvenlik açıklarını bulma (Python) | Kod inceleme | zor (×3) | 80 | 93 | 80 | 100 | 80 | 86 |
| inceleme-mantik-js — Mantık hatalarını bulma (JS) | Kod inceleme | zor (×3) | 74 | 80 | 100 | 100 | 100 | 74 |

## Notlar

- Puanlar 0–100. Her görevin puanı rubrik maddelerinin ağırlıklı ortalamasıdır (gizli testler, dosya durumu, biçim kuralları, satır satır çıktı benzerliği vb.); yanlış dosya adı, test dosyasını değiştirme gibi durumlar çarpan cezası alır.
- Kod/SQL görevleri gizli testlerle (SQL ayrıca farklı verili gizli bir veritabanında) puanlanır.
- Düşünülen adım: düşünmenin açık olduğu model çağrısı / toplam çağrı (otomatik modda gambit'in kendi kuralı).
- Ayrıntılı notlar ve her görevin tam dökümü: `responses/<model>__<mod>/<görev>.json` ve `.log`.
