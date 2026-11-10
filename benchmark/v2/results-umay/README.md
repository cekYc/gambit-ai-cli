# Umay sonuçları: Gambit Bench v2

Umay Akıllı, Umay Hızlı, Umay Ultra Hızlı ve Umay Daha Zeki'nin [Umay CLI](https://github.com/Umay-Official/Umay-CLI) ajanıyla Gambit Bench v2'nin 39 görevinde koşturulduğu sonuçlar (9 Kasım 2026 22:10 – 10 Kasım 01:10, görev başına süre sınırı yok). Özet, grafikler, önceki koşularla karşılaştırma ve koşullar: [Umay CLI · KIYASLAMA.md](https://github.com/Umay-Official/Umay-CLI/blob/main/docs/KIYASLAMA.md).

## Yapılandırmalar

| Klasör adı | Model | Düşünme | Genel puan |
| --- | --- | --- | --- |
| `umay-akilli__dusunme` | Umay Akıllı | açık (`enable_thinking: true`) | 89,4 |
| `umay-akilli__varsayilan` | Umay Akıllı | alan gönderilmedi, Umay karar verdi | 72,1 |
| `umay-akilli__kapali` | Umay Akıllı | kapalı (`enable_thinking: false`) | 67,5 |
| `umay-hizli__dusunme` | Umay Hızlı | açık | 87,2 |
| `umay-hizli__varsayilan` | Umay Hızlı | alan gönderilmedi | 64,9 |
| `umay-hizli__kapali` | Umay Hızlı | kapalı | 73,9 |
| `umay-ultra-hizli__dusunme` | Umay Ultra Hızlı | açık | 61,7 |
| `umay-ultra-hizli__kapali` | Umay Ultra Hızlı | kapalı | 42,3 |
| `umay-daha-zeki__dusunme` | Umay Daha Zeki | açık | 71,3 |
| `umay-daha-zeki__kapali` | Umay Daha Zeki | kapalı | 52,4 |

## Ne nerede

- **[`sandboxes/<yapılandırma>/<görev>/`](sandboxes):** Görev bittiğinde çalışma klasörünün son hali; Umay'ın yazdığı ve düzenlediği dosyalar burada. Örnek: [`sandboxes/umay-akilli__dusunme/kod-semver/semver.py`](sandboxes/umay-akilli__dusunme/kod-semver/semver.py). SQL görevlerinin veritabanı dosyaları (`*.db`) görev verisi olduğu için depoda yok.
- **[`responses/<yapılandırma>/<görev>.json`](responses):** Modelin son cevabı, her araç çağrısı (okunan/yazılan dosya, çalıştırılan komut ve sonucu) ve puanın rubrik ayrıntısı.
- **`responses/<yapılandırma>/<görev>.log`:** Ekran çıktısı; düşünceler, araç olayları ve yanıt metni.
- **[`umay-yanitlar.html`](umay-yanitlar.html):** Bütün yapılandırmaların cevaplarını görev görev yan yana gösteren sayfa.
- **[`RAPOR.md`](RAPOR.md), [`rapor.html`](rapor.html), [`sonuclar.csv`](sonuclar.csv):** Gambit'in rapor biçiminde sıralama, kategori ve görev tabloları.
- **[`results.jsonl`](results.jsonl):** Görev başına sonuç; puan, süre, adım ve araç sayısı, notlar.

Görevlerin tanımı ve notlandırıcılar: [`../gorevler`](../gorevler), [`../core.py`](../core.py). Koşucu: [`../umay_yeni_modeller.py`](../umay_yeni_modeller.py), [`../umay_kos.py`](../umay_kos.py) ve [`../umay_ajan.mjs`](../umay_ajan.mjs).

## Notlar

- Görev puanları rubrikle verilir (gizli testler, dosya durumu, SQL sonuç karşılaştırması); genel puan zorluk ağırlıklıdır.
- Görev başına süre sınırı yoktu (`time_limit`). Umay sunucusu her isteği yaklaşık 180 saniyede kesiyor; model hiç çıktı vermeden gelen sunucu hataları (boş akış, kopan bağlantı, "servisler yanıt veremiyor") beklenip yeniden denendi, `empty_retries` kaç isteğin yeniden gönderildiğini gösterir. Çıktı başladıktan sonraki kesilmeler sonuç sayıldı (`crash` alanı).
- Umay CLI, sonu bozuk metin araç çağrılarını (eksik ya da yanlış kapanış) onarıyor; 8 ve 9 Kasım'daki önceki koşular bu onarım olmadan yapılmıştı.
- Onay gerektiren işlemler "yalnızca görev klasörü" kuralıyla otomatik yanıtlandı; klasör dışına yazma ve bazı komutlar engellendi (sonuçtaki `notes` alanı).
