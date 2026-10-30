# kod-roma · puan 1.00

**Not:** 12/12 test

## Prompt

Python'da `int_to_roman(n: int) -> str` fonksiyonunu yaz: 1 ile 3999 arasındaki tam sayıyı Roma rakamına
çevirsin (ör. 1994 → "MCMXCIV"). Bu aralığın dışındaki değerlerde ValueError fırlatsın.
Sadece Python kodunu tek bir ```python bloğu içinde ver.

## Düşünme

*   Goal: Write a Python function `int_to_roman(n: int) -> str`.
    *   Input: An integer `n` between 1 and 3999 (inclusive).
    *   Output: The Roman numeral representation of `n`.
    *   Constraint 1: If $n < 1$ or $n > 3999$, raise a `ValueError`.
    *   Constraint 2: Output must be *only* the Python code inside a single ```python block.

    *   Roman numerals mapping (descending order):
        *   M: 1000
        *   CM: 900
        *   D: 500
        *   CD: 400
        *   C: 100
        *   XC: 90
        *   L: 50
        *   XL: 40
        *   X: 10
        *   IX: 9
        *   V: 5
        *   IV: 4
        *   I: 1

    *   Algorithm: Greedy approach. Iterate through the mapping, subtract the value from `n`, and append the symbol to the result string until `n` becomes 0.

    ```python
    def int_to_roman(n: int) -> str:
        if not (1 <= n <= 3999):
            raise ValueError("Input must be between 1 and 3999.")

        val = [
            1000, 900, 500, 400,
            100, 90, 50, 40,
            10, 9, 5, 4,
            1
        ]
        syb = [
            "M", "CM", "D", "CD",
            "C", "XC", "L", "XL",
            "X", "IX", "V", "IV",
            "I"
        ]

        roman_num = ""
        i = 0
        while n > 0:
            for _ in range(n // val[i]):
                roman_num += syb[i]
                n -= val[i]
            i += 1
        return roman_num
    ```

    *   `int_to_roman(1994)` -> "MCMXCIV" (Correct)
    *   `int_to_roman(3999)` -> "MMMCMXCIX" (Correct)
    *   `int_to_roman(0)` -> `ValueError` (Correct)
    *   `int_to_roman(4000)` -> `ValueError` (Correct)

    The user requested *only* the Python code in a single block.

    ```python
    def int_to_roman(n: int) -> str:
        if not (1 <= n <= 3999):
            raise ValueError("Input must be between 1 and 3999.")

        mapping = [
            (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
            (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
            (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')
        ]

        roman_num = ""
        for value, symbol in mapping:
            while n >= value:
                roman_num += symbol
                n -= value

        return roman_num
    ```

    *   Function name: `int_to_roman` (Matches)
    *   Type hint: `(n: int) -> str` (Matches)
    *   Range check: 1-3999 (Matches)
    *   Error type: `ValueError` (Matches)
    *   Format: Single ```python block (Matches)

    Wait, the prompt says "Sadece Python kodunu tek bir ```python bloğu içinde ver." (Give only the Python code in a single ```python block). This means no explanation text outside the block.

## Cevap

```python
def int_to_roman(n: int) -> str:
    if not (1 <= n <= 3999):
        raise ValueError("Input must be between 1 and 3999.")

    mapping = [
        (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
        (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
        (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')
    ]

    roman_num = ""
    for value, symbol in mapping:
        while n >= value:
            roman_num += symbol
            n -= value

    return roman_num
```

## Notlandırılan kod/komut

```
def int_to_roman(n: int) -> str:
    if not (1 <= n <= 3999):
        raise ValueError("Input must be between 1 and 3999.")

    mapping = [
        (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
        (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
        (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')
    ]

    roman_num = ""
    for value, symbol in mapping:
        while n >= value:
            roman_num += symbol
            n -= value

    return roman_num
```
