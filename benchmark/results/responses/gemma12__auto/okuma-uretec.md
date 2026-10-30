# okuma-uretec · puan 1.00

**Not:** doğru

## Prompt

Aşağıdaki Python kodu çalıştırılınca ekrana tam olarak ne yazdırılır? Kodu kafanda çalıştır. Sadece çıktıyı tek bir ```text bloğu içinde ver.

```python
def gen():
    try:
        yield 1
        yield 2
    finally:
        print("bitti")

for x in gen():
    print(x)
    break
print("son")
```

## Düşünme

Goal: determine the exact output of the provided Python code when executed.

Code walkthrough:
1. `gen()` defines a generator with two `yield` statements and a `finally` block that prints `"bitti"`.
2. The for loop iterates over `gen()`, calls `next(gen())` implicitly on each iteration, and breaks after the first element is printed.
3. First iteration: `yield 1` suspends execution of `gen()` just before printing 1; control returns to the caller; `print(x)` prints `1`.
4. The `break` statement terminates the loop immediately after that print.
5. When a generator's iterator is garbage collected or closed (e.g., at the end of the break), its `finally` block executes — in this case, printing `"bitti"`.
6. After the for block, `print("son")` runs normally.

Execution sequence: 1 → bitti → son

Output lines: one per print call, no extra spaces or formatting.

```text
1
bitti
son
```

## Cevap

```text
1
bitti
son
```

## Notlandırılan kod/komut

```
1
bitti
son
```
