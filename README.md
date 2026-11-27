# Gambit AI & Local LLM Benchmark Suite

LM Studio ve yerel büyük dil modelleri (Gemma, Qwen vb.) ile **%100 çevrimdışı (offline)** ve güvenli çalışan akıllı terminal asistanı (**Gambit CLI**) ile yerel modeller için 31 görevlik kapsamlı performans ve yetenek değerlendirme paketi (**Benchmark Suite**).

---

## Öne Çıkan Özellikler

- **Tamamen Çevrimdışı ve Gizlilik Odaklı:** İnternet bağlantısı gerektirmez. Verileriniz, dosyalarınız ve komut geçmişiniz bilgisayarınızdan asla dışarı çıkmaz.
- **Satranç Taşı Rolleri:** Modeller VRAM, bağlam ve hız ihtiyaçlarına göre optimize edilmiş satranç taşları isimleriyle çağrılır (`knight`, `rook`, `queen`, `bishop`, `king`).
- **Model Başına Düşünme Düzeyleri:** Her modelin desteklediği düzeyler (kapalı/açık, kademeli modellerde low–xhigh) LM Studio'dan okunur; `/think <düzey>` ya da `--effort` ile seçilir.
- **Kullanıcı Onaylı Güvenli Araçlar (Tool Calling):** Dosya okuma ve arama işlemleri doğrudan yapılır; dosya yazma, düzenleme (diff gösterimi ile) ve PowerShell komut çalıştırma her zaman kullanıcı onayına tabidir.
- **31 Görevlik Yerel Model Benchmark'ı:** Python, SQL, PowerShell ve çok adımlı dosya ajan senaryolarında modellerin doğruluğunu, süresini ve token üretimini ölçen test paketi.
- **Görsel Dashboard & Tablolar:** Sonuçları detaylı radar grafikleri, ısı haritası ve karşılaştırma tablolarıyla sunan HTML panosu.
- **Sıfır İnternet Kurulumu:** `wheels/` dizini sayesinde sıfırdan internetsiz ortamlarda dahi tek komutla çalışmaya hazır hale gelir.

---

## Proje Yapısı

```text
├── ai-cli/                     # Gambit CLI asistanı
│   ├── ai.py                   # CLI ana çalışma motoru ve sohbet döngüsü
│   ├── tools.py                # Modelin kullandığı güvenli kabuk (PowerShell/bash) ve dosya araçları
│   ├── lmstudio.py             # Model yönetimi: diskteki modeller, bellek tahmini, GPU oranı önerisi, RAM bekçisi
│   ├── servers.py              # Gambit'in başlattığı llama-server'lar (knight: ik_llama.cpp)
│   ├── config.json             # Sunucu, model ve satranç profilleri ayarları
│   ├── config.example.json     # Şablon konfigürasyon dosyası
│   ├── ai.bat / gambit.bat     # Windows başlatma betikleri
│   ├── gambit.sh               # Linux başlatma betiği
│   ├── lmstudio-hub/           # LM Studio sanal modelleri: görsel eki kapalı, düşünme düzeyleri (build.py)
│   └── requirements.txt        # Python bağımlılıkları (openai, rich, prompt_toolkit)
├── benchmark/                  # Yerel modeller için benchmark paketi
│   ├── bench.py                # Otomatik test ve değerlendirme motoru
│   ├── tasks.py                # 31 kodlama, SQL, terminal ve ajan görevi
│   ├── grading.py              # Görev sonuçlarını değerlendiren test fonksiyonları
│   ├── tune_gpu.py             # En uygun VRAM/GPU oranını ölçen optimizasyon aracı
│   ├── report.py               # Sonuçları JSON ve tablolara dönüştüren raporlayıcı
│   ├── dashboard/index.html    # Radar grafikli ve interaktif görsel dashboard
│   ├── results/                # Benchmark kayıtları, model cevapları ve JSONL verileri
│   └── tablolar/               # Markdown ve CSV formatında özet puan tabloları
├── wheels/                     # Windows/Python 3.14 için internetsiz hazır kurulum paketleri
└── deneme/                     # Ajan ve test denemeleri için örnek Flask CRUD uygulaması
```

---

## Hızlı Başlangıç

