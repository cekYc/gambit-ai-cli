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

*   `a = [1, 2, 3]` -> `a` is a list object containing `[1, 2, 3]`.
    *   `b = a` -> `b` points to the *same* list object as `a`. They are aliases.
    *   `b += [4]` -> This is an in-place addition for lists (equivalent to `b.extend([4])`). Since `b` and `a` point to the same object, both `a` and `b` now represent `[1, 2, 3, 4]`.
    *   `c = a[:]` -> This creates a *shallow copy* of list `a`. `c` is a new list object containing the elements currently in `a`. So `c` is `[1, 2, 3, 4]`.
    *   `c.append(5)` -> The `.append()` method modifies the list `c` in-place. It does *not* affect `a` or `b`. Now `c` is `[1, 2, 3, 4, 5]`.
    *   `print(a, b, c)` -> Prints the current state of `a`, `b`, and `c`.

    *   `a`: `[1, 2, 3, 4]`
    *   `b`: `[1, 2, 3, 4]`
    *   `c`: `[1, 2, 3, 4, 5]`

    The output of `print(a, b, c)` will be:
    `[1, 2, 3, 4] [1, 2, 3, 4] [1, 2, 3, 4, 5]`

    *   `b += [4]` vs `b = b + [4]`:
        *   `b = b + [4]` would create a *new* list and assign it to `b`, leaving `a` unchanged.
        *   `b += [4]` is equivalent to `b.__iadd__([4])`, which modifies the existing object in place for lists. Since `a` and `b` are the same object, `a` changes too.
    *   `c = a[:]`: This creates a copy. Changes to `c` do not affect `a`.

    The output should be exactly as printed by Python's `print()` function for these lists.

    ```text
    [1, 2, 3, 4] [1, 2, 3, 4] [1, 2, 3, 4, 5]
    ```

## Cevap

```text
[1, 2, 3, 4] [1, 2, 3, 4] [1, 2, 3, 4, 5]
```

## Notlandırılan kod/komut

```
[1, 2, 3, 4] [1, 2, 3, 4] [1, 2, 3, 4, 5]
```
