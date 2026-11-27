# Gambit CLI

LM Studio'daki yerel modellerle terminalden çalışan asistan. İnternet gerektirmez.
Model dosyaları listeleyip okuyabilir ve içlerinde arama yapabilir. Dosya yazma, düzenleme ve
komut çalıştırma ise her seferinde senin onayınla olur.

## Modeller

CLI'da modeller satranç taşlarının adlarıyla görünür; gerçek model adları ekrana yazılmaz.
Hangi adın hangi modeli yüklediği `config.json`'daki `presets` bölümünde tanımlı.

| Ad | Model | Düşünme düzeyleri | Ne için |
|---|---|---|---|
| `pawn` | Ornith 1.5 9B sansürsüz (IQ4_XS) | off, on | Küçük ve hızlı; kısa, basit işler |
| `knight` | Inkling 2 Mini sansürsüz (AD-IQ3_S) | none, minimal, low, medium, high, xhigh (tamamen kapatılamaz) | Deneme; Bench v2'de Qwen ve Gemma ile karşılaştırılacak |
| `bishop` | Qwen3.5 9B Defiant Fable sansürsüz (Q4_K_M) | off, on | Hafif, hızlı ve görsel destekli; günlük pratik işler |
| `rook` | Qwen3.6 35B A3B heretic (i1-IQ3_S) | off, on | Sansürsüz; kod ve siber güvenlik, MoE olduğu için hızlı |
| `queen` | Gemma 4 26B A4B QAT (Q4_0) | off, on | Varsayılan ana model; her alanda tam puanlı |
| `king` | Ternary Bonsai 2.5 27B (Qwen3.8 27B'nin ternary hâli, Q2_0) | off, medium, xhigh | Zor işler ve ajan görevleri |

Hepsi 16k bağlam ve tek eşzamanlı tahminle yüklenir. GPU oranları bu laptopta gerçek yüklemeyle ölçüldü
(`benchmark/tune_gpu.py --fit all`): her model uzun bir prompt işledikten sonra ekran kartında en az 500 MiB boş
kalacak en yüksek oranda. Ekran kartı ekranı da çizdiği için (`nvidia` grafik modu) bu pay masaüstüne ve tarayıcıya
bırakılır; hibrit moda geçilirse `--fit all --apply` (ve `--fit all --vision --apply`) yeniden çalıştırılmalı.

| Taş | Metin modu: GPU · üretim | Görsel mod: GPU · üretim |
|---|---|---|
| `pawn` | %85 · 29,8 tok/s | %55 · 16,9 tok/s |
| `knight` | ik_llama.cpp · prompt ~97, üretim ~15 tok/s | LM Studio, max (2 blok) · 12,7 tok/s |
| `bishop` | %50 · 14,1 tok/s | %10 · 9,0 tok/s (görsel eki F32, 1,74 GB) |
| `rook` | %25 · 15,0 tok/s | görsel eki yok |
| `queen` | %25 · 22,7 tok/s | %15 · 20,3 tok/s |
| `king` | %50 · 6,2 tok/s | %35 · 4,7 tok/s |

knight (Inkling 2 Mini) metin modunda LM Studio yerine **ik_llama.cpp** ile çalışıyor: aynı dosya, aynı GPU yerleşimi
(bütün katmanlar GPU'da, uzmanların en çok çalışan 4 bloğu GPU'da, kalanı RAM'de), ama prompt okuma LM Studio'daki ~47
yerine ~97 tok/s. Ayrıntı ve ölçümler aşağıda ("Gambit'in başlattığı sunucular") ve YAPILACAKLAR'da. Görsel modu LM
Studio'da (sanal model) kalıyor.

### Gambit'in başlattığı sunucular (ik_llama.cpp)

Hazır ayarda `"server"` alanı olan taş metin modunda LM Studio'ya değil, Gambit'in kendisinin başlattığı bir
`llama-server`'a yüklenir (`servers.py`):

- `/load knight` (ya da `gambit -m knight`) önce LM Studio'daki modelleri boşaltır, sunucuyu ölçülen ayarlarla başlatır
  (RAM bekçisi açık) ve istekleri ona gönderir. Başka bir taş yüklenince, `/vision` ile görsel moda geçince ya da
  `/unload`'da sunucu kapatılır.
- Sunucu Gambit kapandıktan sonra da çalışır (LM Studio'da yüklü kalan model gibi); sonraki açılışta tanınır. PID ve
  günlük `~/.cache/gambit/` altında.
- Sunucu düşünme düzeyini şablona doğrudan iletir: knight'ta `none` ve `minimal` de seçilebilir (sanal model gerekmez).
- Program `~/Desktop/GambitAI/ik_llama.cpp/build/bin/llama-server`; derleme adımları YAPILACAKLAR'da. Yoksa knight LM
  Studio'daki sanal modelle (prompt ~47 tok/s) yüklenir.
Modeli atanmamış bir hazır ayar boş yuvadır: listede görünür ama yüklenemez.

Hazır ayar modeli GGUF dosyasının adıyla (`file`) bulur; LM Studio'daki model anahtarı sistemden sisteme
değişebildiği için anahtar yazılmasa da olur. Model diskte yoksa `/model` listesinde ayrıca gösterilir
(iniyorsa yüzdesiyle), `/load` diğer modelleri boşaltmadan durur ve indirme komutunu söyler.

### Yükleme ve bellek

`/load` modeli şu sırayla yükler:

1. Diğer modelleri boşaltır, `lms load --estimate-only` ile modelin GPU'da ve RAM'de ne kadar yer
   isteyeceğini sorar.
2. Tahmin boş VRAM'e (`nvidia-smi`, `vram_limit_gb` ile sınırlı) ya da boş RAM'e sığmıyorsa uyarır, sığan en
   yüksek GPU oranını (gerekirse 8k bağlamı) önerir: önerilen ayarla, yine de ya da hiç yüklememeyi seçersin.
3. Yüklerken **RAM bekçisi** çalışır: boş RAM `ram_guard_mb`'nin altına inerse ya da Linux'ta bellek baskısı
   (PSI, süreçlerin belleği beklerken durduğu zamanın yüzdesi) `psi_guard`'ı geçerse yüklemeyi durdurur ve
   tüm modelleri boşaltır. Pop!_OS'ta model dosyası belleğe eşlendiği (mmap) ve açık uygulamalar sıkıştırılmış
   takasa (zram) itildiği için boş RAM yüklerken düşmeyebiliyor; tıkanmayı bellek baskısı gösterir.

`/fit <ad>` aynı hesabı yüklemeden yapar. Diskte olup hiçbir taşa bağlı olmayan bir model için
(`/fit <model anahtarı>`) `config.json`'a yapıştırılacak hazır ayarı da yazar.

## Kurulum

### Linux (Pop!_OS, Ubuntu)
```bash
sudo apt install python3-venv        # Ubuntu/Pop!_OS'ta venv için gerekli
python3 -m venv ai-cli/.venv
ai-cli/.venv/bin/pip install -r ai-cli/requirements.txt
ai-cli/.venv/bin/python ai-cli/lmstudio-hub/build.py --install   # LM Studio sanal modelleri (aşağıda)
ln -s "$PWD/ai-cli/gambit.sh" ~/.local/bin/gambit   # her klasörden "gambit" ile açmak için
```
LM Studio'nun `lms` aracı `~/.lmstudio/bin/lms` yolunda aranır (`config.json`: `lms_path`).

### Windows: İnternetsiz (Çevrimdışı) Kurulum:
Depo içerisindeki hazır paketlerle internetsiz kurulum yapmak için:
```powershell
# Proje ana dizinindeyken:
python -m venv ai-cli\.venv
.\ai-cli\.venv\Scripts\python.exe -m pip install --no-index --find-links wheels -r ai-cli\requirements.txt
```

### Windows: Standart Kurulum:
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
.\ai-cli\ai.bat --no-think           # düşünme kapalı (--think: açık, modelin varsayılan düzeyi)
.\ai-cli\ai.bat --effort medium      # düşünme düzeyi (modelde yoksa en yakını)
.\ai-cli\ai.bat -m queen --image ekran.png "bu hatayı açıkla"   # resimli tek seferlik soru (görsel modda yüklü olmalı)
.\ai-cli\ai.bat --show-think         # düşünme metnini ekranda göster
```

Linux'ta `.\ai-cli\ai.bat` yerine `ai-cli/gambit.sh` (ya da bağlantıyı kurduysan `gambit`) kullanılır.
Windows'ta `ai-cli` klasörünü kullanıcı `PATH` ortam değişkenine eklerseniz her yerden doğrudan `gambit` veya `ai` yazarak çalıştırabilirsiniz (ör. `gambit -m bishop`).

LM Studio sunucusu kapalıysa CLI onu kendisi başlatır. Model seçilmezse, yüklü modellerden araç
kullanabilen ilki seçilir.

## Komutlar

| Komut | Ne yapar |
|---|---|
| `/load queen` | Diğer modelleri boşaltır, bellek tahminine bakıp modeli kendi ayarlarıyla RAM bekçisi altında yükler |
| `/model` (`/models`) | Modelleri ve yüklü olup olmadıklarını listeler; diskte olmayanları ve ayarı olmayan modelleri ayrı gösterir. `/model <ad>` ile yüklü olana geçer |
| `/fit rook` | Yüklemeden bellek tahmini yapar, bu makineye uygun GPU oranı ve bağlam önerir |
| `/vision` | Görsel modu açar/kapatır: model görsel ekiyle (ya da eksiz) kendi ölçülmüş ayarıyla yeniden yüklenir |
| `/image ekran.png` | Resmi sonraki mesaja ekler (görsel modda; png, jpg, webp, gif, bmp; en fazla 10 MB). `/image` yalnız: eklenenleri siler |
| `/unload` | Tüm modelleri boşaltır |
| `/clear` | Yeni sohbet başlatır |
| `/undo` | Modelin yaptığı son dosya değişikliğini geri alır (art arda kullanılabilir) |
| `/compact` | Eski araç çıktılarını kısaltıp bağlamda yer açar (bağlam dolarken bu kendiliğinden de yapılır) |
| `/tools` | Araçları açar/kapatır |
| `/think` | Düşünmeyi açar/kapatır; `/think low`, `/think xhigh` gibi düzey de seçer (modelin düzeyleri yanıtta yazar) |
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
| `run_command` (Windows: PowerShell, Linux: bash) | gerekir; önce komut gösterilir |
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

## Düşünme düzeyleri

Her modelin düzeyleri LM Studio'nun bildirdiği listeden okunur (`/think` yazınca görünür):

| Düzey | Ne yapar |
|---|---|
| `off` | Düşünmez; en hızlısı. İstekle `reasoning_effort: "none"` gider |
| `on` | Modelin varsayılan düzeyiyle düşünür |
| `low`, `medium`, `high`, `xhigh` | Kademeli düzey; yalnızca şablonu bunu tanıyan modellerde (knight, king) |

Modelde olmayan bir düzey istenirse en yakını seçilir: açık/kapalı modelde `medium` → `on`, king'de `low` →
`xhigh` (Bonsai `low`'u desteklemiyor, kartı da öyle diyor), kapatılamayan knight'ta `off` → `none` (LM Studio'da çalışıyorsa `low`; Inkling'de en
düşük düzey bile düşünmeyi tam kapatmaz). Varsayılan düzey `config.json`'daki `effort` (`off`).

### Görsel mod

pawn, knight, bishop, queen ve king'in görsel eki (mmproj) diskte; rook'unki ayrı bir depoda ve indirilmedi. Görsel ek
VRAM'de 0,6–1,8 GB tuttuğu için her taşın iki ayarı var: metin modu (varsayılan, ek yüklenmez, GPU oranı yüksek) ve
görsel modu (`"vision": {"model", "gpu"}`, ayrıca ölçülmüş daha düşük oran). `/vision` modeli öteki moda geçirip yeniden
yükler, `/image <dosya>` resmi sonraki mesaja ekler. Alt çubukta "görsel açık" ve bekleyen resim sayısı görünür.

### LM Studio sanal modelleri (`lmstudio-hub/`)

Taşların çoğu diskteki GGUF'a değil, onu saran bir LM Studio sanal modeline (`gambit/...`, bir `model.yaml`)
bağlı. Sanal model dosyayı değiştirmez; yükleme ayarı ve düşünme düzeyi ekler. Her modelin iki tanımı var:
`gambit/<ad>` (metin) ve `gambit/<ad>-vision` (görsel ek açık).

- **Metin modunda görsel eki yüklenmez** (`--mmproj` kaldırılır). Ek 6 GB'lık kartta 0,6–1,8 GB VRAM yiyordu
  (Fable'ınki F32, 1,8 GB). Ornith'te aynı GPU oranında boş VRAM 0,7 GB'tan 1,8 GB'a çıktı; oran %55'ten %85'e,
  hız 16,5'ten 29,8 tok/s'ye.
- **Kademeli düzeyler şablona ulaşır.** LM Studio istekteki `reasoning_effort`'u şablona iletmez, yalnızca düşünmeyi
  açar ya da kapatır (`chat_template_kwargs` da yok sayılır). Düzey, sanal modelde `reasoning_effort` seçim alanına
  bağlanınca iletiliyor (knight, king).
- **Inkling 16k'ya sığar ve hızlanır:** llama.cpp prompt işlerken CPU'daki ağırlıkları GPU'ya kopyalıyor (op
  offload); Inkling'de bu ~6 GB tampon istiyordu → `--no-op-offload`. Ama LM Studio'nun isteğe bağlı tensör yüklemesi
  (`lazyMode`) açıkken GPU katmanlarının ağırlıkları da hiç GPU'ya gitmiyordu: 11,6 GB uzman ağırlığı RAM'e sığmayıp
  diskten okunuyor, kısa bir prompt dakikalar sürüyordu. Sanal modelde `lazyMode` kapalı, işlem grubu 128, bütün
  katmanlar GPU'da ve uzman tensörlerinin GPU'ya sığmayanı `--override-tensor` ile CPU'da: 12,1 tok/s.

Kurmak ya da değiştirdikten sonra yenilemek için:

```bash
ai-cli/.venv/bin/python ai-cli/lmstudio-hub/build.py --install
```

Kurulu değilse taşlar dosya adıyla düz modele düşer: görsel eki hep yüklenir (metin modunun GPU oranları sığmayabilir),
knight ve king yalnızca açık/kapalı olur, knight 16k'da yüklenmez. Qwen3.8 27B'nin kendisi (`unsloth/Qwen3.8-27B-GGUF`) indirilirse
aynı yolla `low`, `medium`, `xhigh` eklenebilir.

Otomatik düşünme modu (`auto`: analiz sorularında ve başarısız komuttan sonra düşünmeyi açan) şimdilik
kaldırıldı; config'te `"thinking": "auto"` kalmışsa `off` sayılır. Eski benchmark ölçümleri (31 görev, Windows):

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
- `effort`: varsayılan düşünme düzeyi: `"off"` (varsayılan), `"on"` ya da `"low"`...`"xhigh"`. Ayrıntılar
  "Düşünme düzeyleri" bölümünde. Eski `thinking` ayarı da okunur (`true` → `on`, `false`/`"auto"` → `off`).
- `show_thinking`: düşünme metni ekranda gösterilsin mi. Gizliyken model yine düşünür.
- `think_budget`: bir adımda en fazla kaç token düşünülsün (varsayılan 6144; `0` sınırsız). Aşılırsa adım
  düşünmeden tekrarlanır; küçük modeller aksi halde dakikalarca düşünüp hiç cevap vermeyebiliyor.
- `max_steps`: bir mesaj için en fazla model adımı (varsayılan 25).
- `context_length`: sunucu bağlam uzunluğunu bildirmiyorsa (LM Studio dışı) otomatik kısaltma için kullanılır.
- `animations`, `markdown`: animasyonlar ve Markdown biçimi (varsayılan ikisi de açık).
- `lms_path`: LM Studio'nun `lms` aracı. Windows'tan kalan `.exe` uzantısı Linux'ta yok sayılır; bulunamazsa
  `~/.lmstudio/bin` ve `PATH` aranır.
- `vram_limit_gb`: modele ayrılabilecek en fazla VRAM (varsayılan sınır yok). `nvidia-smi` çalışmıyorsa
  (ör. sürücü güncellendi, bilgisayar yeniden başlatılmadı) tahminler bununla karşılaştırılır.
- `ram_guard_mb` (800), `psi_guard` (40): RAM bekçisinin sınırları; yüklerken boş RAM bunun altına inerse ya
  da bellek baskısı yüzde bunu geçerse yükleme durdurulur. `ram_reserve_gb` (1), `vram_reserve_mb` (300; bu
  config'te 500): tahmin karşılaştırılırken sisteme ve masaüstüne bırakılan paylar.
- `presets`: `/load` için modeller. Anahtar CLI'da görünen ad (`queen`), `desc` listelerde görünen açıklama.
  - Model: `file` GGUF dosya adı (model diskte bununla bulunur), `model` LM Studio model anahtarı (bilinmiyorsa
    yazılmayabilir), `repo` Hugging Face deposu, `quant` ve `size_gb` bilgi için.
  - Yükleme: `context` bağlam uzunluğu, `gpu` GPU oranı (`0.35`, `"max"`, `"off"`), `mtp` MTP tahmini kodlama
    (`true`/`false`; yazılmazsa LM Studio karar verir). `args` doğrudan `lms load`'a geçirilir ve aynı ayar
    ikisinde de varsa `args` geçerlidir; `--parallel 1` varsayılandır.
  - Düşünme: `efforts` modelin düzey listesini LM Studio'nunkinin yerine koyar (ör. LM Studio dışı sunucu için),
    `effort_default` onun varsayılanı. `"thinking": false` düşünemeyen, `"thinking": "always"` düşünmesi
    kapatılamayan model içindir.
  - Sunucu: `"server": {"engine", "bin", "port", "env", "args", "efforts", "effort_default"}` metin modunu Gambit'in
    başlattığı `llama-server`'da çalıştırır (`-m`, `--host`, `--port`, `--alias` Gambit ekler; bkz. "Gambit'in başlattığı
    sunucular").
  - Görsel: `"vision": {"model": "gambit/...-vision", "gpu": 0.5}` görsel modun model anahtarı ve GPU oranı. Sanal model
    kurulu değilse görsel mod dosya adıyla düz modele düşer (LM Studio görsel ekini onunla yükler). `"tools": false` araç çağıramayan modelde araçları ve araç
  talimatlarını hiç göndermez; model yalnızca sohbet eder.
