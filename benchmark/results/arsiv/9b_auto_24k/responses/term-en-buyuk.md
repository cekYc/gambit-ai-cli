# term-en-buyuk · puan 1.00

**Not:** doğru

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

## Cevap

```powershell
Get-ChildItem -Recurse | Measure-Object -Property Length -Sum | Select-Object -ExpandProperty Count | ForEach-Object { $_ } # Yanlış yaklaşım, düzeltme: Get-ChildItem -Recurse | Sort-Object Length -Descending | Select-Object -First 1 Name
```

Düzeltilmiş ve doğru tek satır komutu:

```powershell
Get-ChildItem -Recurse | Sort-Object Length -Descending | Select-Object -First 1 Name
```

## Notlandırılan kod/komut

```
Get-ChildItem -Recurse | Sort-Object Length -Descending | Select-Object -First 1 Name
```
