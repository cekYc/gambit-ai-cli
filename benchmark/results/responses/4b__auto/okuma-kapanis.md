# okuma-kapanis · puan 1.00

**Not:** doğru

## Prompt

Aşağıdaki Python kodu çalıştırılınca ekrana tam olarak ne yazdırılır? Kodu kafanda çalıştır. Sadece çıktıyı tek bir ```text bloğu içinde ver.

```python
fs = [lambda: i for i in range(3)]
print([f() for f in fs])
gs = [lambda i=i: i for i in range(3)]
print([g() for g in gs])
```

## Düşünme

Kullanıcı bana bir Python kodu verip çıktısını sormuş. Kodu kafanda çalıştırmam gerekiyor ve çıktıyı tek bir ```text bloğunda vermeliyim.

İlk satır: `fs = [lambda: i for i in range(3)]`

Bu bir liste comprehension'ı. Her iterasyon için bir lambda fonksiyonu oluşturuyor ama burada önemli bir detay var: `i` parametresi tanımlanmış ama lambda'da parametre yok, sadece `i` kullanılıyor. Python'da bu şekilde açık değişken referans alınması yapılıyor.

Aslında bu kodda bir sorun var. `lambda: i` ifadesinde, `i` list comprehension'ın iç değişkeni olarak tanımlanmış ama lambda fonksiyonları gecikmiş (late-binding) çalışır. Yani her lambda aynı `i` değerine erişir - o da son değerdir çünkü Python'da lambalardaki değişken referansı dinamik değil, çağrıldığında değerlendirilir.

Bunu test edelim:
- range(3) -> 0, 1, 2 için iterasyon yapar
- Her iterasyonda lambda oluşturuluyor ama `i` her seferinde yeni bir değer alıyormuş gibi görünüyor
- Ancak `lambda: i` ifadesinin içinden `i` değişkenine referans alınır ve bu değişken list comprehension'ın son değerini tutar

Aslında bu klasik Python lamba kapanış problemi. `fs[0]`, `fs[1]`, `fs[2]` her biri farklı bir lambda fonksiyonu oluşturuyor, ancak bunların hepsi aynı `i` referansını kullanıyor - o da 2'dir (range(3)'in son değeri).

Bu yüzden ilk çıktı: `[2, 2, 2]` olmalı.

İkinci satır: `gs = [lambda i=i: i for i in range(3)]`
Burada parametreye varsayılan değer veriliyor (`i=i`). Bu, her lambda için kendi `i` değerini tutar (default argüman). Her iterasyon için yeni bir lambda oluşturuluyor ve o lamba kendi `i=0`, `i=1`, `i=2` değerlerini tutar.

Bu yüzden ikinci çıktı: `[0, 1, 2]` olmalı.

Tam çıktı:
```text
[2, 2, 2]
[0, 1, 2]
```

Ama bekle, kodu tekrar kontrol edeyim. Kod şu şekilde:
```python
fs = [lambda: i for i in range(3)]
print([f() for f in fs])
gs = [lambda i=i: i for i in range(3)]
print([g() for g in gs])
```

Yani önce `fs` listesi oluşturuluyor, sonra bu lambalardan çağrılar yapılıyor. Lamba fonksiyonları `i` değişkenini kullanıyor ama bu liste comprehension'ın son değeri 2'ye eşit olacaktır (çünkü range(3) en son 2 değerine erişir).

Evet, ilk çıktı için `[2, 2, 2]`, ikinci çıktı için `[0, 1, 2]`.

Sonuç olarak çıktısı tek bir ```text bloğu içinde vermem gerekiyor.


## Cevap

```text
[2, 2, 2]
[0, 1, 2]
```

## Notlandırılan kod/komut

```
[2, 2, 2]
[0, 1, 2]
```
