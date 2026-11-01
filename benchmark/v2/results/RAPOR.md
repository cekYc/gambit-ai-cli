# Gambit Bench v2 sonuçları

_Güncelleme: 2026-11-01 12:42 · 39 görev · toplam ağırlık 116 · her görev gambit-cli'nin ajan döngüsüyle (sistem istemi, araçlar, düşünme modu) çalıştırıldı._

**Genel puan zorluk ağırlıklıdır** (kolay ×1, orta ×2, zor ×3, çok zor ×4); her görev rubrikle kısmi puan alır.

## Sıralama

| # | Yapılandırma | Model | Genel (ağırlıklı) | Basit ort. | Zor+ görevler | Tam puan / sıfır | Süre (dk) | Token (bin) | Düşünülen adım | Süre aşımı | Görev |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **queen · kapalı** | Gemma 4 26B-A4B | **58,9** | 62,3 | 56,2 | 8 / 8 | 128 | 66,0 | 0/253 | 8 | 39/39 |
| 2 | **knight · kapalı** | Qwen3.5 9B | **57,3** | 60,4 | 54,5 | 6 / 0 | 77 | 125,9 | 0/301 | 2 | 39/39 |
| 3 | **knight · otomatik** | Qwen3.5 9B | **52,2** | 55,4 | 49,2 | 9 / 7 | 104 | 137,8 | 173/278 | 4 | 39/39 |
| 4 | **rook · kapalı** | Qwen3-Coder 30B-A3B | **51,3** | 53,1 | 49,5 | 4 / 6 | 143 | 52,2 | 0/166 | 9 | 39/39 |
| 5 | **bishop · kapalı** | Gemma 4 12B Coder | **20,5** | 20,8 | 20,7 | 0 / 20 | 46 | 21,7 | 2/50 | 0 | 39/39 |

_Yarım kalan ve sıralamaya alınmayan yapılandırmalar: queen · otomatik (1/39 görev)._

## Kategoriler (kategori içinde ağırlıklı)

| Yapılandırma | Kod yazma | Hata ayıklama | Kod okuma | SQL | Terminal | Ajan | Mantık | Talimat | Kod inceleme |
|---|---|---|---|---|---|---|---|---|---|
| queen · kapalı | 42 | 88 | 56 | 0 | 82 | 63 | 100 | 93 | 73 |
| knight · kapalı | 52 | 62 | 55 | 44 | 56 | 48 | 84 | 89 | 57 |
| knight · otomatik | 37 | 53 | 37 | 50 | 62 | 54 | 81 | 66 | 77 |
| rook · kapalı | 55 | 54 | 43 | 43 | 64 | 45 | 40 | 81 | 60 |
| bishop · kapalı | 14 | 0 | 25 | 0 | 0 | 2 | 61 | 82 | 76 |

## Görevler

