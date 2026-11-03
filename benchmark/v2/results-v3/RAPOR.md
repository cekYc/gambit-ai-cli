# Gambit Bench v2 sonuçları

_Güncelleme: 2026-11-03 05:18 · 39 görev · toplam ağırlık 116 · her görev gambit-cli'nin ajan döngüsüyle (sistem istemi, araçlar, düşünme modu) çalıştırıldı._

**Genel puan zorluk ağırlıklıdır** (kolay ×1, orta ×2, zor ×3, çok zor ×4); her görev rubrikle kısmi puan alır.

## Sıralama

| # | Yapılandırma | Model | Genel (ağırlıklı) | Basit ort. | Zor+ görevler | Tam puan / sıfır | Süre (dk) | Token (bin) | Düşünülen adım | Süre aşımı | Görev |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **queen · kapalı** | Gemma 4 26B-A4B | **63,2** | 65,4 | 62,3 | 11 / 9 | 165 | 87,8 | 0/206 | 10 | 39/39 |
| 2 | **queen · otomatik** | Gemma 4 26B-A4B | **58,8** | 60,6 | 55,4 | 13 / 8 | 214 | 91,8 | 30/181 | 18 | 39/39 |
| 3 | **rook · kapalı** | Qwen3-Coder 30B-A3B | **51,9** | 54,1 | 48,3 | 3 / 4 | 141 | 48,0 | 0/157 | 7 | 39/39 |
| 4 | **king · kapalı** | Qwen3.8 27B | **33,4** | 37,6 | 26,2 | 6 / 14 | 258 | 17,4 | 0/130 | 34 | 39/39 |
| 5 | **bishop · kapalı** | Gemma 4 12B Coder | **20,2** | 20,7 | 19,9 | 0 / 19 | 97 | 38,0 | 3/90 | 3 | 39/39 |
| 6 | **pawn · kapalı** | pawn | **9,5** | 10,8 | 7,2 | 0 / 22 | 34 | 139,8 | 0/317 | 0 | 39/39 |
| 7 | **knight · kapalı** | Qwen3.5 9B | **5,1** | 6,1 | 3,5 | 0 / 31 | 99 | 302,9 | 0/64 | 0 | 39/39 |

## Kategoriler (kategori içinde ağırlıklı)

| Yapılandırma | Kod yazma | Hata ayıklama | Kod okuma | SQL | Terminal | Ajan | Mantık | Talimat | Kod inceleme |
|---|---|---|---|---|---|---|---|---|---|
| queen · kapalı | 51 | 72 | 66 | 35 | 73 | 50 | 100 | 91 | 83 |
| queen · otomatik | 74 | 43 | 22 | 56 | 80 | 61 | 67 | 69 | 90 |
| rook · kapalı | 55 | 74 | 38 | 38 | 59 | 48 | 35 | 81 | 64 |
| king · kapalı | 21 | 86 | 0 | 19 | 82 | 24 | 0 | 77 | 50 |
| bishop · kapalı | 16 | 0 | 31 | 3 | 0 | 2 | 34 | 84 | 76 |
| pawn · kapalı | 6 | 2 | 9 | 0 | 0 | 10 | 23 | 45 | 21 |
| knight · kapalı | 0 | 0 | 0 | 0 | 0 | 2 | 8 | 61 | 10 |

## Görevler

