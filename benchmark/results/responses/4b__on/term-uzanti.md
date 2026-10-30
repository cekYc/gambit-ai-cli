# term-uzanti · puan 0.00

**Not:** .md dosyası oluşmamış; hata: Rename-Item: ' $_.Name -replace '\.txt$', '.md' ' bağımsız değişkenini kabul eden bir konumsal parametre bulunamadı.

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

## Düşünme

Kullanıcı, mevcut klasör yapısında `data` dizinindeki `.txt` dosyalarının uzantılarını `.md` olarak değiştirmemi istiyor. İçerik aynı kalmalı.

Bunu yapmak için PowerShell 7 (pwsh) kullanacağım. Tek satır veya virgülle birleştirilmiş komutlar istenmiş, ama `data/report.csv` dosyasının ilk satırı hakkında bilgi vermesi gerekebilir, ancak bu görev ile doğrudan ilgili değil. Asıl odak noktası `.txt` dosyalarının uzantısını değiştirme işlemi.

PowerShell'de bir dizin içindeki dosya uzantılarını değiştirmek için `Get-ChildItem` ve `Rename-Item` kullanılır.

Şimdi, komutu düşünelim:
1.  `data` klasörünü bulmak için `.\data`.
2.  İçindeki tüm dosyaları seçmek için `Get-ChildItem .\data -Include *.txt`.
3.  Her bir dosyanın ismini `.md` uzantısına dönüştürmek için yeni isim oluşturmalıyız.
4.  Dosya adı ve uzantısı olarak değiştirme işlemi için `Rename-Item` kullanılır.

İşlem şu şekilde olabilir:
```powershell
Get-ChildItem data\*.txt | Rename-Item { $_.Name -replace '\.txt$', '.md' }
```

Bu komut, uzantıyı `.md` olarak değiştirir ve içerik aynı kalır.

PowerShell 7 (pwsh) için bu mantık geçerlidir.

Ayrıca `Rename-Item` yerine `-Path` parametresi de kullanılabilir ama yukarıdaki yöntem daha okunaklıdır.
Alternatif bir yaklaşım:
```powershell
Get-ChildItem data\*.txt | ForEach-Object { Rename-Item $_ . -NewName ($_.BaseName + ".md") }
```

Bu da aynı sonucu verir, ancak daha uzun olabilir. `Replace` kullanımı daha temizdir.

Son olarak, kullanıcı "tek satır; gerekirse komutları ; ile birleştir" demiş. Ancak genellikle tek bir komutu basitçe vermek yeterlidir. Yukarıdaki tek bir Pipeline komutu yeterli olacaktır.

```powershell
Get-ChildItem data\*.txt | Rename-Item { $_.Name -replace '\.txt$', '.md' }
```

Bu, `.txt` uzantısını olan dosyaları seçer ve adlarını `.md` olarak değiştirir. Dosya içeriği etkilenmez çünkü sadece isminin (uzantısının) değişmesi isteniyor.

Tekrar kontrol edelim: `data/report.csv` dosyası ile ilgili bilgi verildi, ama oradaki `.txt` dosyaları üzerinde işlem yapılması gerekiyor. Bu komut doğru çalışacak.


## Cevap

```powershell
Get-ChildItem data\*.txt | Rename-Item { $_.Name -replace '\.txt$', '.md' }
```

## Notlandırılan kod/komut

```
Get-ChildItem data\*.txt | Rename-Item { $_.Name -replace '\.txt$', '.md' }
```
