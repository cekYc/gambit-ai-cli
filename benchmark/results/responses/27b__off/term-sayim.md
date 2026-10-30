# term-sayim · puan 1.00

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

Görev: Bu klasörde ve tüm alt klasörlerde toplam kaç tane .log dosyası var? Komut sadece sayıyı yazdırsın.

Bu işi bulunduğum klasörde yapan PowerShell komutunu yaz (tek satır; gerekirse komutları ; ile birleştir). Sadece komutu tek bir ```powershell bloğu içinde ver.

## Cevap

```powershell
(Get-ChildItem -Path . -Filter *.log -Recurse | Measure-Object).Count
```

## Notlandırılan kod/komut

```
(Get-ChildItem -Path . -Filter *.log -Recurse | Measure-Object).Count
```
