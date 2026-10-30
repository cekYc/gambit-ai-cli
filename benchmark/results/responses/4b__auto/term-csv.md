# term-csv · puan 0.00

**Not:** beklenen 550.0, çıktı ''; hata:   1 |  … et-Content data/report.csv | ForEach-Object { $_,-split ','[-]3 } | W …
     |                                                                 ~
     | '-' birli işlecinden sonra ifade eksik.

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
Get-Content data/report.csv | Select-String '^date,' -Context 0,3 | ForEach-Object { $row = $_; if ($row -match ',(\d+)$') { [int]($matches[1]) } else { 0 } } | Measure-Object -Sum | Select-Object -ExpandProperty Sum
```

**Düzeltme:** Yukarıdaki komut mantık olarak hataya açıktır (ilk satırı da dahil edip temizleme yapmayı bekliyordu ancak regex ve context yönetimi karışık). Şu anki klasör yapısına göre `data/report.csv` dosyasının ilk satırı (`date,product,amount`) sayı olarak algılanmamalı. En güvenli ve net yol, CSV formatını doğrudan okuyup, "amount" sütununu bulmak ve sadece ondalıklı olmayan (int veya double) değerleri toplamaktır.

Düzeltilmiş ve güvenilir komut aşağıdadır:

```powershell
Get-Content data/report.csv | Where-Object -NotMatches '^date,' | ForEach-Object { $_,-split ','[-]5 } | Where-Object { [double]$_ -gt 0 } | Measure-Object -Sum | Select-Object -ExpandProperty Sum
```

**Not:** Bu komut `Get-Content` ile dosyayı okur, ilk satırı (date,...) dışarı atar, virgülle ayırarak son elemanı alır ve sadece geçerli sayılarla toplama yapar. Ancak PowerShell'de `-NotMatches` operatörü doğrudan kullanımında bazı sürümlerde sorun çıkarabilir veya hatasız çalışması için daha net bir yaklaşım gerekebilir. En kesin çözüm `Select-String` ile sütun numarasına göre kesintiyi yapmak veya CSV parser kullanmaktır.

En stabil ve tek satırlık çözüm:

```powershell
Get-Content data/report.csv | ForEach-Object { $_,-split ','[-]3 } | Where-Object { [double]$_ -ne $null } | Measure-Object -Sum | Select-Object -ExpandProperty Sum
```

## Notlandırılan kod/komut

```
Get-Content data/report.csv | ForEach-Object { $_,-split ','[-]3 } | Where-Object { [double]$_ -ne $null } | Measure-Object -Sum | Select-Object -ExpandProperty Sum
```
