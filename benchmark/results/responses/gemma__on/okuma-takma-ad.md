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
    *   `b += [4]` -> This is an in-place addition (equivalent to `b.extend([4])`). Since `b` and `a` point to the same object, the original list is modified.
        *   Current state of `a`: `[1, 2, 3, 4]`
        *   Current state of `b`: `[1, 2, 3, 4]`
    *   `c = a[:]` -> This creates a *shallow copy* (slice) of the current list `a`. `c` is a new list object containing the elements currently in `a`.
        *   Current state of `c`: `[1, 2, 3, 4]`
    *   `c.append(5)` -> This appends `5` to the list `c`. Since `c` is a separate object from `a` and `b`, it does not affect them.
        *   Current state of `c`: `[1, 2, 3, 4, 5]`
    *   `print(a, b, c)` -> Prints the values of `a`, `b`, and `c`.

    *   `a` is `[1, 2, 3, 4]`
    *   `b` is `[1, 2, 3, 4]`
    *   `c` is `[1, 2, 3, 4, 5]`

    The output of `print(a, b, c)` will be:
    `[1, 2, 3, 4] [1, 2, 3, 4] [1, 2, 3, 4, 5]`

    *   `b += [4]` vs `b = b + [4]`:
        *   `b = b + [4]` would create a *new* list and reassign `b`, leaving `a` unchanged.
        *   `b += [4]` is equivalent to `b.__iadd__([4])`, which modifies the object in place for lists. Therefore, `a` is modified. Correct.
    *   `c = a[:]`: This creates a new list. Correct.

    The output should be exactly as printed by Python's `print()` function when passing multiple arguments separated by commas (which adds spaces).

    Result: `[1, 2, 3, 4] [1, 2, 3, 4] [1, 2, 3, 4, 5]`

## Cevap

```text
[1, 2, 3, 4] [1, 2, 3, 4] [1, 2, 3, 4, 5]
```

## Notlandırılan kod/komut

```
[1, 2, 3, 4] [1, 2, 3, 4] [1, 2, 3, 4, 5]
```
