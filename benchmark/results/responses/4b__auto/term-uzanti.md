# term-uzanti · puan 0.00

**Not:** .md dosyası oluşmamış; hata: Rename-Item: Belirtilen hedef bir yol veya cihaz adını temsil ettiğinden, yeniden adlandırılamıyor.
Rename-Item: Belirtilen hedef bir yol veya cihaz adını temsil ettiğinden, yeniden adlandırılamıyor.

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
Get-ChildItem -Path .\data -Filter *.txt | ForEach-Object { Rename-Item $_ "($_.Name -replace '\.txt$', '.md')"; $_ }
```

## Notlandırılan kod/komut

```
Get-ChildItem -Path .\data -Filter *.txt | ForEach-Object { Rename-Item $_ "($_.Name -replace '\.txt$', '.md')"; $_ }
```
