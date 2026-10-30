# Yerel Model Benchmark Paketi (Local LLM Benchmark)

LM Studio üzerinde çalışan yerel büyük dil modellerini (Gemma, Qwen, Coder vb.) kodlama, SQL, PowerShell terminali ve çok adımlı ajan görevlerinde sınayan kapsamlı değerlendirme paketi.

Modelleri hem standart (**düşünme kapalı**) hem **otomatik düşünme** (`auto`) hem de **tam düşünme** (`on`) modlarında karşılaştırır; hız, VRAM kullanımı ve başarı puanlarını raporlar.

---

## Dizin Yapısı

- **`bench.py`**: Ana değerlendirme motoru. Modelleri LM Studio üzerinden yükler, 31 görevi çalıştırır, cevapları ve sandbox çıktılarını kaydeder.
- **`tasks.py`**: 31 adet görevin tanımları, referans çözümleri ve test senaryoları (Python kodlama, SQL sorguları, PowerShell terminal komutları, dosya sistemi ajan görevleri).
- **`grading.py`**: Görev çıktılarını deterministik olarak değerlendiren notlandırıcılar.
- **`tune_gpu.py`**: Modelin VRAM sığma ve üretim hızını (tok/s) optimize etmek için farklı GPU katman oranlarını otomatik ölçen araç.
- **`report.py`**: `results/results.jsonl` dosyasındaki verileri panonun (`dashboard/`) okuduğu JSON yapılarına ve Markdown/CSV tablolarına (`tablolar/`) dönüştürür.
- **`dashboard/index.html`**: Sonuçları görselleştiren radar grafikli, ısı haritalı ve kategori kırılımlı etkileşimli görsel pano.
- **`tablolar/`**: Benchmark özet puanları, kategori ve görev ayrıntılarının Markdown ve CSV formatındaki güncel tabloları.
- **`results/`**: Ham benchmark sonuçları (`results.jsonl`), yapılandırmalar (`configs.jsonl`), model cevapları (`responses/`) ve GPU optimizasyon ölçümleri (`tuning/`).

---

## Kullanım

### 1. Benchmark'ı Çalıştırma
```powershell
# Varsayılan modelleri (knight ve queen) test et
python bench.py

# Belirli bir modeli çalıştır (ai-cli/config.json'daki adıyla)
python bench.py --models king

# Sadece belirli bir düşünme modunu dene (off, auto, on)
python bench.py --modes auto

# Yalnızca belirli görevleri filtrele (örn. kod ve SQL görevleri)
python bench.py --only kod-,sql-

# LM Studio'da o an yüklü olan mevcut modelle çalış (hızlı deneme)
python bench.py --no-load

# Notlandırıcıların doğruluğunu referans çözümlerle sına (model çalıştırmaz)
python bench.py --selftest

# Kayıtlı cevapları güncel notlandırıcılarla yeniden puanla
python bench.py --regrade
```

### 2. GPU VRAM ve Hız Optimizasyonu (`tune_gpu.py`)
Modeli farklı GPU yükleme oranlarıyla (16k context) sınayarak saniyedeki token üretimini ve VRAM tüketimini ölçer:
```powershell
python tune_gpu.py <model-anahtarı> 0.3 0.5 0.7 max
python tune_gpu.py --context 24576 <model-anahtarı> max
```
Ölçüm sonuçları otomatik olarak `results/tuning/<model>.json` dosyasına yazılır.

### 3. Rapor ve Tabloları Güncelleme
```powershell
python report.py
```
Bu komut `results/dashboard/` altındaki JSON verilerini ve `tablolar/` altındaki özet tabloları yeniden derler.

### 4. Sonuç Panosu
`dashboard/index.html` dosyasını tarayıcınızda veya Antigravity Generative UI arayüzünde açarak görsel analizleri inceleyebilirsiniz.
