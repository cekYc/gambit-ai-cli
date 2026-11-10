# Gambit Bench v2 sonuçları

_Güncelleme: 2026-11-10 01:09 · 39 görev · toplam ağırlık 116 · her görev gambit-cli'nin ajan döngüsüyle (sistem istemi, araçlar, düşünme modu) çalıştırıldı._

**Genel puan zorluk ağırlıklıdır** (kolay ×1, orta ×2, zor ×3, çok zor ×4); her görev rubrikle kısmi puan alır.

## Sıralama

| # | Yapılandırma | Model | Genel (ağırlıklı) | Basit ort. | Zor+ görevler | Tam puan / sıfır | Süre (dk) | Token (bin) | Düşünülen adım | Süre aşımı | Görev |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **umay-akilli · düşünme açık** | umay-akilli | **89,4** | 89,4 | 89,1 | 22 / 1 | 47 | 0,0 | 232/232 | 0 | 39/39 |
| 2 | **umay-hizli · düşünme açık** | umay-hizli | **87,2** | 88,4 | 85,6 | 27 / 2 | 46 | 0,0 | 147/147 | 0 | 39/39 |
| 3 | **umay-hizli · düşünme kapalı** | umay-hizli | **73,9** | 74,3 | 73,7 | 13 / 1 | 21 | 0,0 | 0/208 | 0 | 39/39 |
| 4 | **umay-akilli · düşünme alanı gönderilmedi** | umay-akilli | **72,1** | 71,9 | 70,8 | 15 / 7 | 22 | 0,0 | 0/154 | 0 | 39/39 |
| 5 | **umay-daha-zeki · düşünme açık** | umay-daha-zeki | **71,3** | 70,7 | 73,5 | 8 / 2 | 49 | 0,0 | 185/185 | 0 | 39/39 |
| 6 | **umay-akilli · düşünme kapalı** | umay-akilli | **67,5** | 68,0 | 64,8 | 12 / 6 | 17 | 0,0 | 0/151 | 0 | 39/39 |
| 7 | **umay-hizli · düşünme alanı gönderilmedi** | umay-hizli | **64,9** | 66,1 | 63,0 | 9 / 2 | 24 | 0,0 | 0/189 | 0 | 39/39 |
| 8 | **umay-ultra-hizli · düşünme açık** | umay-ultra-hizli | **61,7** | 62,8 | 60,4 | 7 / 3 | 44 | 0,0 | 162/162 | 0 | 39/39 |
| 9 | **umay-daha-zeki · düşünme kapalı** | umay-daha-zeki | **52,4** | 53,4 | 53,6 | 9 / 5 | 24 | 0,0 | 0/199 | 0 | 39/39 |
| 10 | **umay-ultra-hizli · düşünme kapalı** | umay-ultra-hizli | **42,3** | 42,8 | 43,5 | 1 / 6 | 20 | 0,0 | 0/197 | 0 | 39/39 |

## Kategoriler (kategori içinde ağırlıklı)

| Yapılandırma | Kod yazma | Hata ayıklama | Kod okuma | SQL | Terminal | Ajan | Mantık | Talimat | Kod inceleme |
|---|---|---|---|---|---|---|---|---|---|
| umay-akilli · düşünme açık | 95 | 100 | 85 | 86 | 98 | 66 | 96 | 97 | 90 |
| umay-hizli · düşünme açık | 66 | 97 | 91 | 71 | 100 | 100 | 100 | 100 | 90 |
| umay-hizli · düşünme kapalı | 72 | 97 | 49 | 66 | 93 | 74 | 80 | 80 | 80 |
| umay-akilli · düşünme alanı gönderilmedi | 71 | 75 | 72 | 81 | 27 | 70 | 100 | 86 | 77 |
| umay-daha-zeki · düşünme açık | 71 | 89 | 58 | 73 | 60 | 62 | 100 | 64 | 86 |
| umay-akilli · düşünme kapalı | 64 | 72 | 68 | 81 | 45 | 43 | 96 | 72 | 83 |
| umay-hizli · düşünme alanı gönderilmedi | 81 | 62 | 54 | 45 | 73 | 63 | 62 | 88 | 68 |
| umay-ultra-hizli · düşünme açık | 45 | 69 | 52 | 39 | 74 | 81 | 68 | 94 | 83 |
| umay-daha-zeki · düşünme kapalı | 46 | 43 | 37 | 32 | 92 | 26 | 100 | 84 | 79 |
| umay-ultra-hizli · düşünme kapalı | 38 | 5 | 38 | 19 | 38 | 56 | 83 | 79 | 83 |

