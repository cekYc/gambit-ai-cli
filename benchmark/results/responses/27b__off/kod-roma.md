# kod-roma · puan 1.00

**Not:** 12/12 test

## Prompt

Python'da `int_to_roman(n: int) -> str` fonksiyonunu yaz: 1 ile 3999 arasındaki tam sayıyı Roma rakamına
çevirsin (ör. 1994 → "MCMXCIV"). Bu aralığın dışındaki değerlerde ValueError fırlatsın.
Sadece Python kodunu tek bir ```python bloğu içinde ver.

## Cevap

```python
def int_to_roman(n: int) -> str:
    """Convert an integer (1-3999) to a Roman numeral string."""
    if not isinstance(n, int) or isinstance(n, bool):
        raise ValueError(f"Expected an integer, got {type(n).__name__}")
    if n < 1 or n > 3999:
        raise ValueError(f"Number must be between 1 and 3999, got {n}")
    
    # Mapping of values to Roman numeral symbols (including subtractive notation)
    val_sym = [
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
        (1, 'I'),
    ]
    
    result = []
    for value, symbol in val_sym:
        while n >= value:
            result.append(symbol)
            n -= value
    
    return ''.join(result)
```

## Notlandırılan kod/komut

```
def int_to_roman(n: int) -> str:
    """Convert an integer (1-3999) to a Roman numeral string."""
    if not isinstance(n, int) or isinstance(n, bool):
        raise ValueError(f"Expected an integer, got {type(n).__name__}")
    if n < 1 or n > 3999:
        raise ValueError(f"Number must be between 1 and 3999, got {n}")
    
    # Mapping of values to Roman numeral symbols (including subtractive notation)
    val_sym = [
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
        (1, 'I'),
    ]
    
    result = []
    for value, symbol in val_sym:
        while n >= value:
            result.append(symbol)
            n -= value
    
    return ''.join(result)
```
