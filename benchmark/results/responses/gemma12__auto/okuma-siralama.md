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

Goal: determine the exact output of the provided Python snippet when executed.

Edge cases/details to track:
- `data`: dict with 4 keys ("elma", "armut", "kiraz", "muz").
- `sorted(data, key=lambda k: (-data[k], k))`: sort by value descending (negated), then alphabetically ascending for ties. Values are [3,1,3,2]. Ties at 3 between "elma" and "kiraz"; alphabetical order gives ["elma", "kiraz"]. Then muz (2), armut (1). Order: ['elma', 'kiraz', 'muz', 'armut']
- `sum(v for k, v in data.items() if "a" in k)`: keys containing "a": elma(3), armut(1), kiraz(3). Müz does not contain a. Sum = 3 + 1 + 3 = 7

Output is two print statements on separate lines.


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
