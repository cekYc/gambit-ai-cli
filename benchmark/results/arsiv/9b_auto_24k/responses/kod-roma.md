# kod-roma · puan 1.00

**Not:** 12/12 test

## Prompt

Python'da `int_to_roman(n: int) -> str` fonksiyonunu yaz: 1 ile 3999 arasındaki tam sayıyı Roma rakamına
çevirsin (ör. 1994 → "MCMXCIV"). Bu aralığın dışındaki değerlerde ValueError fırlatsın.
Sadece Python kodunu tek bir ```python bloğu içinde ver.

## Cevap

```python
def int_to_roman(n: int) -> str:
    if not (1 <= n <= 3999):
        raise ValueError("Girdi 1 ile 3999 arasında olmalıdır.")
    
    val = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4,
        1
    ]
    
    syms = [
        "M", "CM", "D", "CD",
        "C", "XC", "L", "XL",
        "X", "IX", "V", "IV",
        "I"
    ]
    
    roman_numeral = ""
    i = 0
    
    while n > 0:
        for _ in range(n // val[i]):
            roman_numeral += syms[i]
            n -= val[i]
        i += 1
        
    return roman_numeral
```

## Notlandırılan kod/komut

```
def int_to_roman(n: int) -> str:
    if not (1 <= n <= 3999):
        raise ValueError("Girdi 1 ile 3999 arasında olmalıdır.")
    
    val = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4,
        1
    ]
    
    syms = [
        "M", "CM", "D", "CD",
        "C", "XC", "L", "XL",
        "X", "IX", "V", "IV",
        "I"
    ]
    
    roman_numeral = ""
    i = 0
    
    while n > 0:
        for _ in range(n // val[i]):
            roman_numeral += syms[i]
            n -= val[i]
        i += 1
        
    return roman_numeral
```
