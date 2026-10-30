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

*   `data = {"elma": 3, "armut": 1, "kiraz": 3, "muz": 2}`

    *   `order = sorted(data, key=lambda k: (-data[k], k))`
    *   The `sorted()` function iterates over the keys of the dictionary (`elma`, `armut`, `kiraz`, `muz`).
    *   The sorting key is a tuple: `(-value, key_name)`. This means it sorts primarily by value in descending order (due to `-data[k]`) and secondarily by the key name in ascending alphabetical order.

    Let's evaluate the keys based on the lambda function:
    *   `elma`: `data["elma"] = 3` -> Key tuple: `(-3, "elma")`
    *   `armut`: `data["armut"] = 1` -> Key tuple: `(-1, "armut")`
    *   `kiraz`: `data["kiraz"] = 3` -> Key tuple: `(-3, "kiraz")`
    *   `muz`: `data["muz"] = 2` -> Key tuple: `(-2, "muz")`

    Now, sort these tuples:
    1.  `(-3, "elma")` vs `(-3, "kiraz")`: `-3 == -3`, so compare strings `"elma"` and `"kiraz"`. `"elma"` comes before `"kiraz"`. Order: `("elma", "kiraz")`.
    2.  Next is `(-2, "muz")`.
    3.  Last is `(-1, "armut")`.

    Sorted order of keys: `['elma', 'kiraz', 'muz', 'armut']`

    *   `print(order)` -> Output: `['elma', 'kiraz', 'muz', 'armut']`

    *   `sum(v for k, v in data.items() if "a" in k)`
    *   Iterate through items:
        *   `("elma", 3)`: Does `"a"` exist in `"elma"`? Yes (`elma`). Value = 3.
        *   `("armut", 1)`: Does `"a"` exist in `"armut"`? Yes (`armut`). Value = 1.
        *   `("kiraz", 3)`: Does `"a"` exist in `"kiraz"`? Yes (`kiraz`). Value = 3.
        *   `("muz", 2)`: Does `"a"` exist in `"muz"`? No.

    *   Sum of values where "a" is in the key: `3 + 1 + 3 = 7`.

    *   Line 1: `['elma', 'kiraz', 'muz', 'armut']`
    *   Line 2: `7`

    Wait, let me double-check the "a" in keys logic.
    `elma`: e-l-m-**a** (Yes) -> 3
    `armut`: **a**-r-m-u-t (Yes) -> 1
    `kiraz`: k-i-r-**a**-z (Yes) -> 3
    `muz`: m-u-z (No)

    Sum: 3 + 1 + 3 = 7. Correct.

    Let me double-check the sorting logic again.
    `data = {"elma": 3, "armut": 1, "kiraz": 3, "muz": 2}`
    Keys: `elma`, `armut`, `kiraz`, `muz`.
    Values: `3`, `1`, `3`, `2`.

    Sort criteria: `-value` (descending), then `key` (ascending).
    - elma: (-3, "elma")
    - armut: (-1, "armut")
    - kiraz: (-3, "kiraz")
    - muz: (-2, "muz")

    Sorted tuples:
    (-3, "elma")
    (-3, "kiraz")
    (-2, "muz")
    (-1, "armut")

    Resulting list of keys: `['elma', 'kiraz', 'muz', 'armut']`. Correct.

    Final output format check:
    `print(order)` -> `['elma', 'kiraz', 'muz', 'armut']`
    `print(sum(...))` -> `7`

    Wait, let me re-read the dictionary keys carefully to ensure no typos.
    "elma", "armut", "kiraz", "muz".
    e-l-m-a (contains a)
    a-r-m-u-t (contains a)
    k-i-r-a-z (contains a)
    m-u-z (no a)

    Values: 3, 1, 3, 2.
    Sum of values for keys containing 'a': 3 + 1 + 3 = 7. Correct.

    One more check on the sorting order:
    `sorted(data, key=lambda k: (-data[k], k))`
    Values are:
    elma: 3 -> -3
    armut: 1 -> -1
    kiraz: 3 -> -3
    muz: 2 -> -2

    Sorted by first element of tuple (descending order of values):
    -3, -3, -2, -1.
    For the two -3s, compare keys alphabetically: "elma" vs "kiraz". "e" comes before "k".
    So: elma, kiraz, muz, armut.

    Final check on output format:
    `print(order)` prints a list. Python's `print` for a list uses single quotes and square brackets.
    `['elma', 'kiraz', 'muz', 'armut']`
    `7`

    Wait, let me look at the dictionary again.
    `data = {"elma": 3, "armut": 1, "kiraz": 3, "muz": 2}`
    Is there any other key? No.
    "elma" -> contains 'a' (yes)
    "armut" -> contains 'a' (yes)
    "kiraz" -> contains 'a' (yes)
    "muz" -> contains 'a' (no)

    Sum: 3 + 1 + 3 = 7. Correct.

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
