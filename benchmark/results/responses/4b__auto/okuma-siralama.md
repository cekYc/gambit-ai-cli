# okuma-siralama · puan 0.00

**Not:** beklenen "['elma', 'kiraz', 'muz', 'armut']\n7", cevap "['elma', 'kiraz', 'muz', 'armut']\n4"

## Prompt

Aşağıdaki Python kodu çalıştırılınca ekrana tam olarak ne yazdırılır? Kodu kafanda çalıştır. Sadece çıktıyı tek bir ```text bloğu içinde ver.

```python
data = {"elma": 3, "armut": 1, "kiraz": 3, "muz": 2}
order = sorted(data, key=lambda k: (-data[k], k))
print(order)
print(sum(v for k, v in data.items() if "a" in k))
```

## Düşünme

The user is asking me to mentally execute this Python code and determine what would be printed. Let me analyze it step by step.

```python
data = {"elma": 3, "armut": 1, "kiraz": 3, "muz": 2}
order = sorted(data, key=lambda k: (-data[k], k))
print(order)
print(sum(v for k, v in data.items() if "a" in k))
```

First line: Creates a dictionary with keys as fruits and values as counts.

Second line: Sorts the dictionary keys based on two criteria:
1. First by negative value (so higher values come first) using `-data[k]`
2. Second by key name alphabetically for ties (using `k`)

Let's calculate the sort order:
- "elma": 3 → (-3, "elma")
- "armut": 1 → (-1, "armut")
- "kiraz": 3 → (-3, "kiraz")
- "muz": 2 → (-2, "muz")

Sorted by value descending (so -3 comes before -2 which comes before -1), then alphabetically:
- Both "elma" and "kiraz" have value 3. Alphabetically: "elma" < "kiraz" so elma comes first
- Then "armut" with value 1

Wait, let me reconsider. The sort is by `-data[k]` (negative), which means higher values come first when sorted ascendingly. So:
- -3 (for elma and kiraz)
- -2 (for muz)  
- -1 (for armut)

Within the same value (-3 for both "elma" and "kiraz"), it sorts alphabetically by key `k`:
- "elma" comes before "kiraz" alphabetically

So the sorted order is: ["elma", "kiraz", "muz", "armut"]


  
The output prints this list, then filters for keys containing 'a': "armut" (value 1) and "elma" (value 3), summing to 4.


## Cevap

```text
['elma', 'kiraz', 'muz', 'armut']
4
```

## Notlandırılan kod/komut

```
['elma', 'kiraz', 'muz', 'armut']
4
```
