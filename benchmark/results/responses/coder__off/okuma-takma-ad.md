# okuma-takma-ad · puan 0.00

**Not:** beklenen '[1, 2, 3, 4] [1, 2, 3, 4] [1, 2, 3, 4, 5]', cevap '[1, 2, 3] [1, 2, 3] [1, 2, 3, 5]'

## Prompt

Aşağıdaki Python kodu çalıştırılınca ekrana tam olarak ne yazdırılır? Kodu kafanda çalıştır. Sadece çıktıyı tek bir ```text bloğu içinde ver.

```python
a = [1, 2, 3]
b = a
b += [4]
c = a[:]
c.append(5)
print(a, b, c)
```

## Cevap

Python kodunun çalıştırılması sonucu ekrana aşağıdaki ifadeye benzer bir çıktı yazılır:

```
[1, 2, 3] [1, 2, 3] [1, 2, 3, 5]
```

Yorumlanarak:
1. `a` listesi oluşturulur ve ilk değerleri [1, 2, 3].
2. `b[:] = a` kodu, `a` listesinin bir kopyasını oluşturur ve `b` listesiyle aynı değeri alır ([1, 2, 3]).
3. `c.append(5)` kodu, `c` listesiye [5] değerini ekler.
4. `print(a, b, c)` kodu, `a`, `b` ve `c` listelerini ekrana yazdırır ([1, 2, 3], [1, 2, 3], [1, 2, 3, 5]).

## Notlandırılan kod/komut

```
[1, 2, 3] [1, 2, 3] [1, 2, 3, 5]
```