| Görev | Kategori | Seviye (ağırlık) | queen · kapalı | queen · otomatik | rook · kapalı | king · kapalı | bishop · kapalı | pawn · kapalı | knight · kapalı |
|---|---|---|---|---|---|---|---|---|---|
| kod-semver — SemVer 2.0 karşılaştırma | Kod yazma | zor (×3) | 92 | 95 | 57 | 0 | 0 | 37 | 0 |
| kod-yorumlayici — Mini dil yorumlayıcısı | Kod yazma | çok zor (×4) | 0 | 0 | 24 | 0 | 0 | 0 | 0 |
| kod-csv — CSV ayrıştırıcı (RFC 4180) | Kod yazma | zor (×3) | 96 | 96 | 3 | 19 | 22 | 3 | 0 |
| kod-bagimlilik — Bağımlılık sırası ve döngü | Kod yazma | zor (×3) | 88 | 76 | 34 | 0 | 16 | 0 | 0 |
| kod-kova-js — Token bucket hız sınırlayıcı (JS) | Kod yazma | zor (×3) | 100 | 100 | 96 | 96 | 44 | 0 | 0 |
| kod-turkce — Türkçe harf ve sıralama | Kod yazma | orta (×2) | 0 | 95 | 87 | 58 | 0 | 0 | 0 |
| kod-fark — Minimal satır farkı (diff) | Kod yazma | çok zor (×4) | 0 | 83 | 95 | 0 | 25 | 0 | 0 |
| hata-envanter — Stok modülü (5 hata) | Hata ayıklama | orta (×2) | 94 | 94 | 86 | 100 | 0 | 14 | 0 |
| hata-tarih — Tarih yardımcıları (4 hata) | Hata ayıklama | zor (×3) | 100 | 0 | 80 | 75 | 0 | 0 | 0 |
| hata-async-js — Async JS yardımcıları (4 hata) | Hata ayıklama | zor (×3) | 0 | 0 | 77 | 81 | 0 | 0 | 0 |
| hata-onbellek — Önbellek dekoratörü (6 hata) | Hata ayıklama | çok zor (×4) | 95 | 83 | 61 | 91 | 0 | 0 | 0 |
| okuma-mro — Çoklu kalıtım ve super() | Kod okuma | zor (×3) | 64 | 0 | 18 | 0 | 34 | 4 | 0 |
| okuma-uretec — Üreteçler, send ve yield from | Kod okuma | çok zor (×4) | 100 | 100 | 78 | 0 | 39 | 32 | 0 |
| okuma-dekorator — Dekoratör sırası ve geç bağlama | Kod okuma | zor (×3) | 88 | 2 | 15 | 0 | 22 | 0 | 0 |
| okuma-asyncio — asyncio görev sırası | Kod okuma | çok zor (×4) | 30 | 3 | 22 | 0 | 28 | 0 | 0 |
| okuma-js-this — this, kapsam ve hoisting (JS) | Kod okuma | zor (×3) | 43 | 0 | 34 | 1 | 32 | 0 | 0 |
| okuma-js-tip — Tür dönüşümleri (JS) | Kod okuma | orta (×2) | 74 | 0 | 59 | 0 | 24 | 11 | 1 |
| sql-sehir-ciro — Şehir cirosu (sıfırlar dahil) | SQL | orta (×2) | 100 | 100 | 100 | 100 | 0 | 0 | 0 |
| sql-net-satis — İade düşülmüş net satış | SQL | zor (×3) | 100 | 100 | 15 | 15 | 0 | 0 | 0 |
| sql-kategori-pay — Kategori payı ve sıralama | SQL | zor (×3) | 0 | 0 | 100 | 0 | 0 | 0 | 0 |
| sql-ardisik-ay — Ardışık aylar (gaps & islands) | SQL | çok zor (×4) | 0 | 100 | 15 | 15 | 10 | 0 | 0 |
| sql-medyan — Şehir bazında medyan sipariş | SQL | çok zor (×4) | 15 | 0 | 0 | 0 | 0 | 0 | 0 |
| term-log-rapor — Log seviyelerini sayıp CSV rapor | Terminal | orta (×2) | 100 | 100 | 9 | 90 | 0 | 0 | 0 |
| term-arsiv — Fotoğrafları tarihe göre arşivleme | Terminal | zor (×3) | 0 | 100 | 83 | 42 | 0 | 0 | 0 |
| term-ini — INI dosyalarında bölüme özel değişiklik | Terminal | zor (×3) | 100 | 25 | 28 | 100 | 0 | 0 | 0 |
| term-kopyalar — İçeriği aynı dosyaları bulma | Terminal | zor (×3) | 100 | 100 | 100 | 100 | 0 | 0 | 0 |
| ajan-kutuphane — Projeye gecikme cezası özelliği ekleme | Ajan | zor (×3) | 89 | 64 | 79 | 21 | 1 | 1 | 1 |
| ajan-yeniden-adlandir — Kod tabanında güvenli yeniden adlandırma | Ajan | zor (×3) | 71 | 81 | 86 | 9 | 7 | 5 | 7 |
| ajan-veri-temizle — Dağınık JSONL verisini temizleyip özetleme | Ajan | zor (×3) | 72 | 65 | 0 | 0 | 0 | 0 | 0 |
| ajan-hata-izi — Hatanın kaynağını bulup düzeltme | Ajan | zor (×3) | 0 | 42 | 0 | 16 | 0 | 0 | 0 |
| ajan-api-belgesi — Kaynaktan API belgesi çıkarma | Ajan | orta (×2) | 0 | 52 | 90 | 97 | 0 | 60 | 0 |
| mantik-olasilik — Olasılık ve kombinatorik | Mantık | zor (×3) | 100 | 100 | 69 | 0 | 50 | 11 | 0 |
| mantik-algoritma — Algoritma analizi | Mantık | zor (×3) | 100 | 0 | 35 | 0 | 53 | 24 | 0 |
| mantik-bulmaca — Mantık bulmacası | Mantık | zor (×3) | 100 | 100 | 0 | 0 | 0 | 33 | 25 |
| talimat-cikarim — E-postadan yapılandırılmış veri | Talimat | orta (×2) | 92 | 100 | 92 | 100 | 68 | 92 | 84 |
| talimat-kisitli-metin — Çok kısıtlı tanıtım metni | Talimat | zor (×3) | 90 | 28 | 77 | 56 | 94 | 35 | 64 |
| talimat-commit — Kurallara uygun commit mesajı | Talimat | orta (×2) | 90 | 100 | 75 | 85 | 85 | 15 | 35 |
| inceleme-guvenlik — Güvenlik açıklarını bulma (Python) | Kod inceleme | zor (×3) | 86 | 100 | 71 | 100 | 71 | 43 | 0 |
| inceleme-mantik-js — Mantık hatalarını bulma (JS) | Kod inceleme | zor (×3) | 80 | 80 | 57 | 0 | 80 | 0 | 20 |

## Notlar

- Puanlar 0–100. Her görevin puanı rubrik maddelerinin ağırlıklı ortalamasıdır (gizli testler, dosya durumu, biçim kuralları, satır satır çıktı benzerliği vb.); yanlış dosya adı, test dosyasını değiştirme gibi durumlar çarpan cezası alır.
- Kod/SQL görevleri gizli testlerle (SQL ayrıca farklı verili gizli bir veritabanında) puanlanır.
- Düşünülen adım: düşünmenin açık olduğu model çağrısı / toplam çağrı (otomatik modda gambit'in kendi kuralı).
- Ayrıntılı notlar ve her görevin tam dökümü: `responses/<model>__<mod>/<görev>.json` ve `.log`.
