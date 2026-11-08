# Umay sonuçları: Gambit Bench v2

Umay Akıllı ve Umay Hızlı'nın, [Umay CLI](https://github.com/Umay-Official/Umay-CLI) ajanıyla Gambit Bench v2'nin 39 görevinde koşturulduğu sonuçlar (8 Kasım 2026). Özet, grafikler ve koşullar: [Umay CLI · KIYASLAMA.md](https://github.com/Umay-Official/Umay-CLI/blob/main/docs/KIYASLAMA.md).

## Yapılandırmalar

| Klasör adı | Model | Düşünme | Genel puan |
| --- | --- | --- | --- |
| `umay-akilli__dusunme` | Umay Akıllı | açık (`enable_thinking: true`) | 87,6 |
| `umay-akilli__varsayilan` | Umay Akıllı | alan gönderilmedi, Umay karar verdi | 83,2 |
| `umay-akilli__kapali` | Umay Akıllı | kapalı (`enable_thinking: false`) | 65,2 |
| `umay-hizli__dusunme` | Umay Hızlı | açık | 81,4 |
| `umay-hizli__varsayilan` | Umay Hızlı | alan gönderilmedi | 79,4 |
| `umay-hizli__kapali` | Umay Hızlı | kapalı | 68,7 |

## Ne nerede

- **[`sandboxes/<yapılandırma>/<görev>/`](sandboxes):** Görev bittiğinde çalışma klasörünün son hali; Umay'ın yazdığı ve düzenlediği dosyalar burada. Örnek: [`sandboxes/umay-akilli__dusunme/kod-semver/semver.py`](sandboxes/umay-akilli__dusunme/kod-semver/semver.py). SQL görevlerinin veritabanı dosyaları (`*.db`) görev verisi olduğu için depoda yok.
- **[`responses/<yapılandırma>/<görev>.json`](responses):** Modelin son cevabı, her araç çağrısı (okunan/yazılan dosya, çalıştırılan komut ve sonucu) ve puanın rubrik ayrıntısı.
- **`responses/<yapılandırma>/<görev>.log`:** Ekran çıktısı; düşünceler, araç olayları ve yanıt metni.
- **[`RAPOR.md`](RAPOR.md), [`rapor.html`](rapor.html), [`sonuclar.csv`](sonuclar.csv):** Gambit'in rapor biçiminde sıralama, kategori ve görev tabloları.
- **[`results.jsonl`](results.jsonl):** Görev başına sonuç; puan, süre, adım ve araç sayısı, notlar.

Görevlerin tanımı ve notlandırıcılar: [`../gorevler`](../gorevler), [`../core.py`](../core.py). Koşucu: [`../umay_kos.py`](../umay_kos.py) ve [`../umay_ajan.mjs`](../umay_ajan.mjs).

## Notlar

- Görev puanları rubrikle verilir (gizli testler, dosya durumu, SQL sonuç karşılaştırması); genel puan zorluk ağırlıklıdır.
- Sıfır puanlı görevlerin çoğunda Umay'ın yanıtı cevaba ya da araç çağrısına gelmeden sunucu tarafında kesildi; ilgili `.log` dosyası uzun bir düşünceyle biter.
- Onay gerektiren işlemler "yalnızca görev klasörü" kuralıyla otomatik yanıtlandı; klasör dışına yazma ve bazı komutlar engellendi (sonuçtaki `notes` alanı).
