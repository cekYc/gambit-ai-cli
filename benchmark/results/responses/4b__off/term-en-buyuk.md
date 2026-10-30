# term-en-buyuk · puan 0.00

**Not:** beklenen 'big.bin', çıktı ''; hata: Select-Object: "Length" özelliği bulunamadı.
Select-Object: "Length" özelliği bulunamadı.
Select-Object: "Length" özelliği bulunamadı.

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
Get-ChildItem -Recurse | Select-Object -ExpandProperty Length | Sort-Object -Descending | Select-Object -First 1 | ForEach-Object { $_.Name }
```

## Notlandırılan kod/komut

```
Get-ChildItem -Recurse | Select-Object -ExpandProperty Length | Sort-Object -Descending | Select-Object -First 1 | ForEach-Object { $_.Name }
```
