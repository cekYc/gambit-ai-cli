# Umay sonuçları: önceki koşular (9 Kasım 2026)

Güncel sonuçlar [`../results-umay`](../results-umay) klasöründe (9 Kasım 22:10 – 10 Kasım 01:10). Bu klasörde, aynı yapılandırmaların o gece yeniden koşturulmadan önceki sonuçları saklanıyor; [Umay CLI · KIYASLAMA.md](https://github.com/Umay-Official/Umay-CLI/blob/main/docs/KIYASLAMA.md) içindeki "Önceki koşular" tablosu bunlara dayanır.

| Klasör adı | Model | Düşünme | Genel puan | Ne zaman | Fark |
| --- | --- | --- | --- | --- | --- |
| `umay-ultra-hizli__dusunme` | Umay Ultra Hızlı | açık | 52,1 | 9 Kasım sabahı | Ultra Hızlı'nın arkasındaki model akşama doğru değişti |
| `umay-ultra-hizli__kapali` | Umay Ultra Hızlı | kapalı | 73,7 | 9 Kasım sabahı | Aynı |
| `umay-daha-zeki__dusunme` | Umay Daha Zeki | açık | 47,9 | 9 Kasım akşamı | Güncel koşuyla aynı model; araç çağrısı onarımı olmadan |
| `umay-daha-zeki__kapali` | Umay Daha Zeki | kapalı | 40,4 | 9 Kasım akşamı | Aynı |

- **Ultra Hızlı (sabah):** Görev başına süre sınırı yoktu. Umay sunucusu her isteği yaklaşık 180 saniyede kesiyor; düşünme açıkken 14 sıfırın 10'u bu kesmeden (`crash` alanında "context deadline exceeded").
- **Daha Zeki (akşam, onarımsız):** Model araçları metin içinde `<tool_call>` bloklarıyla çağırıyor ve uzun bir dosya içeriğinden sonra JSON'un sonunu sık sık bozuyor. O sırada Umay CLI bu çağrıları okuyamıyordu; ilgili görevlerde dosya hiç yazılmadı. Aynı model onarımlı CLI ile 71,3 ve 52,4 aldı.
- Umay Akıllı ve Umay Hızlı'nın 8 Kasım sonuçları (87,6, 83,2, 65,2, 81,4, 79,4, 68,7) bu depoda `6c59ad2` commit'indeki `results-umay` klasöründe (görev klasörleriyle birlikte).

Klasör düzeni [`../results-umay`](../results-umay) ile aynıdır: `results.jsonl`, `responses/<yapılandırma>/<görev>.json`, `sandboxes/<yapılandırma>/<görev>/`, ve Gambit'in rapor biçiminde [`RAPOR.md`](RAPOR.md), [`rapor.html`](rapor.html), [`sonuclar.csv`](sonuclar.csv).
