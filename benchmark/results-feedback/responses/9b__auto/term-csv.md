# term-csv · puan 0.00

**Not:** beklenen 550.0, çıktı '0'

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
Get-Content data/report.csv | Select-String -Pattern '^\d+,\s*\d+,' | ForEach-Object { $_.Matches.Value.Split(',')[2] } | Add-Type -MemberDefinition 'public static int Parse(string s) => Convert.ToInt32(s);' -Name 'Helper' -Namespace 'MathExt' 2>$null; $total = (Get-Content data/report.csv | Select-String -Pattern '^\d+,\s*\d+,' | ForEach-Object { $_.Matches.Value.Split(',')[2] } | Measure-Object -Sum).Sum; Write-Output $total
```

## Notlandırılan kod/komut

```
Get-Content data/report.csv | Select-String -Pattern '^\d+,\s*\d+,' | ForEach-Object { $_.Matches.Value.Split(',')[2] } | Add-Type -MemberDefinition 'public static int Parse(string s) => Convert.ToInt32(s);' -Name 'Helper' -Namespace 'MathExt' 2>$null; $total = (Get-Content data/report.csv | Select-String -Pattern '^\d+,\s*\d+,' | ForEach-Object { $_.Matches.Value.Split(',')[2] } | Measure-Object -Sum).Sum; Write-Output $total
```
