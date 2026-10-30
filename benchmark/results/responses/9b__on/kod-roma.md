# kod-roma · puan 1.00

**Not:** 12/12 test

## Prompt

Python'da `int_to_roman(n: int) -> str` fonksiyonunu yaz: 1 ile 3999 arasındaki tam sayıyı Roma rakamına
çevirsin (ör. 1994 → "MCMXCIV"). Bu aralığın dışındaki değerlerde ValueError fırlatsın.
Sadece Python kodunu tek bir ```python bloğu içinde ver.

## Düşünme

The user wants me to write a Python function that converts integers between 1 and 3999 to Roman numerals. The function should raise a ValueError for values outside this range.

Roman numeral rules:
- I = 1
- V = 5
- X = 10
- L = 50
- C = 100
- D = 500
- M = 1000

Special combinations for subtraction notation:
- IV = 4 (I before V)
- IX = 9 (I before X)
- XL = 40 (X before L)
- XC = 90 (X before C)
- CD = 400 (C before D)
- CM = 900 (C before M)

The standard approach is to use a mapping of values in descending order including the subtraction cases, then iterate through them.

Let me write this function:

```python
def int_to_roman(n: int) -> str:
    if n < 1 or n > 3999:
        raise ValueError("Sadece 1 ile 3999 arasındaki tam sayılar kabul edilir")
    
    roman_map = [
        (1000, 'M'),
        (900, 'CM'),
        (500, 'D'),
        (400, 'CD'),
        (100, 'C'),
        (90, 'XC'),
        (50, 'L'),
        (40, 'XL'),
        (10, 'X'),
        (9, 'IX'),
        (5, 'V'),
        (4, 'IV'),
        (1, 'I')
    ]
    
    result = []
    for value, symbol in roman_map:
        while n >= value:
            result.append(symbol)
            n -= value
    
    return ''.join(result)
```

This should work correctly. Let me verify with the example: 1994 → "MCMXCIV"


- M (1000): 1994 - 1000 = 994, result = ["M"]
- CM (900): 994 - 900 = 94, result = ["M", "CM"]
- XC (90): 94 - 90 = 4, result = ["M", "CM", "XC"]
- IV (4): 4 - 4 = 0, result = ["M", "CM", "XC", "IV"]

Final: "MCMXCIV" ✓

The function handles the conversion correctly by processing values from largest to smallest, including special subtraction cases.


## Cevap

```python
def int_to_roman(n: int) -> str:
    if n < 1 or n > 3999:
        raise ValueError("Sadece 1 ile 3999 arasındaki tam sayılar kabul edilir")
    
    roman_map = [
        (1000, 'M'),
        (900, 'CM'),
        (500, 'D'),
        (400, 'CD'),
        (100, 'C'),
        (90, 'XC'),
        (50, 'L'),
        (40, 'XL'),
        (10, 'X'),
        (9, 'IX'),
        (5, 'V'),
        (4, 'IV'),
        (1, 'I')
    ]
    
    result = []
    for value, symbol in roman_map:
        while n >= value:
            result.append(symbol)
            n -= value
    
    return ''.join(result)
```

## Notlandırılan kod/komut

```
def int_to_roman(n: int) -> str:
    if n < 1 or n > 3999:
        raise ValueError("Sadece 1 ile 3999 arasındaki tam sayılar kabul edilir")
    
    roman_map = [
        (1000, 'M'),
        (900, 'CM'),
        (500, 'D'),
        (400, 'CD'),
        (100, 'C'),
        (90, 'XC'),
        (50, 'L'),
        (40, 'XL'),
        (10, 'X'),
        (9, 'IX'),
        (5, 'V'),
        (4, 'IV'),
        (1, 'I')
    ]
    
    result = []
    for value, symbol in roman_map:
        while n >= value:
            result.append(symbol)
            n -= value
    
    return ''.join(result)
```
