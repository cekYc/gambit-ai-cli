# term-en-buyuk · puan 0.00

**Not:** beklenen 'big.bin', çıktı 'readme.md'

## Prompt

Windows'ta PowerShell 7 (pwsh) kullanıyorum. Bulunduğum klasörün yapısı şöyle:
```text
.
├── logs
│   ├── app1.log
│   ├── app2.log
│   └── old
│       └── app0.log
├── data
│   ├── notes.txt
│   ├── todo.txt
│   ├── report.csv
│   ├── big.bin
│   └── image.png
└── readme.md
```
data/report.csv dosyasının ilk satırı: date,product,amount

Görev: Bu klasördeki (alt klasörler dahil) en büyük dosyanın sadece adını yazdır.

Bu işi bulunduğum klasörde yapan PowerShell komutunu yaz (tek satır; gerekirse komutları ; ile birleştir). Sadece komutu tek bir ```powershell bloğu içinde ver.

## Düşünme

Kullanıcı, mevcut klasör yapısında en büyük dosyanın ismini çıkarmamı istiyor. Verilen klasör yapısına bakarak:

```text
.
├── logs
│   ├── app1.log
│   ├── app2.log
│   └── old
│       └── app0.log
├── data
│   ├── notes.txt
│   ├── todo.txt
│   ├── report.csv
│   ├── big.bin
│   └── image.png
└── readme.md
```

Tüm dosyaları kontrol etmem gerekiyor. En büyük dosya hangisi? Dosya boyutlarını bilmiyorum ama senaryoya göre en büyük dosyanın ismini çıkarmam gerekiyor.

Windows'ta PowerShell 7 için en büyük dosyayı bulmak için:
1. `Get-ChildItem` veya `ls -R` ile tüm dosyaları almalıyım (sadece dosyaları, klasörleri hariç)
2. Her bir dosyanın boyutunu getirmeliyim
3. En büyük olanı filtrelemem gerekiyor

PowerShell'de en iyi yol:
```powershell
Get-ChildItem -Recurse | Where-Object { $_.PSIsContainer -eq $false } | Sort-Object Length -Descending | Select-Object -First 1 | Select-Object -ExpandProperty Name
```

Bu komut:
- `Get-ChildItem -Recurse` ile tüm dizinleri ve alt dizinlerindeki dosyaları alır
- `Where-Object { $_.PSIsContainer -eq $false }` ile sadece dosyalara filtreler (klasör hariç)
- `Sort-Object Length -Descending` ile uzunluğa göre azalandırır sıralar
- `Select-Object -First 1` ile ilk elemanı alır
- `Select-Object -ExpandProperty Name` ile sadece isimini yazdırır

Ama daha kısa ve temiz bir yol:

```powershell
(Get-ChildItem -Recurse -File | Sort-Object Length -Descending).Name
```

Bu tek satırda çalışır. `Get-ChildItem -Recurse -File` tüm dosyaları getirir, sonra Longuza göre sıralar ve ilk elemanın ismini alır.

Şimdi bu komutu tek bir powershell bloğu içinde sunacağım:

```powershell
(Get-ChildItem -Recurse -File | Sort-Object Length -Descending).Name
```

Bu en büyük dosyanın sadece adını yazdırır.


## Cevap

```powershell
(Get-ChildItem -Recurse -File | Sort-Object Length -Descending).Name
```

## Notlandırılan kod/komut

```
(Get-ChildItem -Recurse -File | Sort-Object Length -Descending).Name
```
