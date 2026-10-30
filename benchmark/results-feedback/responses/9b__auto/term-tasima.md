# term-tasima · puan 1.00

**Not:** tamam

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

Görev: archive adında bir klasör oluştur ve logs klasörünün doğrudan içindeki .log dosyalarını (alt klasördekiler hariç) bu klasöre taşı.

Bu işi bulunduğum klasörde yapan PowerShell komutunu yaz (tek satır; gerekirse komutları ; ile birleştir). Sadece komutu tek bir ```powershell bloğu içinde ver.

## Cevap

```powershell
New-Item -ItemType Directory -Force -Path archive | ForEach-Object { Move-Item -Path logs/*.log -Destination $_.FullName }
```

## Notlandırılan kod/komut

```
New-Item -ItemType Directory -Force -Path archive | ForEach-Object { Move-Item -Path logs/*.log -Destination $_.FullName }
```