| Görev | Kategori | Seviye (ağırlık) | queen · kapalı | knight · kapalı | knight · otomatik | rook · kapalı | bishop · kapalı |
|---|---|---|---|---|---|---|---|
| kod-semver — SemVer 2.0 karşılaştırma | Kod yazma | zor (×3) | 0 | 97 | 43 | 73 | 0 |
| kod-yorumlayici — Mini dil yorumlayıcısı | Kod yazma | çok zor (×4) | 3 | 3 | 3 | 18 | 0 |
| kod-csv — CSV ayrıştırıcı (RFC 4180) | Kod yazma | zor (×3) | 87 | 22 | 16 | 22 | 17 |
| kod-bagimlilik — Bağımlılık sırası ve döngü | Kod yazma | zor (×3) | 58 | 89 | 27 | 24 | 7 |
| kod-kova-js — Token bucket hız sınırlayıcı (JS) | Kod yazma | zor (×3) | 96 | 85 | 92 | 100 | 0 |
| kod-turkce — Türkçe harf ve sıralama | Kod yazma | orta (×2) | 100 | 100 | 100 | 52 | 0 |
| kod-fark — Minimal satır farkı (diff) | Kod yazma | çok zor (×4) | 0 | 12 | 17 | 92 | 57 |
| hata-envanter — Stok modülü (5 hata) | Hata ayıklama | orta (×2) | 100 | 100 | 100 | 86 | 0 |
| hata-tarih — Tarih yardımcıları (4 hata) | Hata ayıklama | zor (×3) | 100 | 52 | 0 | 80 | 0 |
| hata-async-js — Async JS yardımcıları (4 hata) | Hata ayıklama | zor (×3) | 77 | 77 | 65 | 77 | 0 |
| hata-onbellek — Önbellek dekoratörü (6 hata) | Hata ayıklama | çok zor (×4) | 83 | 40 | 61 | 0 | 0 |
| okuma-mro — Çoklu kalıtım ve super() | Kod okuma | zor (×3) | 84 | 67 | 100 | 34 | 34 |
| okuma-uretec — Üreteçler, send ve yield from | Kod okuma | çok zor (×4) | 0 | 56 | 0 | 78 | 48 |
| okuma-dekorator — Dekoratör sırası ve geç bağlama | Kod okuma | zor (×3) | 56 | 71 | 71 | 15 | 17 |
| okuma-asyncio — asyncio görev sırası | Kod okuma | çok zor (×4) | 68 | 29 | 0 | 33 | 4 |
| okuma-js-this — this, kapsam ve hoisting (JS) | Kod okuma | zor (×3) | 81 | 60 | 25 | 34 | 32 |
| okuma-js-tip — Tür dönüşümleri (JS) | Kod okuma | orta (×2) | 65 | 53 | 54 | 58 | 12 |
| sql-sehir-ciro — Şehir cirosu (sıfırlar dahil) | SQL | orta (×2) | 0 | 100 | 0 | 69 | 0 |
| sql-net-satis — İade düşülmüş net satış | SQL | zor (×3) | 0 | 100 | 100 | 100 | 0 |
| sql-kategori-pay — Kategori payı ve sıralama | SQL | zor (×3) | 0 | 28 | 100 | 67 | 0 |
| sql-ardisik-ay — Ardışık aylar (gaps & islands) | SQL | çok zor (×4) | 0 | 15 | 0 | 10 | 0 |
| sql-medyan — Şehir bazında medyan sipariş | SQL | çok zor (×4) | 0 | 15 | 51 | 0 | 0 |
| term-log-rapor — Log seviyelerini sayıp CSV rapor | Terminal | orta (×2) | 59 | 9 | 73 | 50 | 0 |
| term-arsiv — Fotoğrafları tarihe göre arşivleme | Terminal | zor (×3) | 92 | 19 | 0 | 100 | 0 |
| term-ini — INI dosyalarında bölüme özel değişiklik | Terminal | zor (×3) | 70 | 100 | 100 | 0 | 0 |
| term-kopyalar — İçeriği aynı dosyaları bulma | Terminal | zor (×3) | 100 | 81 | 81 | 100 | 0 |
| ajan-kutuphane — Projeye gecikme cezası özelliği ekleme | Ajan | zor (×3) | 89 | 70 | 95 | 89 | 1 |
| ajan-yeniden-adlandir — Kod tabanında güvenli yeniden adlandırma | Ajan | zor (×3) | 71 | 76 | 76 | 90 | 7 |
| ajan-veri-temizle — Dağınık JSONL verisini temizleyip özetleme | Ajan | zor (×3) | 45 | 5 | 0 | 0 | 0 |
| ajan-hata-izi — Hatanın kaynağını bulup düzeltme | Ajan | zor (×3) | 21 | 32 | 47 | 32 | 0 |
| ajan-api-belgesi — Kaynaktan API belgesi çıkarma | Ajan | orta (×2) | 100 | 65 | 48 | 0 | 0 |
| mantik-olasilik — Olasılık ve kombinatorik | Mantık | zor (×3) | 100 | 69 | 61 | 83 | 75 |
| mantik-algoritma — Algoritma analizi | Mantık | zor (×3) | 100 | 82 | 82 | 35 | 41 |
| mantik-bulmaca — Mantık bulmacası | Mantık | zor (×3) | 100 | 100 | 100 | 0 | 67 |
| talimat-cikarim — E-postadan yapılandırılmış veri | Talimat | orta (×2) | 92 | 92 | 100 | 92 | 60 |
| talimat-kisitli-metin — Çok kısıtlı tanıtım metni | Talimat | zor (×3) | 96 | 96 | 28 | 68 | 95 |
| talimat-commit — Kurallara uygun commit mesajı | Talimat | orta (×2) | 90 | 75 | 90 | 90 | 85 |
| inceleme-guvenlik — Güvenlik açıklarını bulma (Python) | Kod inceleme | zor (×3) | 66 | 71 | 100 | 66 | 86 |
| inceleme-mantik-js — Mantık hatalarını bulma (JS) | Kod inceleme | zor (×3) | 80 | 43 | 53 | 53 | 66 |

## Notlar

- Puanlar 0–100. Her görevin puanı rubrik maddelerinin ağırlıklı ortalamasıdır (gizli testler, dosya durumu, biçim kuralları, satır satır çıktı benzerliği vb.); yanlış dosya adı, test dosyasını değiştirme gibi durumlar çarpan cezası alır.
- Kod/SQL görevleri gizli testlerle (SQL ayrıca farklı verili gizli bir veritabanında) puanlanır.
- Düşünülen adım: düşünmenin açık olduğu model çağrısı / toplam çağrı (otomatik modda gambit'in kendi kuralı).
- Ayrıntılı notlar ve her görevin tam dökümü: `responses/<yapılandırma>/<görev>.json` ve `.log`.
