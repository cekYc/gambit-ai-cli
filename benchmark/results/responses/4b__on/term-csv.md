# term-csv · puan 0.00

**Not:** beklenen 550.0, çıktı ''; hata: Skip: 'Skip' terimi bir cmdlet, işlev, betik dosyası veya yürütülebilir program adı olarak tanınmıyor.
Adın yazımını denetleyin veya yol eklenmişse yolun doğru olduğundan emin olun ve yeniden deneyin.

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

Görev: data/report.csv dosyasındaki amount sütununun toplamını yazdır (sadece sayı).

Bu işi bulunduğum klasörde yapan PowerShell komutunu yaz (tek satır; gerekirse komutları ; ile birleştir). Sadece komutu tek bir ```powershell bloğu içinde ver.

## Düşünme

Kullanıcı, mevcut klasör yapısında bulunan data/report.csv dosyasındaki amount sütununun toplamını yazdırmamı istiyor. CSV dosyasının ilk satırı başlık satırı olduğunu belirtmiş (date,product,amount).

PowerShell'de bu işlemi gerçekleştirmek için:
1. Get-Content ile dosyayı okumalıyız
2. İlk satırı atlamalıyız (başlık satırı)
3. amount sütununu almalıyız
4. Sayısal değerleri toplamalıyız

PowerShell 7'de bu işi tek satırda yapmanın birkaç yolu var:

1. Get-Content + Select-String/Select-Object ile sütun seçimi
2. CSV parse etme işlemi
3. İki veya daha fazla komutu ; ile birleştirme

En temiz yol:
```powershell
Get-Content .\data\report.csv | Select-Object -Index 1,2... | Measure-Object -Sum
```

Aslında daha iyi ve temiz yöntem:
```powershell
(Get-Content .\$data\report.csv | Select-String '^.*,\d+,\d+$')[{param($c); $c.Split(',')[-1]}] | ForEach-Object { $_ } | Measure-Object -Sum
```

Hatta en basit ve temiz yöntem:
```powershell
(Get-Content .\data\report.csv).Skip(1) | Select-String '\d+' -AllMatches | ForEach-Object { $_.Matches[0].Value } | Measure-Object -Sum | Select-Object Sum
```

En basit yöntem aslında CSV dosyasını düzgün okumak:
```powershell
(Get-Content .\data\report.csv).Skip(1) | Where-Object { ($_ -split ',')[2] -match '^\d+$' } | Measure-Object -Sum | Select-Object Sum


```

Ya da daha basit bir yol:
```powershell
Get-Content .\data\report.csv -Encoding UTF8 | Select-String '^.*,\d+,' -After 0 | ForEach-Object { ($_ -split ',')[2] } | Measure-Object -Sum
```

PowerShell'de CSV dosyasını okumak için en temiz yöntem:
```powershell
Get-Content .\data\report.csv -Encoding UTF8 | Select-String '^.*,\d+,' -After 0 | ForEach-Object { ($_ -split ',')[2] } | Measure-Object -Sum
```

En iyi çözüm aslında CSV parser kullanmak ama PowerShell'de basit bir yol:

```powershell
(Get-Content .\data\report.csv).Skip(1) | Select-String '\d+' -AllMatches | ForEach-Object { $_.Matches[0].Value } | Measure-Object -Sum
```

Aslında en temiz yöntem:
```powershell
Get-Content .\data\report.csv | Skip 1 | Select-String '\d+\s*,' -AllMatches | ForEach-Object { ($_ -split ',')[2] } | Measure-Object -Sum
```

Hadi bunu basitleştirelim. En temiz yol:

```powershell
(Get-Content .\data\report.csv).Skip(1) | Select-String '\d+\s*,' -AllMatches | ForEach-Object { $_.Matches[0].Value } | Measure-Object -Sum
```

Bu yeterli.


## Cevap

```powershell
Get-Content .\data\report.csv | Skip 1 | Where-Object { ($_ -split ',')[2] -match '^\d+$' } | Measure-Object -Sum | Select-Object Sum
```

## Notlandırılan kod/komut

```
Get-Content .\data\report.csv | Skip 1 | Where-Object { ($_ -split ',')[2] -match '^\d+$' } | Measure-Object -Sum | Select-Object Sum
```
