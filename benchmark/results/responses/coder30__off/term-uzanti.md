# term-uzanti · puan 1.00

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

Görev: data klasöründeki tüm .txt dosyalarının uzantısını .md olarak değiştir (içerikleri aynı kalsın).

Bu işi bulunduğum klasörde yapan PowerShell komutunu yaz (tek satır; gerekirse komutları ; ile birleştir). Sadece komutu tek bir ```powershell bloğu içinde ver.

## Cevap

```powershell
Get-ChildItem -Path data -Name "*.txt" | ForEach-Object { Rename-Item -Path "data\$_.txt" -NewName "$_.md" }
```
Bu PowerShell komutu, `data` klasöründeki tüm `.txt` dosyalarının uzantısını `.md` olarak değiştirir. Komut, her bir `.txt` dosyasını bulup, aynı adla ama farklı uzantıyla yeniden isimlendirir; içerikler aynı kalır.

Ancak bu komutun çalışması için `data` klasöründe `.txt` dosyalarının bulunduğu varsayılır ve `Get-ChildItem` ile yalnızca dosya adları alınarak `Rename-Item` ile iş yapılır. Dilersen, daha güvenli bir versiyonu da sunabilirim:
```powershell
Get-ChildItem -Path data -Filter "*.txt" | ForEach-Object { Rename-Item -LiteralPath $_.FullName -NewName ($_.BaseName + ".md") }
```
Bu sürümde `$_` nesnesinin tam yolu (`FullName`) kullanıldığı için daha güvenlidir.

## Notlandırılan kod/komut

```
Get-ChildItem -Path data -Filter "*.txt" | ForEach-Object { Rename-Item -LiteralPath $_.FullName -NewName ($_.BaseName + ".md") }
```
