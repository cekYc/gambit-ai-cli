# kod-roma · puan 0.42

**Not:** 5/12 test; başarısız: S.int_to_roman(1) == "I" | S.int_to_roman(4) == "IV" | S.int_to_roman(9) == "IX" | S.int_to_roman(14) == "XIV" | S.int_to_roman(1994) == "MCMXCIV"

## Prompt

Python'da `int_to_roman(n: int) -> str` fonksiyonunu yaz: 1 ile 3999 arasındaki tam sayıyı Roma rakamına
çevirsin (ör. 1994 → "MCMXCIV"). Bu aralığın dışındaki değerlerde ValueError fırlatsın.
Sadece Python kodunu tek bir ```python bloğu içinde ver.

## Cevap

```python
def int_to_roman(n):
    if not (1 <= n <= 3999):
        raise ValueError("Input must be between 1 and 3999")

    val = [
        (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
        (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
    ]

    result = ""
    for value, symbol in val:
        while n >= value:
            result += symbol
            n -= value
    return result
```

## Notlandırılan kod/komut

```
def int_to_roman(n):
    if not (1 <= n <= 3999):
        raise ValueError("Input must be between 1 and 3999")

    val = [
        (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
        (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
    ]

    result = ""
    for value, symbol in val:
        while n >= value:
            result += symbol
            n -= value
    return result
```
