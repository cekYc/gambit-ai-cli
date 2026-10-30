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

## Düşünme

Kullanıcının isteği: PowerShell 7'de, mevcut konumdaki tüm alt klasörlerdeki .log dosyalarını sayan ve sadece sayıyı yazdıran tek satır PowerShell komutu isteniyor.

Verilen klasör yapısına göre:
- logs/app1.log (1)
- logs/app2.log (2)
- logs/old/app0.log (3)

Toplam 3 adet .log dosyası var.

Komut gereksinimleri:
- Tek satır
- Gerekirse ; ile birleştirilebilecek komutlar
- Sadece sayıyı yazdırsın
- ```powershell bloğu içinde verilmeli

PowerShell'de bu işlem için birkaç seçenek var:
1. Get-ChildItem -Recurse | Where-Object { $_.Extension -eq ".log" } | Measure-Object -Property Name -Sum.Count (bu da çalışır ama biraz uzun)
2. Get-ChildItem -Recurse *.log | Measure-Object -Line

Daha temiz ve hızlı olan: `Get-ChildItem -Path . -Filter "*.log" -Recurse | Measure-Object -Line`. 

Aslında daha basit bir yaklaşım var: `Get-ChildItem -Path . -Filter "*.log" -Recurse | Select-Count`

En iyi çözüm: `(Get-ChildItem -Path . -Filter '*.log' -Recurse).Count`

Bu, tüm alt klasörlerdeki .log dosyalarını sayar ve sadece sayıyı döndürür. Tek satırda olur ve gereksiz çıktıları içermez.

Ayrıca kullanıcı sadece komutu istiyor, çıktıyı yazdırmak için gerek yok - sadece komutun kendisi yeterli.


## Cevap

```powershell
(Get-ChildItem -Path . -Filter '*.log' -Recurse).Count
```

## Notlandırılan kod/komut

```
(Get-ChildItem -Path . -Filter '*.log' -Recurse).Count
```
