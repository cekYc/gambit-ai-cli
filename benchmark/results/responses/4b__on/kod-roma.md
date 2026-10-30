# kod-roma · puan 1.00

**Not:** 12/12 test

## Prompt

Python'da `int_to_roman(n: int) -> str` fonksiyonunu yaz: 1 ile 3999 arasındaki tam sayıyı Roma rakamına
çevirsin (ör. 1994 → "MCMXCIV"). Bu aralığın dışındaki değerlerde ValueError fırlatsın.
Sadece Python kodunu tek bir ```python bloğu içinde ver.

## Düşünme

Kullanıcının isteği: Python'da `int_to_roman` fonksiyonu yazmak, 1-3999 aralığındaRoma rakamına çevirmek ve dışındaki değerlerde ValueError fırlatmak.

Çözüm adımları:
1.  Gerekli Roma rakamlarını ve değerlerini bir liste olarak tanımla. Normalde büyükten küçüğe sıralama yapılması gerekir (örneğin M=1000, CM=900, D=500, CD=400, C=100, XC=90, L=50, XL=40, X=10, IX=9, V=5, IV=4, I=1).
2.  Verilen sayıyı kontrol et. Eğer 1-3999 aralığı dışında ise `ValueError` fırlatılmalı.
3.  Sıralama: Büyükten küçüğe sıralanmış liste olmalı.
4.  Eşleştirme: Liste içindeki her eleman için, n sayısı o değerden az veya eşitse döngüde bu değeri kullan ve sayıyı o değere göre düşür.

Kod yapısı:
```python
def int_to_roman(n: int) -> str:
    if not (1 <= n <= 3999):
        raise ValueError("Değer 1 ile 3999 arasında olmalıdır")
    
    values = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    symbols = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    
    roman_numeral = []
    for i in range(len(values)):
        while n >= values[i]:
            roman_numeral.append(symbols[i])
            n -= values[i]
    
    return "".join(roman_numeral)
```

Bu fonksiyon, Roma rakamlarını doğru şekilde oluşturur ve istenen aralık kontrolünü yapar. Tek bir ```python bloğu içinde sunacağım.


## Cevap

```python
def int_to_roman(n: int) -> str:
    if not (1 <= n <= 3999):
        raise ValueError("Değer 1 ile 3999 arasında olmalıdır.")
    
    values = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    symbols = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    
    result = []
    
    for i in range(len(values)):
        while n >= values[i]:
            result.append(symbols[i])
            n -= values[i]
            
    return "".join(result)

# Örnek kullanım:
print(int_to_roman(1994))  # Çıktı: MCMXCIV
```

## Notlandırılan kod/komut

```
def int_to_roman(n: int) -> str:
    if not (1 <= n <= 3999):
        raise ValueError("Değer 1 ile 3999 arasında olmalıdır.")
    
    values = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    symbols = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    
    result = []
    
    for i in range(len(values)):
        while n >= values[i]:
            result.append(symbols[i])
            n -= values[i]
            
    return "".join(result)

# Örnek kullanım:
print(int_to_roman(1994))  # Çıktı: MCMXCIV
```
