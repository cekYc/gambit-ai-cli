# Gambit: yapılacaklar

## 1. Arayüz: Umay CLI'ın arayüzünü Gambit'e uyarla

[Umay CLI](https://github.com/Umay-Official/Umay-CLI) arayüzü daha güzel; Gambit'e taşınacak.

- [ ] Umay CLI arayüzünde neyin daha iyi olduğunu listele (yerleşim, renkler, araç çağrısı ve düşünme gösterimi, durum satırı, giriş kutusu)
- [ ] Gambit'te karşılığını bul (`ai.py`: `banner`, `repl`, `Spinner`, `PIECES` renkleri, `THEME`)
- [ ] Satranç taşı kimliğini koru (♟ ♞ ♝ ♜ ♛ ♚ ve renkleri)
- [ ] Araçlar zaten ortak (`tools.py`, Umay CLI'da da kullanılıyor); sadece arayüz katmanı değişecek

## 2. Modelleri daha temiz kullanmak

26 Kasım 2026'da Pop!_OS'ta yapıldı; model yönetimi `ai-cli/lmstudio.py`'de (CLI ve benchmark betikleri ortak kullanır).

- [x] Ayarları yeni model listesine göre yeniden düzenle: Pop!_OS'ta indirilen modellere göre (bkz. bölüm 3, "İndirilenler")
- [x] Model diskte yoksa açıkça söyle; `/models` listesinde silinmiş modelleri ayrı göster (iniyorsa yüzdesiyle; `/load` diğer modelleri boşaltmadan durup indirme komutunu söyler)
- [x] Yüklemeden önce `lms load --estimate-only` ile bellek tahmini al; GPU'ya ya da RAM'e sığmayacaksa uyar ve sığan ayarı öner
- [x] Yükleme sırasında RAM bekçisi: boş RAM `ram_guard_mb`'nin (800) altına inerse **ya da bellek baskısı (PSI) %40'ı geçerse** yükleme durur, `lms unload --all`. Durdurma yolu gerçek yüklemeyle denendi
- [ ] RAM bekçisini sığmayan bir modelle sına (ör. `knight` + `--gpu off`), tarayıcı kapalıyken; PSI eşiği %40 tahmin, gerekirse ayarla
- [x] Donanıma göre ayar önerisi: `/fit <ad>` VRAM'e sığan en yüksek `--gpu` oranını (0,05 adımla) ve gerekirse 8k bağlamı önerir; `vram_limit_gb` 5,5
- [x] Model başına düşünme düzeyleri (27 Kasım): düzeyler LM Studio'nun `allowed_options`'ından okunur; `/think <düzey>`, `--effort`. Kademeli düzeyler (knight: low–xhigh, king: off/medium/xhigh) sanal modelle şablona bağlandı (`ai-cli/lmstudio-hub/`), prompt günlüğünden doğrulandı
- [x] Otomatik düşünme modu (`auto`) şimdilik kaldırıldı (CLI, Bench v1, Bench v2); varsayılan `effort: "off"`
- [ ] Otomatik modu tartış: geri gelecekse düzeylerle nasıl birleşir (ör. analiz sorusunda `medium`, hata sonrası bir üst düzey)
- [ ] Hangi taşın varsayılan düzeyi ne olmalı: Bench v2 ile düzeyleri karşılaştır (`--plan king:off,king:medium,king:xhigh`)
- [ ] Kırılganlığa karşı: yükleme sonrası sağlık denetimi (sürecin VRAM kullanımı beklenenden çok düşükse uyar), açılışta sanal model tanımlarının kurulu ve güncel olduğunu denetle, LM Studio / llama.cpp sürümü ölçülenden farklıysa bir kez uyar
- [~] MTP: ayar başına `"mtp": true/false` ve `tune_gpu.py --mtp` eklendi; ölçüm için `nvidia-smi` çalışmalı ve MTP katmanlı bir dosya gerekli (ör. Bonsai `-mtp`, Defiant Fable `MTP-Q4_K_M`)
- [x] Linux (Pop!_OS) desteği: `gambit.sh`, `lms` yolu (`.exe` olsa da bulunur), `run_command` bash ile; `python` yerine `python3` bildiriliyor; Bench v2 terminal görevleri Linux'ta "bash" diyor
- [x] Yeni model eklemeyi kolaylaştır: hazır ayarda `file`, `repo`, `quant`, `size_gb`, `context`, `gpu`, `mtp` tek yerde; `/fit <model anahtarı>` yapıştırılacak hazır ayarı yazar

## 3. Pop!_OS'a geçiş

Windows'ta 15,2 GB RAM'in ~9 GB'ını açık uygulamalar tutuyor, ekran kartında ~5,2 GB kullanılabiliyor. Pop!_OS'ta beklenen: ~13,5 GB boş RAM, "hybrid" grafik modunda ~5,7 GB VRAM. Rahat sınır ~16 GB model dosyası, 17 GB'a kadar sınırda (tarayıcı kapalı, 8k–16k bağlam). Bunlar tahmin; Pop!_OS'ta ölçülecek.

### Kurulacak modeller

| Model | Depo | Dosya (quant) | Boyut | Ne için |
|---|---|---|---|---|
| Gemma 4 26B A4B it QAT | `google/gemma-4-26B-A4B-it-qat-q4_0-gguf` (LM Studio: `google/gemma-4-26b-a4b-qat`) | **Q4_0** (QAT) | 14,44 GB + 1,19 GB görsel eki | Günlük ana model; Windows'ta ~17 tok/s, Bench v1'de 100 |
| Qwen3.8 27B | `unsloth/Qwen3.8-27B-GGUF` | **UD-IQ4_XS** | 14,35 GB | Zor işler; en az uyduran ama dense olduğu için yavaş |
| Qwen3.6 35B A3B heretic (sansürsüz) | `mradermacher/Qwen3.6-35B-A3B-uncensored-heretic-i1-GGUF` | **i1-IQ3_S** | 15,4 GB | Sansürsüz, kod ve siber; MoE olduğu için hızlı |
| Inkling 2 Mini Uncensored | `AtomicChat/Inkling-2-Mini-Uncensored-GGUF` | **AD-IQ3_S** | 13,34 GB + 0,64 GB görsel eki | Deneme; Bench v2'de Qwen ve Gemma ile karşılaştırılacak |

### Değişen tercihler (ilk listeye göre)

- Qwen3.6 heretic: **IQ3_XS (14,48 GB) yerine i1-IQ3_S (15,4 GB)**. IQ3_XS için yapımcı notu yok, IQ3_S'e "Q3_K türlerinden iyi" notu var. `llmfan46/...-Native-MTP-Preserved-GGUF` deposunda en küçük dosya 17,27 GB olduğu için o depo seçilmedi. Görsel için mmproj dosyası statik depoda: `mradermacher/Qwen3.6-35B-A3B-uncensored-heretic-GGUF`.
- Inkling: **UD Q3_K_XL (14,90 GB, Unsloth) alınmayacak**, yalnızca sansürsüz AD-IQ3_S. "AD" = Atomic Dynamic: dikkat ve döngü katmanları Q8_0, uzmanlar sıkıştırılmış; orijinalle aynı sonraki tokenı seçme oranı %94,2. Sansür kaldırma MMLU'da −1,5 puan, araç çağrısı 20/20. Sansürlü Inkling istenirse Unsloth yerine `AtomicChat/Inkling-2-Mini-GGUF` → AD-IQ4_XS (15,00 GB).
- Qwen3.8 27B için ayrı MTP dosyası (`Mtp Qwen3.8 27B`, 2,30 GB) **gerekmez**: kaliteyi değiştirmez, RAM yer; `king` ayarında MTP zaten kapalıydı.
- Gemma için QAT Q4_0, Unsloth UD-IQ4_XS ve UD-Q3_K_M'den tercih edildi: aynı boyutta orijinale en yakın olan QAT.

### İndirilenler ve taşlar (27 Kasım)

| Taş | Model | Dosya | Düşünme | Görsel eki |
|---|---|---|---|---|
| ♟ pawn | Ornith 1.5 9B sansürsüz | `Ornith-1.5-9B-uncensored.IQ4_XS.gguf` (5,23 GB) | off/on | f16, 0,88 GB |
| ♞ knight | Inkling 2 Mini sansürsüz | `Inkling-2-Mini-Uncensored-AD-IQ3_S.gguf` (13,34 GB) | low/medium/high/xhigh (kapatılamaz) | F16, 0,61 GB |
| ♝ bishop | Qwen3.5 9B Defiant Fable sansürsüz | `Qwen3.5-9B-The-Defiant-Fable-Uncnr-Heretic-NEO-MAX-Q4_K_M.gguf` (6,83 GB) | off/on | F32, 1,74 GB |
| ♜ rook | Qwen3.6 35B A3B heretic | `Qwen3.6-35B-A3B-uncensored-heretic.i1-IQ3_S.gguf` (15,25 GB) | off/on | yok (ayrı depoda, indirilmedi) |
| ♛ queen | Gemma 4 26B A4B QAT | `gemma-4-26B-A4B-it-QAT-Q4_0.gguf` (14,44 GB, `lmstudio-community/`) | off/on | BF16, 1,19 GB |
| ♚ king | Ternary Bonsai 2.5 27B (Qwen3.8 27B ternary) | `Ternary-Bonsai-2.5-27B-Q2_0.gguf` (7,67 GB) | off/medium/xhigh (`low` desteklenmiyor) | BF16, 0,89 GB |

- king listede Qwen3.8 27B UD-IQ4_XS'ti (14,35 GB, indirilmedi); Bonsai 2.5 aynı modelin 1,76 bit'lik hâli ve modelin kartına göre araç çağırmada FP16 düzeyinde. Qwen3.8 indirilirse sanal modeli `low`/`medium`/`xhigh` ile eklenebilir.
- pawn ve bishop listede yoktu (Pop!_OS'ta indirildi); taşları boyut/hıza göre seçildi, değiştirilebilir.

### Ölçülen ayarlar (27 Kasım, `nvidia` grafik modu, 16k bağlam)

`benchmark/tune_gpu.py --fit`: her oranda gerçek yükleme + uzun prompt, ekran kartında en az 500 MiB boş kalan en yüksek
oran. Metin modunda görsel eki yüklenmiyor (sanal modeller, `ai-cli/lmstudio-hub/`).

| Taş | Metin: GPU · üretim · prompt | Görsel: GPU · üretim · prompt | Not |
|---|---|---|---|
| ♟ pawn | 0.85 · 29,8 · 1141 tok/s | 0.55 · 16,9 · 908 tok/s | görsel eki 0,88 GB |
| ♞ knight | max · 12,1 · 42 tok/s | max · ölçülmedi | uzmanların 4 bloğu GPU'da (görselde 2), kalanı RAM'de; aşağıya bak |
| ♝ bishop | 0.5 · 14,1 · 852 tok/s | 0.1 · 9,0 · 671 tok/s | görsel eki F32, 1,74 GB; depodaki F16 (0,92 GB) indirilirse görsel oran artar |
| ♜ rook | 0.25 · 15,0 · 520 tok/s | — | görsel eki indirilmedi (ayrı depo); 0.3'te boş VRAM 464 MiB |
| ♛ queen | 0.25 · 22,7 · 769 tok/s | 0.15 · 20,3 · 496 tok/s | Windows'ta ~17 tok/s; MoE, oran düşünce hız az düşüyor |
| ♚ king | 0.5 · 6,2 · 303 tok/s | 0.35 · 4,7 · 284 tok/s | Bonsai (Qwen3.8 27B ternary) |

- **knight (Inkling 2 Mini):** 16k'da ilk başta hiç yüklenmiyordu: llama.cpp prompt işlerken CPU'daki uzman ağırlıklarını GPU'ya kopyalıyor (op offload), bunun için ~6,2–7,7 GB tampon istiyordu (bağlam ve işlem grubu küçültülünce de sığmadı). Sanal modelde `--no-op-offload` ile yükleniyor. Ama uzman ağırlıkları GPU oranından bağımsız olarak CPU tarafında kalıyor (16 GPU katmanında süreç yalnızca ~1 GB VRAM kullanıyor), 13,3 GB'lık dosyanın RAM'de durması gerekiyor; açık uygulamalarla bu sığmıyor ve ağırlıklar diskten yeniden okunuyor: 700 token'lık prompt 8 dakikada bitmedi. Nedeni LM Studio'nun isteğe bağlı tensör yüklemesi (`lazyMode`): `--no-op-offload` ile birlikte GPU katmanlarının ağırlıkları GPU'ya hiç gitmiyordu (%95'te süreç ~1 GB VRAM kullanıyordu). **Çözüldü (sanal model):** `lazyMode` kapalı, işlem grubu 128, `--gpu max` ve `--override-tensor` ile 20 bloğun uzmanları CPU'da, döngülü 6-9'unki GPU'da → 12,1 tok/s üretim, ~44 tok/s prompt (`--threads-batch 8` ile ~48), uzun prompttan sonra 725 MiB boş VRAM, 9,4 GiB boş RAM. 5 blokla 12,5 tok/s ama yalnızca 263 MiB boş kalıyordu. AD-IQ2_M'e gerek kalmadı.
- [x] knight'ın prompt hızı (27 Kasım): op offload kapalı olduğu için CPU'daki uzmanlar prompt'ta CPU'da hesaplanıyor. Uzun prompt (5,5k token), iki tur: taban 44,4 tok/s → `--threads-batch 8` 48,0 (üretim 13,8, değişmedi); işlem grubu 256 + 3 GPU bloğu 50,0 ama üretim 10,6-13,3'e düşüyor; üretim için 8 iş parçacığı ve prompt için 16 fayda etmedi. Kısa prompt ölçümleri aynı ayarda ±%40 oynuyor, karar uzun prompta göre. Kalan sınır CPU: hibrit moda geçince bir uzman bloğu daha GPU'ya girer (`lmstudio-hub/build.py`, `INKLING_GPU_EXPERT_BLOCKS`). Ölçümler: `benchmark/results/tuning/knight_variants_*.json`
- [ ] bishop'ın görsel ekini F16'yla değiştir (`mmproj-F16.gguf`, 0,92 GB; F32 1,74 GB): görsel modda %10 yerine daha yüksek GPU oranı (tahmin ~%35; ölçülmedi)
- Adımlar 0,05; büyük modellerde (rook, queen) her adım ~700 MiB, aradaki boşluk kullanılmıyor.
- **Tek seferlik deneme (27 Kasım):** her taş kendi ölçülmüş ayarıyla yüklenip `gambit.sh -y` ile "fiyatlar.csv'den toplam hesaplayan topla.py yaz, çalıştır" görevini aldı: 6 taşın 6'sı dosyayı yazıp çalıştırdı, sonuç doğru (488,75; pawn 24 sn, bishop 22, queen 37, rook 108, king `medium` 96, knight `medium` 115 sn). Görsel modda 5 taşın 5'i 4 renkli deneme resmindeki renkleri ve sol üst köşeyi doğru söyledi (`--image`). Düzeyler prompt günlüğünden doğrulandı: knight low/medium/high/xhigh → 0.2/0.7/0.9/0.99 (düşünme 240 → 796 karakter), king medium/xhigh.

### Pop!_OS'ta ilk işler

1. [x] **Bilgisayarı yeniden başlat** (27 Kasım'da yapıldı, `nvidia-smi` çalışıyor): NVIDIA sürücüsü güncellenmiş ama yüklü çekirdek modülü eski (595.84, kütüphane 595.104) → `nvidia-smi`: "Driver/library version mismatch". CUDA yine de çalışıyor (`llama-server` libcuda yüklüyor) ama VRAM ölçülemiyor.
2. [x] Grafik modu "hybrid" yapıldı (27 Kasım). Ama iki ekran da (laptop paneli eDP-2 ve HDMI) hâlâ NVIDIA'ya bağlı: paneli hangi kartın süreceğini BIOS'taki MUX belirliyor, HDMI her durumda NVIDIA'da. Kazanç ~190 MiB (boş VRAM 5,20 → 5,39 GB); oranları değiştirmeye yetmedi.
3. [x] LM Studio ve `lms` kurulu, `.venv` oluşturuldu. Not: `python3.12-venv` paketi yok, venv pip'siz kurulup pip elle eklendi; temiz kurulum için `sudo apt install python3-venv`.
4. [x] Gambit Linux'ta çalışıyor: `ai-cli/gambit.sh`, `lms_path` `~/.lmstudio/bin/lms`.
5. [x] Her model 16k bağlamda gerçek yüklemeyle ölçüldü (`tune_gpu.py --fit all --apply`, bkz. "Ölçülen ayarlar"). Hibrit moda geçilirse yeniden çalıştır.
6. [x] `config.json` satranç ayarları indirilen modellere göre yazıldı (tahmine göre); ölçümden sonra `gpu` değerlerini güncelle.
7. [ ] Bench v2 ile karşılaştır: `python benchmark/v2/run.py --plan <ayar>:off,<ayar>:on` (ya da bir düzey). JS görevleri için `node` gerekli (`sudo apt install nodejs`; şu an kurulu değil, öz testte 4 görev bu yüzden hata veriyor). Heretic'te araç çağrısı ölçülmemiş, ajan görevlerine özellikle bak. Linux'ta terminal görevleri bash ile yapılıyor; Windows sonuçlarıyla birebir karşılaştırılmaz.

### Pop!_OS'ta öğrenilenler

- RAM: toplam 14,9 GiB; Firefox, Claude ve LM Studio açıkken ~7,3 GiB boş.
- Takas: 14,9 GB zram (sıkıştırılmış, RAM'de) + 4 GB disk, `swappiness` 180. Model yüklenirken çekirdek açık uygulamaları zram'e itiyor, model dosyası belleğe eşleniyor (mmap); bu yüzden "boş RAM" yüklerken düşmüyor, hatta artıyor (7,2 → 9,8 GiB). Tıkanmayı bellek baskısı (`/proc/pressure/memory`) gösteriyor; normal yüklemede en fazla %2.
- LM Studio "failed to mlock ... RLIMIT_MEMLOCK" uyarısı veriyor (`ulimit -l` ~1,9 GiB): "modeli bellekte tut" tam kilitlenemiyor. Zararsız görünüyor; hız sorunu olursa bakılacak.

### LM Studio mu, doğrudan llama-server mı? (27 Kasım)

LM Studio modelleri kendi paketindeki llama.cpp `llama-server`'ıyla çalıştırıyor (`~/.lmstudio/extensions/backends/llama.cpp-linux-x86_64-nvidia-cuda12-avx2-2.83.0/`). knight, LM Studio'nun ürettiği komut satırının birebir aynısıyla doğrudan da çalıştırıldı (CUDA kütüphaneleri `backends/vendor/linux-llama-cuda12-vendor-v1/` altında, `LD_LIBRARY_PATH`'e eklenmeli) ve aynı protokolle arka arkaya ölçüldü:

| | Doğrudan llama-server (tur 1 / 2) | LM Studio (tur 1 / 2) |
|---|---|---|
| Uzun prompt (5,5k token) | 49,1 / 45,1 tok/s | 47,1 / 46,7 tok/s |
| Üretim (300 token) | 14,3 / 11,0 tok/s | 13,6 / 12,7 tok/s |
| Boş VRAM | 722 / 573 MiB | 719 / 719 MiB |
| Boş RAM | 9,68 / 8,03 GiB | 9,22 / 8,23 GiB |

- **Hız ve bellekte fark yok** (gürültü içinde). LM Studio servisi arayüz kapalıyken ~90 MB tutuyor; arayüz açıkken ~1,2 GB.
- **Doğrudan llama-server'ın tek gerçek artısı kontrol:** düşünme düzeyi `chat_template_kwargs` ya da üst düzey `reasoning_effort` ile şablona doğrudan ulaşıyor (Inkling low/medium/xhigh → 0,2/0,7/0,99, sanal model gerekmeden); bütün llama.cpp ayarları komut satırında.
- **Karar:** şimdilik LM Studio'da kal (çalışıyor, ölçüldü, modeller onun arayüzünden indiriliyor). Sanal model alanları bir LM Studio güncellemesinde bozulursa ya da LM Studio'nun engellediği bir ayar gerekirse Gambit'e `llama-server` (+ model değiştirmek için `llama-swap` ya da yönlendirme modu) arka ucu eklenir; `base_url` zaten OpenAI uyumlu her sunucuyu kabul ediyor.

### ik_llama.cpp denemesi (27 Kasım, knight)

[ik_llama.cpp](https://github.com/ikawrakow/ik_llama.cpp) Inkling 2 Mini'yi (`inkling2_loop`) 22 Kasım'dan beri destekliyor (#2967). `~/Desktop/GambitAI/ik_llama.cpp`'de derlendi (commit b945c31; `sudo apt install cmake nvidia-cuda-toolkit`, CUDA 12.0, g++-12):

```bash
cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=86 -DCMAKE_BUILD_TYPE=Release -DCMAKE_CUDA_HOST_COMPILER=g++-12 -DLLAMA_CURL=OFF
cmake --build build --target llama-server -j 12
```

En iyi ayar (16k bağlam, aynı AD-IQ3_S dosyası):

```bash
GGML_CUDA_NO_PINNED=1 build/bin/llama-server -m <Inkling...AD-IQ3_S.gguf> -c 16384 -np 1 --jinja -fa on -ngl 99 \
  --swa-compress -ub 256 -t 6 -tb 8 \
  -ot 'blk\.(0|1|2|3|4|5|10|11|12|13|14|15|16|17|18|19|20|21|22|23)\.ffn_(gate_up|down)_exps\.weight=CPU'
```

| Ayar (sunucu tarafı, 2 tur) | Uzun prompt | Kısa prompt | Üretim | Boş VRAM |
|---|---|---|---|---|
| LM Studio (llama.cpp 2.83.0, 4 blok, ub128) | 46,9 | ~47 | 13,2 | 725 MiB |
| ik: LM Studio'nun aynısı (4 blok, ub128) | 83,8 | 89,6 | 14,7 | 1212 |
| **ik: ub256, 4 blok** | **97,1** | 95,5 | 15,3 | 1098 |
| ik: ub256, 5 blok | 100,0 | 98,4 | 15,8 | 644 |
| ik: uzman önbelleği 2,6 GB (bütün uzmanlar CPU'da) | 67,1 | 63,4 | 10,1 | 480 |

- Prompt okuma ~2,1 kat, üretim ~%15-20 hızlı. Düşünme düzeyleri `chat_template_kwargs` ya da üst düzey `reasoning_effort` ile şablona gidiyor (sanal model gerekmez), araç çağrıları doğru ayrıştırılıyor (`tool_calls`, düşünme `reasoning_content`'te).
- `--swa-compress` şart: yoksa KV önbelleği kayan pencereyi kullanmıyor, 48 katman geçişinin hepsine tam bağlam ayırıyor (3,1 GB; açıkken 0,7 GB).
- `GGML_CUDA_NO_PINNED=1` şart: yoksa CPU'daki uzmanlar 9,5 GiB kilitli belleğe kopyalanıyor, boş RAM 1,35 GiB'e düşüyor. Kapalıyken ağırlıklar LM Studio'daki gibi dosyadan eşleniyor (çekirdek geri alabiliyor).
- İşlem grubu 512 yüklenmiyor (hesap tamponu 3,9 GB); uzman önbelleği sabit yerleşimden yavaş (isabet %55).
- [x] Gambit'e ik_llama.cpp arka ucu (`ai-cli/servers.py`, hazır ayarda `"server"`): `/load knight` LM Studio'yu boşaltıp sunucuyu başlatır, `/vision`, başka taş ve `/unload` kapatır; sunucu Gambit kapansa da yaşar, PID `~/.cache/gambit/servers.json`'da. Denendi: tek seferlik CSV görevi doğru (86 sn, sunucu açılışı dahil), sohbette knight → pawn → knight → görsel (LM Studio) → metin → `/unload` geçişleri, Bench v2 `kod-turkce` (`knight:low`) 95/100. Ölçümler: `benchmark/results/tuning/knight_ik_llama_20261127.json`
- [x] Bench v2 düzeltmesi: plan sonundaki yeniden puanlama görev klasörü olmayan (Windows koşuları) ya da notlandırıcısı çalışamayan (node yok) kayıtları sıfırlıyordu (93 kayıt); artık atlıyor, eski puan korunuyor

## Notlar

- Laptop: RTX 3060 Laptop 6 GB VRAM, 15,2 GB RAM. Rahat sınır ~10 GB model dosyası; 13–15 GB dosyalar çalışıyor ama sınırda.
- Yeni modelleri Bench v2 (39 görev) ile karşılaştır: `python benchmark/v2/run.py --plan <ayar>:off,<ayar>:on`
