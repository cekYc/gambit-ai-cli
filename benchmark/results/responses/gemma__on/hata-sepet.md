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

*   Class `Cart` has two bugs:
        1.  Different `Cart` objects share the same items (class-level attribute issue).
        2.  Discount calculation is wrong (`total(10)` should apply a 10% discount, but currently it subtracts `subtotal * 10`, which is huge).

    *   Current code: `items = []` defined at the class level. In Python, this makes `items` a class attribute shared by all instances of `Cart`.
    *   Fix: Move `self.items = []` into an `__init__` method to make it an instance attribute.

    *   Current code: `subtotal - subtotal * discount_percent`. If `discount_percent` is 10, it calculates `subtotal - (subtotal * 10)`, which results in a negative number.
    *   Requirement: `total(10)` should mean 10% off.
    *   Formula fix: `subtotal * (1 - discount_percent / 100)`.

    ```python
    class Cart:
        def __init__(self):
            self.items = []

        def add(self, name, price, qty=1):
            self.items.append((name, price, qty))

        def total(self, discount_percent=0):
            subtotal = sum(price * qty for _, price, qty in self.items)
            # Correct formula: subtotal - (subtotal * (discount_percent / 100))
            return round(subtotal * (1 - discount_percent / 100), 2)
    ```

    *   "Sadece Python kodunu tek bir ```python bloğu içinde ver." (Only provide the Python code in a single block).

    *   Bug 1: `items = []` at class level -> Fixed by moving to `__init__`.
    *   Bug 2: `subtotal - subtotal * discount_percent` where input is 10 for 10% -> Fixed by dividing by 100.

    ```python
    class Cart:
        def __init__(self):
            self.items = []

        def add(self, name, price, qty=1):
            self.items.append((name, price, qty))

        def total(self, discount_percent=0):
            """İndirimli toplam tutar; indirim yüzde olarak verilir (ör. 10 → %10)."""
            subtotal = sum(price * qty for _, price, qty in self.items)
            return round(subtotal * (1 - discount_percent / 100), 2)
    ```

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
        return round(subtotal * (1 - discount_percent / 100), 2)
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
        return round(subtotal * (1 - discount_percent / 100), 2)
```
