# term-grep · puan 0.00

**Not:** beklenen '6', çıktı ''; hata: üştürülemiyor. Hata: "The input string ',' was not in a correct format."
InvalidArgument: “," değerini "System.Int32" türüne dönüştürülemiyor. Hata: "The input string ',' was not in a correct format."

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

Görev: logs klasöründeki (alt klasörler dahil) tüm .log dosyalarında 'ERROR' geçen satırların toplam sayısını yazdır (sadece sayı).

Bu işi bulunduğum klasörde yapan PowerShell komutunu yaz (tek satır; gerekirse komutları ; ile birleştir). Sadece komutu tek bir ```powershell bloğu içinde ver.

## Cevap

```powershell
(Get-ChildItem -Path .\logs -Include *.log,*.log -Recurse | Select-Object -Expand FullName) | ForEach-Object { (Select-String -Path $_ -Pattern 'ERROR' | Measure-Object).Count } | ForEach-Object { "$_" + "," } | Select-String -Pattern ',?$' -AllMatches | ForEach-Object { [int]($_.Matches.Groups[0].Value) }
```

## Notlandırılan kod/komut

```
(Get-ChildItem -Path .\logs -Include *.log,*.log -Recurse | Select-Object -Expand FullName) | ForEach-Object { (Select-String -Path $_ -Pattern 'ERROR' | Measure-Object).Count } | ForEach-Object { "$_" + "," } | Select-String -Pattern ',?$' -AllMatches | ForEach-Object { [int]($_.Matches.Groups[0].Value) }
```
