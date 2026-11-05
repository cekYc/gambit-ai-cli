# Gambit Bench v2 sonuçları

_Güncelleme: 2026-11-04 21:33 · 39 görev · toplam ağırlık 116 · her görev gambit-cli'nin ajan döngüsüyle (sistem istemi, araçlar, düşünme modu) çalıştırıldı._

**Genel puan zorluk ağırlıklıdır** (kolay ×1, orta ×2, zor ×3, çok zor ×4); her görev rubrikle kısmi puan alır.

## Sıralama

| # | Yapılandırma | Model | Genel (ağırlıklı) | Basit ort. | Zor+ görevler | Tam puan / sıfır | Süre (dk) | Token (bin) | Düşünülen adım | Süre aşımı | Görev |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **rook · otomatik** | Qwen3-Coder 30B-A3B | **84,8** | 86,0 | 83,4 | 19 / 0 | 23 | 176,7 | 51/273 | 0 | 39/39 |
| 2 | **rook · kapalı** | Qwen3-Coder 30B-A3B | **79,0** | 80,4 | 77,7 | 14 / 1 | 18 | 128,3 | 0/277 | 0 | 39/39 |

## Kategoriler (kategori içinde ağırlıklı)

| Yapılandırma | Kod yazma | Hata ayıklama | Kod okuma | SQL | Terminal | Ajan | Mantık | Talimat | Kod inceleme |
|---|---|---|---|---|---|---|---|---|---|
| rook · otomatik | 70 | 90 | 81 | 100 | 100 | 76 | 100 | 78 | 75 |
| rook · kapalı | 68 | 94 | 81 | 79 | 70 | 90 | 79 | 79 | 76 |

## Görevler

| Görev | Kategori | Seviye (ağırlık) | rook · otomatik | rook · kapalı |
|---|---|---|---|---|
| kod-semver — SemVer 2.0 karşılaştırma | Kod yazma | zor (×3) | 95 | 95 |
| kod-yorumlayici — Mini dil yorumlayıcısı | Kod yazma | çok zor (×4) | 68 | 71 |
| kod-csv — CSV ayrıştırıcı (RFC 4180) | Kod yazma | zor (×3) | 78 | 34 |
| kod-bagimlilik — Bağımlılık sırası ve döngü | Kod yazma | zor (×3) | 61 | 95 |
| kod-kova-js — Token bucket hız sınırlayıcı (JS) | Kod yazma | zor (×3) | 100 | 100 |
| kod-turkce — Türkçe harf ve sıralama | Kod yazma | orta (×2) | 95 | 95 |
| kod-fark — Minimal satır farkı (diff) | Kod yazma | çok zor (×4) | 21 | 12 |
| hata-envanter — Stok modülü (5 hata) | Hata ayıklama | orta (×2) | 94 | 80 |
| hata-tarih — Tarih yardımcıları (4 hata) | Hata ayıklama | zor (×3) | 95 | 95 |
| hata-async-js — Async JS yardımcıları (4 hata) | Hata ayıklama | zor (×3) | 100 | 100 |
| hata-onbellek — Önbellek dekoratörü (6 hata) | Hata ayıklama | çok zor (×4) | 78 | 95 |
| okuma-mro — Çoklu kalıtım ve super() | Kod okuma | zor (×3) | 80 | 80 |
| okuma-uretec — Üreteçler, send ve yield from | Kod okuma | çok zor (×4) | 100 | 100 |
| okuma-dekorator — Dekoratör sırası ve geç bağlama | Kod okuma | zor (×3) | 100 | 88 |
| okuma-asyncio — asyncio görev sırası | Kod okuma | çok zor (×4) | 67 | 68 |
| okuma-js-this — this, kapsam ve hoisting (JS) | Kod okuma | zor (×3) | 71 | 86 |
| okuma-js-tip — Tür dönüşümleri (JS) | Kod okuma | orta (×2) | 63 | 56 |
| sql-sehir-ciro — Şehir cirosu (sıfırlar dahil) | SQL | orta (×2) | 100 | 100 |
| sql-net-satis — İade düşülmüş net satış | SQL | zor (×3) | 100 | 100 |
| sql-kategori-pay — Kategori payı ve sıralama | SQL | zor (×3) | 100 | 100 |
| sql-ardisik-ay — Ardışık aylar (gaps & islands) | SQL | çok zor (×4) | 100 | 15 |
| sql-medyan — Şehir bazında medyan sipariş | SQL | çok zor (×4) | 100 | 100 |
| term-log-rapor — Log seviyelerini sayıp CSV rapor | Terminal | orta (×2) | 100 | 100 |
| term-arsiv — Fotoğrafları tarihe göre arşivleme | Terminal | zor (×3) | 100 | 0 |
| term-ini — INI dosyalarında bölüme özel değişiklik | Terminal | zor (×3) | 100 | 100 |
| term-kopyalar — İçeriği aynı dosyaları bulma | Terminal | zor (×3) | 100 | 89 |
| ajan-kutuphane — Projeye gecikme cezası özelliği ekleme | Ajan | zor (×3) | 96 | 96 |
| ajan-yeniden-adlandir — Kod tabanında güvenli yeniden adlandırma | Ajan | zor (×3) | 90 | 95 |
| ajan-veri-temizle — Dağınık JSONL verisini temizleyip özetleme | Ajan | zor (×3) | 31 | 72 |
| ajan-hata-izi — Hatanın kaynağını bulup düzeltme | Ajan | zor (×3) | 74 | 100 |
| ajan-api-belgesi — Kaynaktan API belgesi çıkarma | Ajan | orta (×2) | 97 | 83 |
| mantik-olasilik — Olasılık ve kombinatorik | Mantık | zor (×3) | 100 | 100 |
| mantik-algoritma — Algoritma analizi | Mantık | zor (×3) | 100 | 38 |
| mantik-bulmaca — Mantık bulmacası | Mantık | zor (×3) | 100 | 100 |
| talimat-cikarim — E-postadan yapılandırılmış veri | Talimat | orta (×2) | 100 | 100 |
| talimat-kisitli-metin — Çok kısıtlı tanıtım metni | Talimat | zor (×3) | 50 | 60 |
| talimat-commit — Kurallara uygun commit mesajı | Talimat | orta (×2) | 100 | 85 |
| inceleme-guvenlik — Güvenlik açıklarını bulma (Python) | Kod inceleme | zor (×3) | 100 | 100 |
| inceleme-mantik-js — Mantık hatalarını bulma (JS) | Kod inceleme | zor (×3) | 49 | 51 |

## Notlar

- Puanlar 0–100. Her görevin puanı rubrik maddelerinin ağırlıklı ortalamasıdır (gizli testler, dosya durumu, biçim kuralları, satır satır çıktı benzerliği vb.); yanlış dosya adı, test dosyasını değiştirme gibi durumlar çarpan cezası alır.
- Kod/SQL görevleri gizli testlerle (SQL ayrıca farklı verili gizli bir veritabanında) puanlanır.
- Düşünülen adım: düşünmenin açık olduğu model çağrısı / toplam çağrı (otomatik modda gambit'in kendi kuralı).
- Ayrıntılı notlar ve her görevin tam dökümü: `responses/<model>__<mod>/<görev>.json` ve `.log`.
