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

*   `gen()` is a generator function.
    *   It has a `try...finally` block.
    *   Inside `try`: it yields `1`, then yields `2`.
    *   The `finally` block contains `print("bitti")`.

    *   `for x in gen():` starts the iteration.
    *   Iteration 1:
        *   `next(gen())` is called.
        *   Execution enters `try`.
        *   `yield 1` is reached. The generator pauses and returns `1` to the loop.
        *   The loop body executes: `print(x)` where `x = 1`. Output: `1`.
        *   `break` is encountered.

    *   When a `break` statement exits a loop that is iterating over a generator, the generator's context must be cleaned up.
    *   The Python interpreter triggers the `finally` block of the generator to ensure proper cleanup (this is standard behavior for generators with `try...finally`).
    *   Execution enters the `finally` block: `print("bitti")`. Output: `bitti`.

    *   After the loop is broken and the generator's context is cleaned up, execution continues after the loop.
    *   The next line is `print("son")`. Output: `son`.

    1.  `1` (from `print(x)`)
    2.  `bitti` (from the `finally` block triggered by the generator being closed/exited via `break`)
    3.  `son` (the final print statement after the loop)

    *   Line 1: `1`
    *   Line 2: `bitti`
    *   Line 3: `son`

    Wait, let me double-check the order of `finally` and the code following the loop.
    When `break` is called:
    1. The generator's `__next__` (or `send`) operation is interrupted.
    2. Because it was inside a `try...finally`, the `finally` block executes *before* control returns to the caller to exit the loop.
    3. Therefore, "bitti" prints before "son".

    Let's trace carefully:
    - Loop starts.
    - Generator yields 1.
    - `print(x)` -> `1`.
    - `break` is hit.
    - The generator object is being closed/exited.
    - The `finally` block in the generator runs -> `print("bitti")`.
    - Control returns to the main scope, exiting the loop.
    - `print("son")` executes.

    Output:
    1
    bitti
    son

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
