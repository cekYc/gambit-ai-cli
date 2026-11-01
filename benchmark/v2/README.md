# Gambit Bench v2

Yerel modelleri **gambit-cli'nin kendi ajan döngüsüyle** (`ai-cli/ai.py` → `Chat`) sınayan, daha zor ve
kısmi puanlı benchmark. Her görevde model gerçek gambit oturumundaki gibi çalışır: aynı sistem istemi, aynı
araçlar (`read_file`, `list_dir`, `search_files`, `write_file`, `edit_file`, `run_command`/PowerShell) ve aynı
düşünme modu mantığı (`off` / `auto`). Onay soruları bir güvenlik kuralıyla (yalnızca görev klasörü) otomatik yanıtlanır.

## v1'den farkları

| | v1 | v2 |
|---|---|---|
| Çalıştırma | çoğu görev tek API çağrısı | **her görev gambit-cli ajan döngüsü** (araçlı ya da `--no-tools`) |
| Puan | çoğunlukla 0 / 1 | **rubrik**: her görevde 5–20 ağırlıklı madde, kısmi puan |
| Genel puan | görevlerin düz ortalaması | **zorluk ağırlıklı** (kolay ×1, orta ×2, zor ×3, çok zor ×4) |
| Görev sayısı | 31 (6 kategori) | 39 (9 kategori, toplam ağırlık 116) |
| Ezberlemeye karşı | — | gizli testler, SQL için verisi farklı gizli veritabanı, "başka veriyle de doğru mu" kontrolleri |

## Kategoriler

| Kategori | Görev | Nasıl puanlanır |
|---|---|---|
| Kod yazma | 7 (SemVer, mini dil yorumlayıcı, RFC 4180 CSV, bağımlılık sırası, token bucket JS, Türkçe sıralama, minimal diff) | gizli testler (ağırlıklı) + kendi kendini doğrulama |
| Hata ayıklama | 4 (5–6 hatalı modüller, testler hataların bir kısmını yakalıyor) | yalnızca hataları yakalayan gizli testler; özgün kodda zaten geçenler gerileme cezası |
| Kod okuma | 6 (MRO, üreteç/send, dekoratör, asyncio, JS `this`, JS tür dönüşümü) | satır satır çıktı benzerliği |
| SQL | 5 (sıfırlı LEFT JOIN, iade fan-out tuzağı, DENSE_RANK payı, gaps & islands, medyan) | iki veritabanında (biri gizli) sütun + satır F1 + sıra |
| Terminal | 4 (log raporu, fotoğraf arşivi, bölüme özel INI değişikliği + CRLF/BOM, içerik kopyaları) | klasörün son durumu, dosya dosya |
| Ajan | 5 (özellik ekleme, güvenli yeniden adlandırma, dağınık JSONL, hata izi sürme, API belgesi) | gizli testler + dosya durumu + gerileme kontrolleri |
| Mantık | 3 (olasılık, algoritma analizi, bulmaca) | alt soru başına; yakın sayısal cevap yarım puan |
| Talimat | 3 (yapılandırılmış çıkarım, 9 kurallı metin, commit mesajı) | kural başına |
| Kod inceleme | 2 (güvenlik açıkları, JS mantık hataları) | doğru satır ±1 → 0,6, doğru tür → +0,4; yanlış alarm cezası |

## Kullanım

```powershell
python benchmark\v2\run.py --selftest                 # notlandırıcıları sına (model gerekmez)
python benchmark\v2\run.py                            # varsayılan plan (aşağıda)
python benchmark\v2\run.py --plan queen:off,queen:auto
python benchmark\v2\run.py --only kod-,sql-
python benchmark\v2\run.py --regrade                  # kayıtlı çalıştırmaları yeniden puanla
python benchmark\v2\rapor.py                          # raporu yeniden üret
```

Varsayılan plan: önce düşünme kapalı `knight, rook, queen, bishop`, sonra otomatik düşünme `knight, queen, bishop`,
en son `king` (düşünme kapalı; ~2,5 tok/s olduğu için diğer sonuçları bekletmesin diye sona alındı). `rook`
düşünmeyi desteklemediği, `king` de çok yavaş olduğu için otomatik modda çalıştırılmaz.

Sınırlar (tüm modellere aynı): görev başına en fazla 14 model adımı, model çağrısı başına 8192 (kapalı) / 12288
(otomatik) token, görev başına 8 dk (araçlı) / 5 dk (araçsız) süre. `run_command` zaman aşımında süreç ağacının
tamamı kapatılır. Yarıda kalan çalıştırma aynı komutla kaldığı yerden sürer.

## Çıktılar (`results/`)

- `RAPOR.md`, `rapor.html`, `sonuclar.csv`: sıralama, kategori ve görev tabloları (her yapılandırma bitince güncellenir)
- `results.jsonl`: görev başına sonuç (rubrik maddeleri dahil), `configs.jsonl`: yapılandırma olayları
- `responses/<hazır_ayar>__<mod>/<görev>.json|.log`: tam mesaj geçmişi, araç çağrıları, gambit ekran çıktısı
- `sandboxes/`: her görevin çalışma klasörünün son hali (yeniden puanlama için)
- `durum.json`: o an çalışan görev; `BITTI.txt`: tüm plan bitince yazılır
