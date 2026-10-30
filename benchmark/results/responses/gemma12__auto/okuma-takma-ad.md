# okuma-takma-ad · puan 1.00

**Not:** doğru

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

## Düşünme

Goal: determine the exact output of the provided Python snippet after mental execution and return only that as plain text in one ```text block.

Edge cases: list assignment vs mutation; slice copy; `+=` on a shared reference.

Execution trace:
1. `a = [1, 2, 3]` → new list object at ref 'a' ([1, 2, 3]).
2. `b = a` → both names point to the same list object.
3. `b += [4]` → in-place extend on that shared object; b is now [1, 2, 3, 4], and so is a. (a copy would be `b = a + [4]`).
4. `c = a[:]` → shallow slice creates a new list with current values: [1, 2, 3, 4].
5. `c.append(5)` appends only to the new list: c becomes [1, 2, 3, 4, 5].

Output format for print(a, b, c): tuple representation per Python's str formatting — each list shown with brackets and commas, separated by a space between arguments.
Result: [1, 2, 3, 4] [1, 2, 3, 4] [1, 2, 3, 4, 5]

Double-check: b += is in-place extend on the same object as a; slicing c creates a copy so appending to c does not affect a or b. Correct.


## Cevap

```text
[1, 2, 3, 4] [1, 2, 3, 4] [1, 2, 3, 4, 5]
```

## Notlandırılan kod/komut

```
[1, 2, 3, 4] [1, 2, 3, 4] [1, 2, 3, 4, 5]
```
