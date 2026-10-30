# Gambit CLI

LM Studio'daki yerel modellerle terminalden çalışan asistan. İnternet gerektirmez.
Model dosyaları listeleyip okuyabilir ve içlerinde arama yapabilir. Dosya yazma, düzenleme ve
komut çalıştırma ise her seferinde senin onayınla olur.

## Modeller

CLI'da modeller satranç taşlarının adlarıyla görünür; gerçek model adları ekrana yazılmaz.
Hangi adın hangi modeli yüklediği `config.json`'daki `presets` bölümünde tanımlı.

| Ad | Ne için |
|---|---|
| `knight` | Hafif, çok hızlı ve görsel destekli; günlük pratik işler için (~35 tok/s) |
| `rook` | Kod yazma ve araç kullanımında en seri işçi; düşünmeden üretir (~20 tok/s) |
| `queen` | Varsayılan ana model; her alanda tam puanlı, gerektiğinde düşünür (~17 tok/s) |
| `bishop` | Uzun kod incelemeleri için; yavaş görünür ama lafı uzatmadan çabuk bitirir (~9 tok/s) |
| `king` | Son çare; çok yavaştır ama diğerlerinin tıkandığı en zor işleri çözer (~2,5 tok/s) |

Hepsi 16k bağlam ve tek eşzamanlı tahminle yüklenir; GPU oranları ölçülerek seçildi
(`benchmark/tune_gpu.py`).

## Kurulum

### İnternetsiz (Çevrimdışı) Kurulum:
Depo içerisindeki hazır paketlerle internetsiz kurulum yapmak için:
```powershell
# Proje ana dizinindeyken:
python -m venv ai-cli\.venv
.\ai-cli\.venv\Scripts\python.exe -m pip install --no-index --find-links wheels -r ai-cli\requirements.txt
```

### Standart Kurulum:
```powershell
python -m venv ai-cli\.venv
.\ai-cli\.venv\Scripts\pip install -r ai-cli\requirements.txt
```

## Kullanım

```powershell
.\ai-cli\ai.bat                      # sohbet modu (bulunduğun klasörde çalışır)
.\ai-cli\ai.bat "bu klasörde ne var?" # tek seferlik soru
.\ai-cli\ai.bat -m knight            # yüklü modellerden birini seç (ad ya da adın başı)
.\ai-cli\ai.bat --no-tools           # araçsız, sadece sohbet
.\ai-cli\ai.bat --no-think           # düşünme hep kapalı (--think: hep açık)
.\ai-cli\ai.bat --auto-think         # otomatik düşünme (config.json'daki varsayılan)
.\ai-cli\ai.bat --show-think         # düşünme metnini ekranda göster
```

`ai-cli` klasörünü kullanıcı `PATH` ortam değişkenine eklerseniz her yerden doğrudan `gambit` veya `ai` yazarak çalıştırabilirsiniz (ör. `gambit -m knight`).

LM Studio sunucusu kapalıysa CLI onu kendisi başlatır. Model seçilmezse, yüklü modellerden araç
kullanabilen ilki seçilir.

## Komutlar

| Komut | Ne yapar |
|---|---|
| `/load queen` | Diğer modelleri boşaltır, modeli kendi ayarlarıyla yükler |
| `/model` | Modelleri ve yüklü olup olmadıklarını listeler; `/model <ad>` ile yüklü olana geçer |
| `/unload` | Tüm modelleri boşaltır |
| `/clear` | Yeni sohbet başlatır |
| `/tools` | Araçları açar/kapatır |
| `/think` | Düşünmeyi açar/kapatır; `/think on`, `/think off`, `/think auto` da olur |
| `/show` | Düşünme metnini ekranda gösterir/gizler |
| `/auto` | Onay sormayı açar/kapatır (dikkat) |
| `/exit` | Çıkış |

Alt+Enter yeni satır ekler, Ctrl+C cevabı durdurur, ↑/↓ önceki mesajları getirir.

## Araçlar

| Araç | Onay |
|---|---|
| `list_dir`, `read_file`, `search_files` | gerekmez |
| `write_file`, `edit_file` | gerekir; önce değişiklik farkı gösterilir |
| `run_command` (PowerShell) | gerekir; önce komut gösterilir |

Onay sorusuna `e` (evet), `t` (bu oturumda o araç için hep evet) ya da `h` (hayır) yazabilirsin.
Bunların dışında bir şey yazarsan işlem reddedilir ve yazdığın metin not olarak modele iletilir.

Yeni araç eklemek için `tools.py` içinde bir fonksiyon yazıp `TOOLS` sözlüğüne kaydetmen yeterli.

## Düşünme modları

| Mod | Ne yapar | Ne zaman |
|---|---|---|
| `auto` (varsayılan) | Düşünme kapalı başlar. Mesaj bir analiz sorusuysa (kod ne yazdırır/ne yapar, neden, açıkla, karşılaştır, why, explain...) o tur açılır. Bir komut başarısız olursa (ör. testler geçmezse) turun geri kalanında açılır. Tur bitince yeniden kapanır. | Günlük kullanım |
| `off` | Hiç düşünmez; en hızlısı. | Basit, hızlı işler |
| `on` | Her cevaptan önce düşünür; çok yavaş, küçük modellerde döngüye girebilir. | Zor bir problemi elle zorlamak için |

Otomatik modda düşünme açıldığında ekranda bir satırla belirtilir. Analiz sorusu kalıplarını
`ai.py` içindeki `ANALYSIS_QUESTION` belirler; sorunu farklı kelimelerle soruyorsan ve düşünme
açılmıyorsa `/think on` ile elle açabilir ya da kalıplara ekleme yapabilirsin. Düşünme desteği olmayan
modelde (`rook`) mod bir şey değiştirmez.

Kendi benchmark'ımızda (`benchmark/`, 31 kodlama ve terminal görevi) otomatik mod ölçülen her
modelde en yüksek puanı aldı:

| Model | Kapalı | Otomatik | Açık |
|---|---|---|---|
| `queen` | 94 puan, 10 dk | 100 puan, 20 dk | 94 puan, 69 dk |
| `knight` | 71 puan, 6 dk | 82 puan, 20 dk | 80 puan, 61 dk |
| `rook` (düşünme yok) | 88 puan, 8 dk | — | — |
| `bishop` | — | 71 puan, 13 dk | — |
| `king` | 96 puan, 56 dk | — | — |

## Ayarlar (`config.json`)

- `base_url`: sunucu adresi. Herhangi bir OpenAI uyumlu sunucu olabilir, örneğin llama.cpp `llama-server`.
- `model`: varsayılan model. Boş bırakılırsa yüklü olan kullanılır.
- `temperature`: `null` bırakılırsa LM Studio'nun model ayarı geçerli olur.
- `thinking`: düşünme modu: `"auto"` (varsayılan), `false` (kapalı) ya da `true` (açık). Ayrıntılar
  "Düşünme modları" bölümünde. Düşünme kapalıyken istekle birlikte `reasoning_effort: "none"`
  gönderilir; bu, LM Studio'da Gemma 4 ve Qwen3.5'te düşünmeyi gerçekten kapatır.
- `show_thinking`: düşünme metni ekranda gösterilsin mi. Gizliyken model yine düşünür.
- `presets`: `/load` için modeller. Anahtar CLI'da görünen ad (`queen`), `model` LM Studio'daki model
  kimliği, `args` doğrudan `lms load` komutuna geçirilir, `desc` listelerde görünen açıklama.
