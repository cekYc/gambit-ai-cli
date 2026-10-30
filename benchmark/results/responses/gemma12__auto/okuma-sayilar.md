# okuma-sayilar · puan 0.00

**Not:** beklenen "-4 2 2 4 -2\n['a', 'b', '', 'c'] ['x', 'y']", cevap "(-4, 2, 2, 4, -2)\n(['a', 'b', '', 'c'], ['x', 'y'])"

## Prompt

Aşağıdaki Python kodu çalıştırılınca ekrana tam olarak ne yazdırılır? Kodu kafanda çalıştır. Sadece çıktıyı tek bir ```text bloğu içinde ver.

```python
print(7 // -2, -7 % 3, round(2.5), round(3.5), int(-2.7))
print("a,b,,c".split(","), "  x  y ".split())
```

## Düşünme

Goal: determine the exact output of two `print` calls in Python and return it as a plain string in one ```text block.

Edge cases / subtleties:
- Integer division with negative numbers (`7 // -2`): Python uses floor division, so `-3.5 → -4`.
- Modulo with negative divisor (`-7 % 3`): `-7 = (-3)*3 + 2`, result is `2`.
- Rounding half cases: Python rounds to the nearest even number for `.5` (round(2.5)→2, round(3.5)→4).
- int() truncation toward zero (`int(-2.7)` → -2).
- split(",") on "a,b,,c" with consecutive commas produces an empty string in the middle.
- .split() with no argument splits on whitespace and discards leading/trailing/multiple spaces ("  x  y " → ["x", "y"]).

Calculation:
Line 1: (-4, 2, 2, 4, -2)
Line 2: (['a', 'b', '', 'c'], ['x', 'y'])

Output format is two print lines.


## Cevap

```text
(-4, 2, 2, 4, -2)
(['a', 'b', '', 'c'], ['x', 'y'])
```

## Notlandırılan kod/komut

```
(-4, 2, 2, 4, -2)
(['a', 'b', '', 'c'], ['x', 'y'])
```
