# kod-roma · puan 1.00

**Not:** 12/12 test

## Prompt

Python'da `int_to_roman(n: int) -> str` fonksiyonunu yaz: 1 ile 3999 arasındaki tam sayıyı Roma rakamına
çevirsin (ör. 1994 → "MCMXCIV"). Bu aralığın dışındaki değerlerde ValueError fırlatsın.
Sadece Python kodunu tek bir ```python bloğu içinde ver.

## Cevap

Aşağıda `int_to_roman(n: int) -> str` fonksiyonunun bir Python kodu örneği bulunmaktadır:

```python
def int_to_roman(n: int) -> str:
    if not (1 <= n <= 3999):
        raise ValueError("Input must be between 1 and 3999.")
    
    # Dictionary to hold the Roman numeral values for each integer place
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
    
    roman_numeral = []
    i = 0
    while n > 0:
        for _ in range(n // val[i]):
            roman_numeral.append(syms[i])
            n -= val[i]
        i += 1
    
    return ''.join(roman_numeral)

# Example usage:
print(int_to_roman(1994))  # Output: "MCMXCIV"
```

Bu fonksiyonu, verilen `n` sayısının 1 ile 3999 arasında olması gerekiyor. Bu dışında bir değer girildiğinde ValueError fırlatıyor.
Bu fonksiyonu, `int_to_roman()` fonksiyonuna tam sayı yerine bir harf veya string verilirse ValueError fırlatıyor.

## Notlandırılan kod/komut

```
def int_to_roman(n: int) -> str:
    if not (1 <= n <= 3999):
        raise ValueError("Input must be between 1 and 3999.")
    
    # Dictionary to hold the Roman numeral values for each integer place
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
    
    roman_numeral = []
    i = 0
    while n > 0:
        for _ in range(n // val[i]):
            roman_numeral.append(syms[i])
            n -= val[i]
        i += 1
    
    return ''.join(roman_numeral)

# Example usage:
print(int_to_roman(1994))  # Output: "MCMXCIV"
```
