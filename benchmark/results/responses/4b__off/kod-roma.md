# kod-roma · puan 1.00

**Not:** 12/12 test

## Prompt

Python'da `int_to_roman(n: int) -> str` fonksiyonunu yaz: 1 ile 3999 arasındaki tam sayıyı Roma rakamına
çevirsin (ör. 1994 → "MCMXCIV"). Bu aralığın dışındaki değerlerde ValueError fırlatsın.
Sadece Python kodunu tek bir ```python bloğu içinde ver.

## Cevap

```python
def int_to_roman(n: int) -> str:
    if not 1 <= n <= 3999:
        raise ValueError("Bir Roma rakamı sadece 1 ile 3999 arasında olabilir.")
    
    values = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    symbols = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    
    roman = []
    
    for i in range(len(values)):
        while n >= values[i]:
            n -= values[i]
            roman.append(symbols[i])
            
    return "".join(roman)
```

## Notlandırılan kod/komut

```
def int_to_roman(n: int) -> str:
    if not 1 <= n <= 3999:
        raise ValueError("Bir Roma rakamı sadece 1 ile 3999 arasında olabilir.")
    
    values = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    symbols = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    
    roman = []
    
    for i in range(len(values)):
        while n >= values[i]:
            n -= values[i]
            roman.append(symbols[i])
            
    return "".join(roman)
```
