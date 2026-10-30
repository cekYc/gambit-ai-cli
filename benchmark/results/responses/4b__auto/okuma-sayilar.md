# okuma-sayilar · puan 1.00

**Not:** doğru

## Prompt

Aşağıdaki Python kodu çalıştırılınca ekrana tam olarak ne yazdırılır? Kodu kafanda çalıştır. Sadece çıktıyı tek bir ```text bloğu içinde ver.

```python
print(7 // -2, -7 % 3, round(2.5), round(3.5), int(-2.7))
print("a,b,,c".split(","), "  x  y ".split())
```

## Düşünme

The user is asking me to run this Python code mentally and output what will be printed to the screen. Let me analyze each expression:

1. `7 // -2` - This is floor division (//). 7 divided by -2 = -3.5, but floor division rounds down to the next integer toward negative infinity. So 7 // -2 = -4
2. `-7 % 3` - This is modulo. -7 mod 3: In Python, the result has the same sign as the divisor (3), so it's positive. -7 = (-3)*3 + 2, but actually let me think again. -7 / 3 = -2 with remainder -1... wait, in Python:
   -7 % 3 gives 2 because -7 = 3*(-3) + 2
   
3. `round(2.5)` and `round(3.5)` - In Python 3, round uses banker's rounding (round to nearest even). So round(2.5) = 2 (even), round(3.5) = 4 (even)

4. `int(-2.7)` - This is integer conversion, truncates toward zero: int(-2.7) = -2

For the second line:
1. `"a,b,,c".split(",")` - Splitting by comma gives: ['a', 'b', '', 'c'] (note there are two commas creating an empty string in between)
2. `"  x  y ".split()` - Default split on whitespace, so it removes leading/trailing spaces and multiple spaces become single separators. Result: ['x', 'y']

Wait, let me verify the floor division again:
7 // -2 = ?


In Python, // is floor division which always rounds toward negative infinity. 7 / -2 = -3.5, and floor(-3.5) = -4 ✓

Now for modulo with negative numbers in Python: The result has the same sign as the divisor (which is positive 3). So -7 % 3 = ? We need -7 = 3 * q + r where 0 <= r < 3. If q = -3, then r = -7 - 3*(-3) = -7 + 9 = 2 ✓

So the first line outputs: -4 2 2 4 -2 (with spaces between values as default print separator is space by default when using multiple arguments)

Actually wait, looking at `print(7 // -2, -7 % 3, round(2.5), round(3.5), int(-2.7))` - this uses comma separation which means space-separated output. The values are:
- 7 // -2 = -4
- -7 % 3 = 2
- round(2.5) = 2 (banker's rounding to even)
- round(3.5) = 4 (banker's rounding to even)
- int(-2.7) = -2

So first line: `-4 2 2 4 -2`

Second line with split():
```python
"a,b,,c".split(",")  # ['a', 'b', '', 'c']
"  x  y ".split()    # ['x', 'y']
```

So output: `['a', 'b', '', 'c'] ['x', 'y']` (space separated between lists)

I need to be careful about the exact format. In Python, print with multiple arguments puts a space separator by default between them. So each list will appear on separate lines if we're looking at this correctly. No wait, there are two separate print statements, so they'll print on different lines.

Let me verify:
- First print statement has 5 comma-separated values that get printed with spaces between
- Second print statement has 2 comma-separated values (two list results) that get printed with spaces between

So the output should be:
```
-4 2 2 4 -2
['a', 'b', '', 'c'] ['x', 'y']
```

I need to be careful about what split() does. `"  x  y ".split()` with no arguments splits on any whitespace and removes empty strings from results, so it would give `['x', 'y']`. And `"a,b,,c".split(",")` gives `['a', 'b', '', 'c']` because there are three commas creating two empty slots.

I'm ready to finalize the output format.


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
