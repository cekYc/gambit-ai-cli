# Gambit CLI

LM Studio'daki yerel modellerle terminalden çalışan asistan. İnternet gerektirmez.
Model dosyaları listeleyip okuyabilir ve içlerinde arama yapabilir. Dosya yazma, düzenleme ve
komut çalıştırma ise her seferinde senin onayınla olur.

## Modeller

CLI'da modeller satranç taşlarının adlarıyla görünür; gerçek model adları ekrana yazılmaz.
Hangi adın hangi modeli yüklediği `config.json`'daki `presets` bölümünde tanımlı.

| Ad | Ne için |
|---|---|
| `pawn` | En küçük ve en hızlı; kısa, basit işler için (~100 tok/s) |
| `knight` | Küçük akıl yürütme modeli; araçsız, her zaman düşünür; matematik ve mantık soruları için (~50 tok/s) |
| `bishop` | Hafif, çok hızlı ve görsel destekli; günlük pratik işler için (~40 tok/s) |
| `rook` | Kod yazma ve araç kullanımında en seri işçi; düşünmeden üretir (~20 tok/s) |
| `queen` | Varsayılan ana model; her alanda tam puanlı, gerektiğinde düşünür (~17 tok/s) |
| `king` | Son çare; çok yavaştır ama diğerlerinin tıkandığı en zor işleri çözer (~2,5 tok/s) |

