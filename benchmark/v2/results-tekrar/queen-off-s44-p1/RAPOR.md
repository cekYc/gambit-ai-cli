# Gambit Bench v2 sonuçları

_Güncelleme: 2026-11-04 23:11 · 39 görev · toplam ağırlık 116 · her görev gambit-cli'nin ajan döngüsüyle (sistem istemi, araçlar, düşünme modu) çalıştırıldı._

**Genel puan zorluk ağırlıklıdır** (kolay ×1, orta ×2, zor ×3, çok zor ×4); her görev rubrikle kısmi puan alır.

## Sıralama

| # | Yapılandırma | Model | Genel (ağırlıklı) | Basit ort. | Zor+ görevler | Tam puan / sıfır | Süre (dk) | Token (bin) | Düşünülen adım | Süre aşımı | Görev |
|---|---|---|---|---|---|---|---|---|---|---|---|

_Yarım kalan ve sıralamaya alınmayan yapılandırmalar: queen · kapalı (10/39 görev)._

## Kategoriler (kategori içinde ağırlıklı)

| Yapılandırma | Kod yazma | Hata ayıklama | Kod okuma | SQL | Terminal | Ajan | Mantık | Talimat | Kod inceleme |
|---|---|---|---|---|---|---|---|---|---|

## Görevler

| Görev | Kategori | Seviye (ağırlık) |  |
|---|---|---|
| kod-semver — SemVer 2.0 karşılaştırma | Kod yazma | zor (×3) |  |
| kod-yorumlayici — Mini dil yorumlayıcısı | Kod yazma | çok zor (×4) |  |
| kod-csv — CSV ayrıştırıcı (RFC 4180) | Kod yazma | zor (×3) |  |
| kod-bagimlilik — Bağımlılık sırası ve döngü | Kod yazma | zor (×3) |  |
| kod-kova-js — Token bucket hız sınırlayıcı (JS) | Kod yazma | zor (×3) |  |
| kod-turkce — Türkçe harf ve sıralama | Kod yazma | orta (×2) |  |
| kod-fark — Minimal satır farkı (diff) | Kod yazma | çok zor (×4) |  |
| hata-envanter — Stok modülü (5 hata) | Hata ayıklama | orta (×2) |  |
| hata-tarih — Tarih yardımcıları (4 hata) | Hata ayıklama | zor (×3) |  |
| hata-async-js — Async JS yardımcıları (4 hata) | Hata ayıklama | zor (×3) |  |
| hata-onbellek — Önbellek dekoratörü (6 hata) | Hata ayıklama | çok zor (×4) |  |
| okuma-mro — Çoklu kalıtım ve super() | Kod okuma | zor (×3) |  |
| okuma-uretec — Üreteçler, send ve yield from | Kod okuma | çok zor (×4) |  |
| okuma-dekorator — Dekoratör sırası ve geç bağlama | Kod okuma | zor (×3) |  |
| okuma-asyncio — asyncio görev sırası | Kod okuma | çok zor (×4) |  |
| okuma-js-this — this, kapsam ve hoisting (JS) | Kod okuma | zor (×3) |  |
| okuma-js-tip — Tür dönüşümleri (JS) | Kod okuma | orta (×2) |  |
| sql-sehir-ciro — Şehir cirosu (sıfırlar dahil) | SQL | orta (×2) |  |
| sql-net-satis — İade düşülmüş net satış | SQL | zor (×3) |  |
| sql-kategori-pay — Kategori payı ve sıralama | SQL | zor (×3) |  |
| sql-ardisik-ay — Ardışık aylar (gaps & islands) | SQL | çok zor (×4) |  |
| sql-medyan — Şehir bazında medyan sipariş | SQL | çok zor (×4) |  |
| term-log-rapor — Log seviyelerini sayıp CSV rapor | Terminal | orta (×2) |  |
| term-arsiv — Fotoğrafları tarihe göre arşivleme | Terminal | zor (×3) |  |
| term-ini — INI dosyalarında bölüme özel değişiklik | Terminal | zor (×3) |  |
| term-kopyalar — İçeriği aynı dosyaları bulma | Terminal | zor (×3) |  |
| ajan-kutuphane — Projeye gecikme cezası özelliği ekleme | Ajan | zor (×3) |  |
| ajan-yeniden-adlandir — Kod tabanında güvenli yeniden adlandırma | Ajan | zor (×3) |  |
| ajan-veri-temizle — Dağınık JSONL verisini temizleyip özetleme | Ajan | zor (×3) |  |
| ajan-hata-izi — Hatanın kaynağını bulup düzeltme | Ajan | zor (×3) |  |
| ajan-api-belgesi — Kaynaktan API belgesi çıkarma | Ajan | orta (×2) |  |
| mantik-olasilik — Olasılık ve kombinatorik | Mantık | zor (×3) |  |
| mantik-algoritma — Algoritma analizi | Mantık | zor (×3) |  |
| mantik-bulmaca — Mantık bulmacası | Mantık | zor (×3) |  |
| talimat-cikarim — E-postadan yapılandırılmış veri | Talimat | orta (×2) |  |
| talimat-kisitli-metin — Çok kısıtlı tanıtım metni | Talimat | zor (×3) |  |
| talimat-commit — Kurallara uygun commit mesajı | Talimat | orta (×2) |  |
| inceleme-guvenlik — Güvenlik açıklarını bulma (Python) | Kod inceleme | zor (×3) |  |
| inceleme-mantik-js — Mantık hatalarını bulma (JS) | Kod inceleme | zor (×3) |  |

## Notlar

- Puanlar 0–100. Her görevin puanı rubrik maddelerinin ağırlıklı ortalamasıdır (gizli testler, dosya durumu, biçim kuralları, satır satır çıktı benzerliği vb.); yanlış dosya adı, test dosyasını değiştirme gibi durumlar çarpan cezası alır.
- Kod/SQL görevleri gizli testlerle (SQL ayrıca farklı verili gizli bir veritabanında) puanlanır.
- Düşünülen adım: düşünmenin açık olduğu model çağrısı / toplam çağrı (otomatik modda gambit'in kendi kuralı).
- Ayrıntılı notlar ve her görevin tam dökümü: `responses/<model>__<mod>/<görev>.json` ve `.log`.
