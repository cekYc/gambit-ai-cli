# term-csv · puan 0.00

**Not:** beklenen 550.0, çıktı ''; hata: ertTo-Int32' terimi bir cmdlet, işlev, betik dosyası veya yürütülebilir program adı olarak tanınmıyor.
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

## Cevap

```powershell
Get-Content data/report.csv | Select-Object -Skip 1 | ForEach-Object { $_.Split(',')[-1] } | ConvertTo-Int32 | Measure-Object -Sum amount | % Sum
```

## Notlandırılan kod/komut

```
Get-Content data/report.csv | Select-Object -Skip 1 | ForEach-Object { $_.Split(',')[-1] } | ConvertTo-Int32 | Measure-Object -Sum amount | % Sum
```
