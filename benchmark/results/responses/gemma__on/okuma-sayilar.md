# okuma-sayilar · puan 1.00

**Not:** doğru

## Prompt

Aşağıdaki Python kodu çalıştırılınca ekrana tam olarak ne yazdırılır? Kodu kafanda çalıştır. Sadece çıktıyı tek bir ```text bloğu içinde ver.

```python
print(7 // -2, -7 % 3, round(2.5), round(3.5), int(-2.7))
print("a,b,,c".split(","), "  x  y ".split())
```

## Düşünme

*   `7 // -2`: Integer division in Python.
        *   `7 / -2 = -3.5`.
        *   Floor division (`//`) rounds towards negative infinity (floor).
        *   The floor of `-3.5` is `-4`.
    *   `-7 % 3`: Modulo operation in Python.
        *   Formula: `r = a - (a // b) * b`
        *   `a = -7`, `b = 3`.
        *   `-7 // 3 = -3` (since `-2.33...` floored is `-3`).
        *   `-7 - (-3 * 3) = -7 - (-9) = -7 + 9 = 2`.
        *   So, `-7 % 3 = 2`.
    *   `round(2.5)`: Python's `round()` function uses "round half to even" (banker's rounding).
        *   `2.5` is exactly halfway between 2 and 3.
        *   The nearest even number is `2`.
        *   So, `round(2.5) = 2`.
    *   `round(3.5)`:
        *   `3.5` is exactly halfway between 3 and 4.
        *   The nearest even number is `4`.
        *   So, `round(3.5) = 4`.
    *   `int(-2.7)`: Integer conversion truncates towards zero.
        *   `-2.7` becomes `-2`.

    *Result of first print:* `-4 2 2 4 -2` (separated by spaces).

    *   `"a,b,,c".split(",")`: Splits the string at every comma.
        *   Parts: `"a"`, `"b"`, `""` (empty string between commas), `"c"`.
        *   Resulting list: `['a', 'b', '', 'c']`.
    *   `"  x  y ".split()`: The `.split()` method without arguments splits by any whitespace and discards empty strings from the result.
        *   String has leading spaces, multiple spaces between x and y, and a trailing space.
        *   Parts: `"x"`, `"y"`.
        *   Resulting list: `['x', 'y']`.

    *Result of second print:* `['a', 'b', '', 'c'] ['x', 'y']` (separated by spaces).

    *   Line 1: `-4 2 2 4 -2`
    *   Line 2: `['a', 'b', '', 'c'] ['x', 'y']`

    Wait, let me re-verify the first line.
    `7 // -2`: `7 / -2 = -3.5`. Floor of `-3.5` is `-4`. Correct.
    `-7 % 3`: `-7 // 3 = -3`. `-7 - (-3 * 3) = 2`. Correct.
    `round(2.5)`: `2`. Correct.
    `round(3.5)`: `4`. Correct.
    `int(-2.7)`: `-2`. Correct.

    Let me re-verify the second line.
    `"a,b,,c".split(",")`: `['a', 'b', '', 'c']`. Correct.
    `"  x  y ".split()`: `['x', 'y']`. Correct.

    *Self-Correction on formatting:* Python's `print(a, b)` puts a space between arguments.
    Line 1 output: `-4 2 2 4 -2`
    Line 2 output: `['a', 'b', '', 'c'] ['x', 'y']`

    Wait, let me check the spacing in Line 1 again.
    `print(7 // -2, -7 % 3, round(2.5), round(3.5), int(-2.7))`
    Arguments: `-4`, `2`, `2`, `4`, `-2`.
    Output: `-4 2 2 4 -2`

    Line 2 output: `['a', 'b', '', 'c'] ['x', 'y']`

    Let's double check the modulo again.
    Python modulo follows the sign of the divisor (3).
    `-7 % 3`:
    -7 / 3 = -2.333...
    Floor is -3.
    -7 - (-3 * 3) = -7 + 9 = 2. Correct.

    Let's double check `round()` again.
    `round(0.5)` -> 0
    `round(1.5)` -> 2
    `round(2.5)` -> 2
    `round(3.5)` -> 4
    Yes, it rounds to the nearest even number when exactly .5.

    Final check on `split()`:
    `"a,b,,c".split(",")` -> `['a', 'b', '', 'c']` (The empty string is preserved because we specified the delimiter).
    `"  x  y ".split()` -> `['x', 'y']` (Default behavior splits by any whitespace and removes empty strings from result).

    Final output structure:
    ```text
    -4 2 2 4 -2
    ['a', 'b', '', 'c'] ['x', 'y']
    ```

## Cevap

```text
-4 2 2 4 -2
['a', 'b', '', 'c'] ['x', 'y']
```

## Notlandırılan kod/komut

```
-4 2 2 4 -2
['a', 'b', '', 'c'] ['x', 'y']
```
