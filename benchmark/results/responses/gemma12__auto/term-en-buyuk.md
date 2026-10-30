# term-en-buyuk · puan 0.00

**Not:** beklenen 'big.bin', çıktı '----------'

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
Get-ChildItem -Recurse -File | Sort-Object Length -Descending | select -First 1 .FullName`n
```

**Açıklama:** `Get-ChildItem -Recurse -File` tüm klasörleri ve alt kırılımları tarayıp sadece dosyaları getirir (`data/big.bin` de dahil). Sonra her dosyanın boyutuna göre büyükten küçüğe sıralar ve en üsttekini seçer. `select -First 1 .FullName` komutu, sonucu raporlanabilir tam bir yol olarak döndürür (sadece dosya adı istenirse `.Name` kullanılabilir ama koro halinde çalışacak yapıda full path her zaman güvenlidir).

## Notlandırılan kod/komut

```
Get-ChildItem -Recurse -File | Sort-Object Length -Descending | select -First 1 .FullName`n
```
