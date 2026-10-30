# okuma-siralama · puan 1.00

**Not:** doğru

## Prompt

Aşağıdaki Python kodu çalıştırılınca ekrana tam olarak ne yazdırılır? Kodu kafanda çalıştır. Sadece çıktıyı tek bir ```text bloğu içinde ver.

```python
data = {"elma": 3, "armut": 1, "kiraz": 3, "muz": 2}
order = sorted(data, key=lambda k: (-data[k], k))
print(order)
print(sum(v for k, v in data.items() if "a" in k))
```

## Düşünme

Kullanıcı bana Python kodunun çıktısını soruyor. Kodu dikkatlice analiz etmem gerekiyor.

İlk satırdaki veri yapısı:
- `data = {"elma": 3, "armut": 1, "kiraz": 3, "muz": 2}`

Bu bir sözlük (dictionary) ve anahtarlar ile değerleri eşleştiriyor.

İkinci satır:
```python
order = sorted(data, key=lambda k: (-data[k], k))
print(order)
```
- `sorted(data, ...)` - data dictionary'ini sıralıyor ama burada bir sorun var!
- Python'da `dict`'in `items()` metodu yok, sadece `sorted(dict.keys())` veya `sorted(dict.items())` kullanılabilir.
- Ancak `sorted(data, key=...)` ifadesi dictionary keyleri için sıralama yapıyor (çünkü `data` bir dict ve sorted() fonksiyonu, iterable olarak verildiğinde dictionary'yi iterasyon yapar).
- Ama bu doğru çalışacak çünkü Python'da dictionary'ye `sorted()` uygulanırken default olarak keylerini iter eder.

Sıralama mantığı:
- `key=lambda k: (-data[k], k)` - önce değerlerin tersi, sonra anahtarın alfabetik sırası

Veriler:
- "elma": 3 → (-3, 'e')
- "armut": 1 → (-1, 'a')
- "kiraz": 3 → (-3, 'k')
- "muz": 2 → (-2, 'm')

Sıralama:
1. -1 en büyük negatif sayı (en küçük değer), sonra -2, -3 en küçüğü
   - En yüksek değer öncelikli: (-3) > (-2) > (-1) değil mi? Hayır! 
   
   Python'da sıralamada daha düşük değerin önce gelmesi gerekir. 
   
   Veri yapısı `(-data[k], k)` şeklinde olmalı, bu da en yüksek değerlerin ilk sırada olması anlamına gelir:
   - "elma": 3 → (-3) - en düşük negatif sayı (en büyük pozitif)
   - "kiraz": 3 → (-3) - aynı değer
   - "muz": 2 → (-2)
   - "armut": 1 → (-1) - en yüksek negatif

   Sıralama:
   1. elma (elma: 3) ve kiraz (kiraz: 3) değeri aynı, alfabetik sıraya göre
      - 'e' < 'k', bu yüzden "elma" önce gelir
   2. muz (muz: 2)
   3. armut (armut: 1)

   Çıktı: `['elma', 'kiraz', 'muz', 'armut']`

İkinci satır:
```python
print(sum(v for k, v in data.items() if "a" in k))
```
- Data içindeki key'ler "a" içerenleri filtreliyor:
  - "elma": "e", "l", "m", "a" → "a" var! ✅
  - "armut": "a", "r", "m", "u", "t" → "a" var! ✅
  - "kiraz": "k", "i", "r", "a", "z" → "a" var! ✅
  - "muz": "m", "u", "z" → "a" yok ❌

- Değerler: elma=3, armut=1, kiraz=3
- Toplam: 3 + 1 + 3 = 7

Sonuç çıktısı:
```text
['elma', 'kiraz', 'muz', 'armut']
7
```

Bunu tek bir ```text bloğunda vereceğim.


## Cevap

```text
['elma', 'kiraz', 'muz', 'armut']
7
```

## Notlandırılan kod/komut

```
['elma', 'kiraz', 'muz', 'armut']
7
```