Hepsi 16k bağlam ve tek eşzamanlı tahminle yüklenir; GPU oranları ölçülerek seçildi
(`benchmark/tune_gpu.py`). Modeli boş (`"model": ""`) bir hazır ayar boş yuvadır: listede görünür ama
yüklenemez; bir model indirince `config.json`'da ona atanır.

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
.\ai-cli\ai.bat -m bishop            # yüklü modellerden birini seç (ad ya da adın başı)
.\ai-cli\ai.bat --no-tools           # araçsız, sadece sohbet
.\ai-cli\ai.bat --no-think           # düşünme hep kapalı (--think: hep açık)
.\ai-cli\ai.bat --auto-think         # otomatik düşünme (config.json'daki varsayılan)
.\ai-cli\ai.bat --show-think         # düşünme metnini ekranda göster
```

`ai-cli` klasörünü kullanıcı `PATH` ortam değişkenine eklerseniz her yerden doğrudan `gambit` veya `ai` yazarak çalıştırabilirsiniz (ör. `gambit -m bishop`).

LM Studio sunucusu kapalıysa CLI onu kendisi başlatır. Model seçilmezse, yüklü modellerden araç
kullanabilen ilki seçilir.

## Komutlar

| Komut | Ne yapar |
|---|---|
| `/load queen` | Diğer modelleri boşaltır, modeli kendi ayarlarıyla yükler |
| `/model` | Modelleri ve yüklü olup olmadıklarını listeler; `/model <ad>` ile yüklü olana geçer |
| `/unload` | Tüm modelleri boşaltır |
| `/clear` | Yeni sohbet başlatır |
| `/undo` | Modelin yaptığı son dosya değişikliğini geri alır (art arda kullanılabilir) |
| `/compact` | Eski araç çıktılarını kısaltıp bağlamda yer açar (bağlam dolarken bu kendiliğinden de yapılır) |
| `/tools` | Araçları açar/kapatır |
| `/think` | Düşünmeyi açar/kapatır; `/think on`, `/think off`, `/think auto` da olur |
| `/show` | Düşünme metnini ekranda gösterir/gizler |
| `/auto` | Onay sormayı açar/kapatır (dikkat) |
| `/exit` | Çıkış |

Alt+Enter yeni satır ekler, Ctrl+C cevabı durdurur, ↑/↓ önceki mesajları getirir. Sohbet modunda adım
sınırına (`max_steps`) gelinirse devam edilip edilmeyeceği sorulur.

## Görünüm

Cevaplar terminalde Markdown olarak biçimlenir (başlık, liste, tablo, renkli kod blokları); tamamlanan
bloklar kalıcı basılır, yazılmakta olan blok canlı güncellenir. Her modelin bir taşı ve rengi vardır
(♟ pawn, ♞ knight, ♝ bishop, ♜ rook, ♛ queen, ♚ king); açılış logosu, istem, alt çubuk ve bekleme göstergesi bu
rengi kullanır. Bekleme göstergesi ne olduğunu (bağlam işleniyor, düşünüyor · 812 token, write_file
hazırlanıyor · 2.4k karakter, çalışıyor) ve geçen süreyi gösterir; alt çubukta bağlamın doluluğu görünür.
Animasyonları `--no-anim` ya da `"animations": false` kapatır. Çıktı terminal değilse (dosyaya ya da boruya
yazılıyorsa) metin biçimlenmeden olduğu gibi akar.

## Araçlar

| Araç | Onay |
|---|---|
| `list_dir`, `read_file`, `search_files` | gerekmez |
| `write_file`, `edit_file` | gerekir; önce değişiklik farkı gösterilir |
| `run_command` (PowerShell) | gerekir; önce komut gösterilir |
| `run_python` | gerekir; önce kod gösterilir |

- `run_python` Python kodunu kabuktan geçirmeden çalıştırır (kod stdin'den verilir). Küçük modeller
  PowerShell'de `python -c "...\"...\"..."` gibi bash tırnaklaması yazıp aynı hatayı defalarca tekrarlıyordu;
  testler, veri işleme ve SQLite sorguları için bu araç kullanılır. Bulunduğun klasördeki modüller içe aktarılabilir.
- `write_file` ve `edit_file` Python, JavaScript ve JSON dosyalarının sözdizimini yazdıktan hemen sonra
  denetleyip sonucu modele bildirir. 30+ satırlık bir dosya yarısından kısa bir içerikle ezilirse model uyarılır.
- `edit_file` satır sonu boşluk farklarını ve `read_file`'dan kopyalanan satır numaralarını tolere eder;
  metin bulunamazsa dosyada en çok benzeyen kısmı satır numaralarıyla modele gösterir.
- `run_command` zaman aşımında yalnızca kabuğu değil başlattığı tüm süreçleri kapatır. PowerShell bir hatayı
  yazıp yine 0 ile çıkarsa sonuçta bu belirtilir.
- Tek bir araç çıktısı bağlamın en fazla ~%30'u kadar modele gider.

Onay sorusuna `e` (evet), `t` (bu oturumda o araç için hep evet) ya da `h` (hayır) yazabilirsin.
Bunların dışında bir şey yazarsan işlem reddedilir ve yazdığın metin not olarak modele iletilir.

Yeni araç eklemek için `tools.py` içinde bir fonksiyon yazıp `TOOLS` sözlüğüne kaydetmen yeterli.

## Ajan döngüsü korumaları

Yerel modellerin benchmark'ta (`benchmark/v2`) en sık takıldığı durumlar CLI tarafında yakalanır:

| Durum | CLI ne yapar |
|---|---|
| Bağlam doluyor (16k'da uzun görevler araç çağrısını yarıda kesiyordu) | %62'yi geçince eski araç çıktılarını ve dosya içeriklerini kısaltır; son adımlar korunur |
| Araç argümanı bozuk JSON | Kaçırılmamış ters bölü, ham satır sonu ve fazladan karakterleri onarır; onarılamazsa geçmişe `{}` yazar (LM Studio'nun 500 vermemesi için) ve kesildiyse modele parça parça yazmasını söyler |
| Model aracı çağırmak yerine `write_file(...)` gibi metin yazdı | Çalıştırılmadığını söyleyip gerçekten çağırmasını ister |
| "Şimdi testleri çalıştırıyorum:" deyip durdu | Adımı araçla yapmasını ya da özetle bitirmesini ister |
| Hiç araç kullanmadan "oluşturdum, test ettim" dedi | Gerçekten yapmasını ya da yapmadığını söylemesini ister |
| İstenen dosyayı yazmayıp kodu sohbete yapıştırdı | Dosyaya kaydetmesini ister |
| `write_file` çağrısı `path` olmadan geldi (Gemma 4 26B ve Qwen3.8 27B uzun içerikte bunu yapıp aynı çağrıyı tekrarlıyordu) | `path`'i başa yazmasını ister; tekrarlanırsa ve kullanıcı tek bir dosya istediyse içeriği o dosyaya kaydeder ve modele söyler |
| Cevap uzunluk sınırında kesildi | Kaldığı yerden devam etmesini ister |
| Hep düşünen model (`thinking: "always"`) daha cevap yazmadan düşünürken kesildi | Düşüncesinin son kısmını geçmişte tutar ve baştan başlamadan cevabı yazmasını ister |
| Aynı komut aynı hatayla tekrar tekrar başarısız | Sonuca not ekler: PowerShell tırnak hatası, kurulu olmayan program (ör. `sqlite3`), `.schema` gibi SQL olmayan komutlar, "3 kez aynı hata: yöntemi değiştir" |
| Başarısız bir komutu, arada hiçbir dosya ya da komut değişmeden aynen tekrar istedi | Çalıştırmaz; aynı hatayı vereceğini ve önce nedeni düzeltmesini söyler |
| Düşünme uzayıp gidiyor | `think_budget` token'ı aşınca o adım düşünmeden tekrarlanır |
| Tek seferlik modda adım sınırı yaklaşıyor | 5 adım kala testleri kısa tutmasını, son iki adımda bitirmeye odaklanmasını söyler |

Bu uyarılar bir turda en fazla iki kez yapılır; ekranda `↻` ve `↳` ile gösterilir.

## Düşünme modları

| Mod | Ne yapar | Ne zaman |
|---|---|---|
| `auto` (varsayılan) | Düşünme kapalı başlar. Mesaj bir analiz sorusuysa (kod ne yazdırır/ne yapar, neden, açıkla, karşılaştır, why, explain...) o tur açılır; analiz isteyen ama dosya yazdıran/düzelttiren bir görevse (ör. "hatayı düzelt ve nedenini açıkla") yalnızca planlama adımında açılır. Bir komut başarısız olursa (ör. testler geçmezse) bir sonraki adımda açılır. Tur bitince yeniden kapanır. | Günlük kullanım |
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
| `bishop` (o zamanki adıyla `knight`) | 71 puan, 6 dk | 82 puan, 20 dk | 80 puan, 61 dk |
| `rook` (düşünme yok) | 88 puan, 8 dk | — | — |
| `king` | 96 puan, 56 dk | — | — |

## Ayarlar (`config.json`)

- `base_url`: sunucu adresi. Herhangi bir OpenAI uyumlu sunucu olabilir, örneğin llama.cpp `llama-server`.
- `model`: varsayılan model. Boş bırakılırsa yüklü olan kullanılır.
- `temperature`: `null` bırakılırsa LM Studio'nun model ayarı geçerli olur.
- `thinking`: düşünme modu: `"auto"` (varsayılan), `false` (kapalı) ya da `true` (açık). Ayrıntılar
  "Düşünme modları" bölümünde. Düşünme kapalıyken istekle birlikte `reasoning_effort: "none"`
  gönderilir; bu, LM Studio'da Gemma 4 ve Qwen3.5'te düşünmeyi gerçekten kapatır.
- `show_thinking`: düşünme metni ekranda gösterilsin mi. Gizliyken model yine düşünür.
- `think_budget`: bir adımda en fazla kaç token düşünülsün (varsayılan 6144; `0` sınırsız). Aşılırsa adım
  düşünmeden tekrarlanır; küçük modeller aksi halde dakikalarca düşünüp hiç cevap vermeyebiliyor.
- `max_steps`: bir mesaj için en fazla model adımı (varsayılan 25).
- `context_length`: sunucu bağlam uzunluğunu bildirmiyorsa (LM Studio dışı) otomatik kısaltma için kullanılır.
- `animations`, `markdown`: animasyonlar ve Markdown biçimi (varsayılan ikisi de açık).
- `presets`: `/load` için modeller. Anahtar CLI'da görünen ad (`queen`), `model` LM Studio'daki model
  kimliği, `args` doğrudan `lms load` komutuna geçirilir, `desc` listelerde görünen açıklama.
  `"thinking": false` düşünemeyen, `"thinking": "always"` düşünmesi kapatılamayan model içindir (ikisinde de
  düşünme ayarı o modelde bir şey değiştirmez). `"tools": false` araç çağıramayan modelde araçları ve araç
  talimatlarını hiç göndermez; model yalnızca sohbet eder.