### 1. Gereksinimler
- **İşletim Sistemi:** Windows (PowerShell 7 veya Windows PowerShell) ya da Linux (Pop!_OS/Ubuntu, bash)
- **Python:** Python 3.10 veya üzeri (tercihen Python 3.14)
- **LM Studio:** [lmstudio.ai](https://lmstudio.ai) kurulu ve yerel sunucusu (`lms`) hazır olmalıdır.

### 2. Kurulum

#### Linux (Pop!_OS / Ubuntu)
```bash
sudo apt install python3-venv
python3 -m venv ai-cli/.venv
ai-cli/.venv/bin/pip install -r ai-cli/requirements.txt
ai-cli/.venv/bin/python ai-cli/lmstudio-hub/build.py --install   # LM Studio sanal modelleri
ai-cli/gambit.sh                    # ya da: ln -s "$PWD/ai-cli/gambit.sh" ~/.local/bin/gambit
```

#### Seçenek A: Çevrimdışı (İnternetsiz) Kurulum (Windows)
Depo içerisindeki hazır `wheels/` paketlerini kullanarak internete bağlanmadan kurulum yapabilirsiniz:
```powershell
python -m venv ai-cli\.venv
.\ai-cli\.venv\Scripts\python.exe -m pip install --no-index --find-links wheels -r ai-cli\requirements.txt
```

#### Seçenek B: Standart Pip Kurulumu
```powershell
python -m venv ai-cli\.venv
.\ai-cli\.venv\Scripts\pip install -r ai-cli\requirements.txt
```

> **İpucu:** `ai-cli` klasörünü ortam değişkenlerinizdeki `PATH` listesine eklerseniz, terminalinizde istediğiniz herhangi bir çalışma klasöründen yalnızca `gambit` veya `ai` yazarak asistanı başlatabilirsiniz.

---

## Gambit CLI Kullanımı

```powershell
# Bulunulan klasörde etkileşimli asistanı başlat
.\ai-cli\ai.bat

# Tek seferlik soru sor ve çık
.\ai-cli\ai.bat "bu klasördeki python dosyalarını listele"

# Belirli bir satranç modeli profiliyle aç
.\ai-cli\ai.bat -m knight

# Düşünme düzeyini belirle
.\ai-cli\ai.bat --no-think       # Düşünme kapalı (varsayılan, en hızlı)
.\ai-cli\ai.bat --effort medium  # Kademeli düzey (modelde yoksa en yakını)
.\ai-cli\ai.bat --show-think   # Düşünme sürecini ekranda göster
```

### Model Profilleri

| Profil Adı | Model | Rol ve Açıklama |
|---|---|---|
| `pawn` | Ornith 1.5 9B sansürsüz | Küçük ve hızlı; kısa, basit işler |
| `knight` | Inkling 2 Mini sansürsüz | Deneme; düşünme düzeyleri low–xhigh, Bench v2'de karşılaştırılacak |
| `bishop` | Qwen3.5 9B Defiant Fable sansürsüz | Hafif, hızlı ve görsel destekli; günlük pratik işler |
| `rook` | Qwen3.6 35B A3B heretic | Sansürsüz; kod ve siber güvenlik, MoE olduğu için hızlı |
| `queen` | Gemma 4 26B A4B QAT | Varsayılan ana model; her alanda tam puanlı, gerektiğinde düşünür |
| `king` | Ternary Bonsai 2.5 27B (Qwen3.8 27B, ternary) | Zor işler ve ajan görevleri; düşünme düzeyleri off/medium/xhigh |

Pop!_OS'ta (RTX 3060 6 GB, 16k bağlam) metin modunda pawn 29,8, queen 22,7, rook 15,0, bishop 14,1, knight ~15 (ik_llama.cpp), king 6,2 tok/s; görsel mod ayrı ölçülmüş oranla yüklenir (`/vision`). `/fit <ad>` modelin bu makinede belleğe sığıp sığmadığını hesaplar;
`/load` yüklemeyi RAM bekçisiyle yapar (ayrıntılar: [ai-cli/README.md](ai-cli/README.md)).

---

## Benchmark Suite

Yerel modellerinizin kodlama, komut satırı ve araç kullanma kabiliyetlerini ölçmek için:

```powershell
# Değerlendirmeyi başlat (varsayılan: knight ve queen)
python benchmark\bench.py

# Belirli bir modeli test et
python benchmark\bench.py --models queen --modes auto

# GPU katman/VRAM optimizasyonunu test et
python benchmark\tune_gpu.py queen 0.2 0.3 0.4 max

# Raporları ve tabloları güncelle
python benchmark\report.py
```

Sonuçları incelemek için `benchmark/dashboard/index.html` dosyasını tarayıcınızda açabilirsiniz.

### Özet Skorlar (31 Görev Üzerinden)

| Model | Düşünme Kapalı | Otomatik Düşünme | Düşünme Açık |
|---|---|---|---|
| `queen` | 94 puan (10 dk) | **100 puan** (20 dk) | 94 puan (69 dk) |
| `knight` | 71 puan (6 dk) | **82 puan** (20 dk) | 80 puan (61 dk) |
| `rook` | **88 puan** (8 dk) | — | — |
| `king` | **96 puan** (56 dk) | — | — |

---

## Güvenlik ve Araç İzinleri

Gambit CLI dosya yazma (`write_file`), dosya düzenleme (`edit_file`) ve kabuk komutu çalıştırma (`run_command`; Windows'ta PowerShell, Linux'ta bash) öncesinde her zaman kullanıcıdan onay ister:
- `e`: Evet (işlemi onayla)
- `t`: Bu oturum boyunca o araç için tüm işlemleri otomatik onayla
- `h`: Hayır (işlemi reddet; modele ret nedeni girilebilir)

---

## Lisans

Bu proje [PolyForm Noncommercial License 1.0.0](LICENSE) ile lisanslanmıştır: kişisel, eğitim, araştırma ve kâr amacı gütmeyen kullanım serbesttir; ticari kullanım için yazılı izin gerekir. 8 Kasım 2026'dan önceki sürümler MIT Lisansı ile yayımlanmıştı.

`ai-cli/tools.py` araçları, [Umay CLI](https://github.com/Umay-Official/Umay-CLI) projesinde de kullanılmaktadır.
