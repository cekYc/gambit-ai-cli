# okuma-takma-ad · puan 0.00

**Not:** beklenen '[1, 2, 3, 4] [1, 2, 3, 4] [1, 2, 3, 4, 5]', cevap '[1, 2, 3, 4] [1, 2, 3, 4] [1, 2, 3, 5]'

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

```text
[1, 2, 3, 4] [1, 2, 3, 4] [1, 2, 3, 5]
```

## Notlandırılan kod/komut

```
[1, 2, 3, 4] [1, 2, 3, 4] [1, 2, 3, 5]
```
