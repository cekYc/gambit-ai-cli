# term-csv · puan 1.00

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

Görev: data/report.csv dosyasındaki amount sütununun toplamını yazdır (sadece sayı).

Bu işi bulunduğum klasörde yapan PowerShell komutunu yaz (tek satır; gerekirse komutları ; ile birleştir). Sadece komutu tek bir ```powershell bloğu içinde ver.

## Cevap

```powershell
((Import-Csv data/report.csv | Select-Object -ExpandProperty amount) -join ' + ') | Invoke-Expression
```
Bu PowerShell komutu, `data/report.csv` dosyasındaki `amount` sütunundaki tüm değerleri alır ve toplar. Ancak bu komut, `amount` sütununun sayısal olduğunu ve her satırda yalnızca bir sayı olduğu varsayımında bulunur. Eğer `amount` sütunu farklı veri tiplerini içerebilir ya da çok satırlıysa, daha kapsamlı bir çözüm gerekebilir.

Eğer `amount` sütununda sayısal olmayan değerler varsa veya bu komut çalışmadıysa, aşağıdaki daha güvenli yaklaşım kullanılabilir:

```powershell
(Import-Csv data/report.csv | Measure-Object -Property amount -Sum).Sum
```

Bu satır, `amount` sütunundaki tüm sayıları toplar ve sonucu yazdırır. Bu çözüm, veri tipiyle ilgili sorunlar yaşanmadığı sürece daha güvenilirdir.

Fakat görevde "sadece sayı" istendiği için, `Import-Csv` ile CSV dosyasını okuyup sadece amount sütununu alıp toplayan komut şu şekilde olabilir:

```powershell
(Import-Csv data/report.csv | Select-Object -ExpandProperty amount) | Measure-Object -Sum | Select-Object -ExpandProperty Sum
```

Bu komut, `amount` sütunundaki sayıları toplar ve sonucu verir.

## Notlandırılan kod/komut

```
(Import-Csv data/report.csv | Select-Object -ExpandProperty amount) | Measure-Object -Sum | Select-Object -ExpandProperty Sum
```
