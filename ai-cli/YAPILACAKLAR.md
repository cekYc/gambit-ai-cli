# Gambit: yapılacaklar

## 1. Arayüz: Umay CLI'ın arayüzünü Gambit'e uyarla

[Umay CLI](https://github.com/Umay-Official/Umay-CLI) arayüzü daha güzel; Gambit'e taşınacak.

- [ ] Umay CLI arayüzünde neyin daha iyi olduğunu listele (yerleşim, renkler, araç çağrısı ve düşünme gösterimi, durum satırı, giriş kutusu)
- [ ] Gambit'te karşılığını bul (`ai.py`: `banner`, `repl`, `Spinner`, `PIECES` renkleri, `THEME`)
- [ ] Satranç taşı kimliğini koru (♟ ♞ ♝ ♜ ♛ ♚ ve renkleri)
- [ ] Araçlar zaten ortak (`tools.py`, Umay CLI'da da kullanılıyor); sadece arayüz katmanı değişecek

## 2. Modelleri daha temiz kullanmak

24 Kasım 2026 itibarıyla `config.json`'daki satranç ayarları silinmiş modellere bakıyor; yalnızca `inkling` ayarı yüklü bir modele bağlı.

- [ ] Ayarları yeni model listesine göre yeniden düzenle (Pop!_OS'ta kurulacak dört model: bölüm 3)
- [ ] Model diskte yoksa açıkça söyle; `/models` listesinde silinmiş modelleri ayrı göster
- [ ] Yüklemeden önce `lms load --estimate-only` ile bellek tahmini al; GPU'ya sığmayacaksa uyar
- [ ] Yükleme sırasında RAM bekçisi: boş RAM eşiğin altına inerse `lms unload --all` (24 Kasım testinde laptopu kilitlenmekten kurtardı)
- [ ] Donanıma göre ayar önerisi: VRAM ~4,5 GB'ı geçmeyecek `--gpu` oranı, 8k–16k bağlam
- [ ] Ayar başına düşünme modu: kalite isteyen modellerde `"thinking": "always"`
- [ ] MTP (`--speculative-draft-mtp`) ayarını model başına açıp kapatabilme; bu laptopta hız kazandırıp kazandırmadığını ölç
- [ ] Linux (Pop!_OS) desteğini dene: `gambit.bat` yerine `.sh` başlatıcı, `lms` yolu, bash ile araç çalıştırma
- [ ] Yeni model eklemeyi kolaylaştır: model anahtarı, sıkıştırma türü, boyut ve önerilen ayarlar tek yerde

## 3. Pop!_OS'a geçiş

Windows'ta 15,2 GB RAM'in ~9 GB'ını açık uygulamalar tutuyor, ekran kartında ~5,2 GB kullanılabiliyor. Pop!_OS'ta beklenen: ~13,5 GB boş RAM, "hybrid" grafik modunda ~5,7 GB VRAM. Rahat sınır ~16 GB model dosyası, 17 GB'a kadar sınırda (tarayıcı kapalı, 8k–16k bağlam). Bunlar tahmin; Pop!_OS'ta ölçülecek.

### Kurulacak modeller

| Model | Depo | Dosya (quant) | Boyut | Ne için |
|---|---|---|---|---|
| Gemma 4 26B A4B it QAT | `google/gemma-4-26B-A4B-it-qat-q4_0-gguf` (LM Studio: `google/gemma-4-26b-a4b-qat`) | **Q4_0** (QAT) | 14,44 GB + 1,19 GB görsel eki | Günlük ana model; Windows'ta ~17 tok/s, Bench v1'de 100 |
| Qwen3.8 27B | `unsloth/Qwen3.8-27B-GGUF` | **UD-IQ4_XS** | 15,38 GB | Zor işler; en az uyduran ama dense olduğu için yavaş |
| Qwen3.6 35B A3B heretic (sansürsüz) | `mradermacher/Qwen3.6-35B-A3B-uncensored-heretic-i1-GGUF` | **i1-IQ3_S** | 15,4 GB | Sansürsüz, kod ve siber; MoE olduğu için hızlı |
| Inkling 2 Mini Uncensored | `AtomicChat/Inkling-2-Mini-Uncensored-GGUF` | **AD-IQ3_S** | 13,34 GB + 0,64 GB görsel eki | Deneme; Bench v2'de Qwen ve Gemma ile karşılaştırılacak |

### Değişen tercihler (ilk listeye göre)

- Qwen3.6 heretic: **IQ3_XS (14,48 GB) yerine i1-IQ3_S (15,4 GB)**. IQ3_XS için yapımcı notu yok, IQ3_S'e "Q3_K türlerinden iyi" notu var. `llmfan46/...-Native-MTP-Preserved-GGUF` deposunda en küçük dosya 17,27 GB olduğu için o depo seçilmedi. Görsel için mmproj dosyası statik depoda: `mradermacher/Qwen3.6-35B-A3B-uncensored-heretic-GGUF`.
- Inkling: **UD Q3_K_XL (14,90 GB, Unsloth) alınmayacak**, yalnızca sansürsüz AD-IQ3_S. "AD" = Atomic Dynamic: dikkat ve döngü katmanları Q8_0, uzmanlar sıkıştırılmış; orijinalle aynı sonraki tokenı seçme oranı %94,2. Sansür kaldırma MMLU'da −1,5 puan, araç çağrısı 20/20. Sansürlü Inkling istenirse Unsloth yerine `AtomicChat/Inkling-2-Mini-GGUF` → AD-IQ4_XS (15,00 GB).
- Qwen3.8 27B için ayrı MTP dosyası (`Mtp Qwen3.8 27B`, 2,30 GB) **gerekmez**: kaliteyi değiştirmez, RAM yer; `king` ayarında MTP zaten kapalıydı.
- Gemma için QAT Q4_0, Unsloth UD-IQ4_XS ve UD-Q3_K_M'den tercih edildi: aynı boyutta orijinale en yakın olan QAT.

### Pop!_OS'ta ilk işler

1. Grafik modunu "hybrid" yap (ekranı Radeon çizsin, NVIDIA boş kalsın); `nvidia-smi` ile boş VRAM'i kontrol et.
2. LM Studio ve `lms` kur, depoyu klonla, `.venv` oluştur (`requirements.txt`).
3. Gambit'i Linux'ta çalıştır: `gambit.bat` yerine `.sh` başlatıcı, `config.json` içinde `lms_path`.
4. Her model için `python benchmark/tune_gpu.py --context 16384 <model> 0.3 0.35 0.4` ile GPU oranını ölç (VRAM ~5,5 GB'ı geçmesin). Yüklemeyi RAM bekçisiyle yap.
5. `config.json` satranç ayarlarını bu dört modele göre yaz; kalite için `"thinking": "always"` seçeneğini dene.
6. Bench v2 ile karşılaştır: `python benchmark/v2/run.py --plan <ayar>:off,<ayar>:auto`. Heretic'te araç çağrısı ölçülmemiş, ajan görevlerine özellikle bak.

## Notlar

- Laptop: RTX 3060 Laptop 6 GB VRAM, 15,2 GB RAM. Rahat sınır ~10 GB model dosyası; 13–15 GB dosyalar çalışıyor ama sınırda.
- Yeni modelleri Bench v2 (39 görev) ile karşılaştır: `python benchmark\v2\run.py --plan <ayar>:off,<ayar>:auto`
