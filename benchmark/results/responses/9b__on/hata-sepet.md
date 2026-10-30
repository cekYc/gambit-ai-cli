# hata-sepet · puan 1.00

**Not:** 5/5 test

## Prompt

Aşağıdaki Python kodunda hata var. Bu sınıfta iki hata var: farklı Cart nesneleri birbirinin ürünlerini görüyor ve indirim yanlış hesaplanıyor (total(10) %10 indirim uygulamalı).
Hatayı düzelt ve kodun düzeltilmiş tam halini ver. Sadece Python kodunu tek bir ```python bloğu içinde ver.

```python
class Cart:
    items = []

    def add(self, name, price, qty=1):
        self.items.append((name, price, qty))

    def total(self, discount_percent=0):
        """İndirimli toplam tutar; indirim yüzde olarak verilir (ör. 10 → %10)."""
        subtotal = sum(price * qty for _, price, qty in self.items)
        return round(subtotal - subtotal * discount_percent, 2)
```

## Düşünme

The user is asking me to fix a Python code that has two bugs:

1. Different Cart objects are seeing each other's items (this is because `items = []` is a class variable instead of an instance variable)
2. The discount calculation is wrong - it should apply 10% discount when total(10) is called, but the current code seems to be calculating correctly... wait, let me re-read this.

Actually looking at the code:
```python
class Cart:
    items = []  # This is a CLASS variable! All instances share the same list
```

This means all Cart objects will share the same `items` list, which is bug #1.

For bug #2 about discount - the current code looks correct mathematically:
```python
return round(subtotal - subtotal * discount_percent, 2)
```

But wait, if discount_percent=10 means 10%, then this should work correctly. Let me think... Actually the issue might be that when items are shared between instances, the total calculation becomes wrong because all Cart objects see each other's items. So both bugs are related to the class variable issue.

Actually, looking more carefully at bug #2 - "indirim yanlış hesaplanıyor (total(10) %10 indirim uygulamalı)" - this means when calling `total(10)` it should apply 10% discount. The current code does:
```python
return round(subtotal - subtotal * discount_percent, 2)
```

This is actually correct mathematically for percentage. If subtotal=100 and discount_percent=10, then result = 100 - 100*0.10 = 90. But wait... the parameter name is `discount_percent` but it's being used as a decimal (0.10) not as a percentage value (10). So if someone passes 10, they get 10% off which means subtracting 10*subtotal instead of 0.10*subtotal.

So the fix should be:
```python
return round(subtotal - subtotal * discount_percent / 100, 2)


```

Or alternatively change the parameter to expect decimal (0-1 range). Based on the docstring saying "ör. 10 → %10" it seems like they want to pass percentage values (like 10 for 10%), so I need to divide by 100.

The main fixes needed are:
1. Change `items = []` from class variable to instance variable using `__init__` method
2. Fix the discount calculation to properly handle percentage values

Let me write the corrected code:

```python
class Cart:
    def __init__(self):
        self.items = []

    def add(self, name, price, qty=1):
        self.items.append((name, price, qty))

    def total(self, discount_percent=0):
        """İndirimli toplam tutar; indirim yüzde olarak verilir (ör. 10 → %10)."""
        subtotal = sum(price * qty for _, price, qty in self.items)
        return round(subtotal - subtotal * discount_percent / 100, 2)
```

This should fix both issues: each Cart instance now has its own items list, and the discount calculation properly divides by 100 to convert percentage values to decimal.


## Cevap

```python
class Cart:
    def __init__(self):
        self.items = []

    def add(self, name, price, qty=1):
        self.items.append((name, price, qty))

    def total(self, discount_percent=0):
        """İndirimli toplam tutar; indirim yüzde olarak verilir (ör. 10 → %10)."""
        subtotal = sum(price * qty for _, price, qty in self.items)
        return round(subtotal - subtotal * discount_percent / 100, 2)
```

## Notlandırılan kod/komut

```
class Cart:
    def __init__(self):
        self.items = []

    def add(self, name, price, qty=1):
        self.items.append((name, price, qty))

    def total(self, discount_percent=0):
        """İndirimli toplam tutar; indirim yüzde olarak verilir (ör. 10 → %10)."""
        subtotal = sum(price * qty for _, price, qty in self.items)
        return round(subtotal - subtotal * discount_percent / 100, 2)
```
