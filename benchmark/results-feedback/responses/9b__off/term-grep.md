# term-grep · puan 0.00

**Not:** 2. deneme: beklenen '6', çıktı '1'

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

## Düşünme



--- 2. deneme ---



## Cevap

```powershell
Get-ChildItem -Path logs -Recurse -Filter *.log | Select-String -Pattern 'ERROR' | Measure-Object -Line | Select-Object -ExpandProperty Count
```

--- Geri bildirim ---

Bu komut çalıştırılınca şu sonuç alındı:
```
çıkış kodu: 1

[stderr]
Select-Object: "Count" özelliği bulunamadı.
```
Hatayı düzelt ve düzeltilmiş komutu ilk istekteki biçimde ver.

--- 2. deneme ---

```powershell
Get-ChildItem -Path logs -Recurse -Filter *.log | Select-String -Pattern 'ERROR' | Measure-Object -Line | ForEach-Object { $_.Count }
```

## Notlandırılan kod/komut

```
Get-ChildItem -Path logs -Recurse -Filter *.log | Select-String -Pattern 'ERROR' | Measure-Object -Line | ForEach-Object { $_.Count }
```