## Görevler

| Görev | Kategori | Seviye (ağırlık) | umay-akilli · düşünme açık | umay-hizli · düşünme açık | umay-hizli · düşünme kapalı | umay-akilli · düşünme alanı gönderilmedi | umay-daha-zeki · düşünme açık | umay-akilli · düşünme kapalı | umay-hizli · düşünme alanı gönderilmedi | umay-ultra-hizli · düşünme açık | umay-daha-zeki · düşünme kapalı | umay-ultra-hizli · düşünme kapalı |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| kod-semver — SemVer 2.0 karşılaştırma | Kod yazma | zor (×3) | 97 | 97 | 65 | 0 | 77 | 97 | 95 | 92 | 82 | 55 |
| kod-yorumlayici — Mini dil yorumlayıcısı | Kod yazma | çok zor (×4) | 84 | 0 | 60 | 28 | 44 | 86 | 28 | 24 | 10 | 10 |
| kod-csv — CSV ayrıştırıcı (RFC 4180) | Kod yazma | zor (×3) | 96 | 0 | 16 | 96 | 81 | 93 | 93 | 0 | 14 | 0 |
| kod-bagimlilik — Bağımlılık sırası ve döngü | Kod yazma | zor (×3) | 95 | 95 | 95 | 95 | 95 | 27 | 76 | 69 | 76 | 48 |
| kod-kova-js — Token bucket hız sınırlayıcı (JS) | Kod yazma | zor (×3) | 100 | 100 | 100 | 92 | 38 | 96 | 100 | 0 | 100 | 29 |
| kod-turkce — Türkçe harf ve sıralama | Kod yazma | orta (×2) | 95 | 95 | 95 | 95 | 83 | 58 | 95 | 37 | 37 | 21 |
| kod-fark — Minimal satır farkı (diff) | Kod yazma | çok zor (×4) | 100 | 95 | 83 | 100 | 87 | 0 | 95 | 87 | 21 | 87 |
| hata-envanter — Stok modülü (5 hata) | Hata ayıklama | orta (×2) | 100 | 100 | 94 | 100 | 94 | 100 | 42 | 100 | 0 | 0 |
| hata-tarih — Tarih yardımcıları (4 hata) | Hata ayıklama | zor (×3) | 100 | 100 | 100 | 0 | 95 | 0 | 95 | 0 | 32 | 20 |
| hata-async-js — Async JS yardımcıları (4 hata) | Hata ayıklama | zor (×3) | 100 | 100 | 100 | 100 | 100 | 88 | 77 | 100 | 77 | 0 |
| hata-onbellek — Önbellek dekoratörü (6 hata) | Hata ayıklama | çok zor (×4) | 100 | 91 | 95 | 100 | 73 | 100 | 34 | 82 | 47 | 0 |
| okuma-mro — Çoklu kalıtım ve super() | Kod okuma | zor (×3) | 80 | 100 | 34 | 60 | 84 | 60 | 34 | 84 | 64 | 65 |
| okuma-uretec — Üreteçler, send ve yield from | Kod okuma | çok zor (×4) | 100 | 100 | 65 | 100 | 66 | 100 | 71 | 31 | 35 | 31 |
| okuma-dekorator — Dekoratör sırası ve geç bağlama | Kod okuma | zor (×3) | 100 | 100 | 25 | 59 | 70 | 41 | 59 | 86 | 39 | 39 |
| okuma-asyncio — asyncio görev sırası | Kod okuma | çok zor (×4) | 65 | 68 | 68 | 68 | 30 | 68 | 64 | 30 | 29 | 30 |
| okuma-js-this — this, kapsam ve hoisting (JS) | Kod okuma | zor (×3) | 71 | 100 | 43 | 60 | 46 | 60 | 29 | 46 | 32 | 38 |
| okuma-js-tip — Tür dönüşümleri (JS) | Kod okuma | orta (×2) | 100 | 84 | 46 | 82 | 55 | 73 | 56 | 48 | 22 | 22 |
| sql-sehir-ciro — Şehir cirosu (sıfırlar dahil) | SQL | orta (×2) | 100 | 100 | 0 | 100 | 100 | 100 | 69 | 24 | 0 | 0 |
| sql-net-satis — İade düşülmüş net satış | SQL | zor (×3) | 100 | 15 | 100 | 100 | 0 | 100 | 15 | 15 | 0 | 15 |
| sql-kategori-pay — Kategori payı ve sıralama | SQL | zor (×3) | 28 | 28 | 100 | 0 | 100 | 0 | 28 | 23 | 100 | 67 |
| sql-ardisik-ay — Ardışık aylar (gaps & islands) | SQL | çok zor (×4) | 100 | 100 | 15 | 100 | 67 | 100 | 15 | 15 | 0 | 15 |
| sql-medyan — Şehir bazında medyan sipariş | SQL | çok zor (×4) | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 51 | 0 |
| term-log-rapor — Log seviyelerini sayıp CSV rapor | Terminal | orta (×2) | 90 | 100 | 100 | 0 | 41 | 100 | 100 | 82 | 100 | 41 |
| term-arsiv — Fotoğrafları tarihe göre arşivleme | Terminal | zor (×3) | 100 | 100 | 100 | 0 | 42 | 0 | 0 | 42 | 100 | 75 |
| term-ini — INI dosyalarında bölüme özel değişiklik | Terminal | zor (×3) | 100 | 100 | 75 | 100 | 50 | 0 | 100 | 75 | 70 | 25 |
| term-kopyalar — İçeriği aynı dosyaları bulma | Terminal | zor (×3) | 100 | 100 | 100 | 0 | 100 | 100 | 100 | 100 | 100 | 11 |
| ajan-kutuphane — Projeye gecikme cezası özelliği ekleme | Ajan | zor (×3) | 100 | 100 | 96 | 100 | 91 | 1 | 89 | 68 | 89 | 89 |
| ajan-yeniden-adlandir — Kod tabanında güvenli yeniden adlandırma | Ajan | zor (×3) | 95 | 100 | 100 | 95 | 9 | 90 | 100 | 76 | 1 | 90 |
| ajan-veri-temizle — Dağınık JSONL verisini temizleyip özetleme | Ajan | zor (×3) | 0 | 100 | 72 | 72 | 89 | 72 | 72 | 89 | 0 | 50 |
| ajan-hata-izi — Hatanın kaynağını bulup düzeltme | Ajan | zor (×3) | 74 | 100 | 26 | 0 | 95 | 0 | 0 | 95 | 26 | 26 |
| ajan-api-belgesi — Kaynaktan API belgesi çıkarma | Ajan | orta (×2) | 56 | 100 | 77 | 87 | 9 | 56 | 52 | 77 | 9 | 9 |
| mantik-olasilik — Olasılık ve kombinatorik | Mantık | zor (×3) | 100 | 100 | 100 | 100 | 100 | 100 | 44 | 78 | 100 | 67 |
| mantik-algoritma — Algoritma analizi | Mantık | zor (×3) | 88 | 100 | 41 | 100 | 100 | 88 | 41 | 100 | 100 | 82 |
| mantik-bulmaca — Mantık bulmacası | Mantık | zor (×3) | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 25 | 100 | 100 |
| talimat-cikarim — E-postadan yapılandırılmış veri | Talimat | orta (×2) | 100 | 100 | 100 | 100 | 0 | 100 | 100 | 100 | 100 | 92 |
| talimat-kisitli-metin — Çok kısıtlı tanıtım metni | Talimat | zor (×3) | 100 | 100 | 60 | 80 | 95 | 42 | 72 | 93 | 69 | 63 |
| talimat-commit — Kurallara uygun commit mesajı | Talimat | orta (×2) | 90 | 100 | 90 | 80 | 80 | 90 | 100 | 90 | 90 | 90 |
| inceleme-guvenlik — Güvenlik açıklarını bulma (Python) | Kod inceleme | zor (×3) | 100 | 80 | 80 | 86 | 86 | 86 | 80 | 100 | 86 | 86 |
| inceleme-mantik-js — Mantık hatalarını bulma (JS) | Kod inceleme | zor (×3) | 80 | 100 | 80 | 69 | 86 | 80 | 57 | 66 | 71 | 80 |

## Notlar

- Puanlar 0–100. Her görevin puanı rubrik maddelerinin ağırlıklı ortalamasıdır (gizli testler, dosya durumu, biçim kuralları, satır satır çıktı benzerliği vb.); yanlış dosya adı, test dosyasını değiştirme gibi durumlar çarpan cezası alır.
- Kod/SQL görevleri gizli testlerle (SQL ayrıca farklı verili gizli bir veritabanında) puanlanır.
- Düşünülen adım: düşünmenin açık olduğu model çağrısı / toplam çağrı (otomatik modda gambit'in kendi kuralı).
- Ayrıntılı notlar ve her görevin tam dökümü: `responses/<model>__<mod>/<görev>.json` ve `.log`.
