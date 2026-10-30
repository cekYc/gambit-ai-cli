# okuma-siralama · puan 0.00

**Not:** beklenen "['elma', 'kiraz', 'muz', 'armut']\n7", cevap "['armut', 'muz', 'elma', 'kiraz']\n4"

## Prompt

Aşağıdaki Python kodu çalıştırılınca ekrana tam olarak ne yazdırılır? Kodu kafanda çalıştır. Sadece çıktıyı tek bir ```text bloğu içinde ver.

```python
data = {"elma": 3, "armut": 1, "kiraz": 3, "muz": 2}
order = sorted(data, key=lambda k: (-data[k], k))
print(order)
print(sum(v for k, v in data.items() if "a" in k))
```

## Cevap

Görevi tamamen anladım. Python kodunun ekrana yazdırdığı sonuçlar şunlardır:

output:
```
['armut', 'muz', 'elma', 'kiraz']
4
```

## Notlandırılan kod/komut

```
['armut', 'muz', 'elma', 'kiraz']
4
```
