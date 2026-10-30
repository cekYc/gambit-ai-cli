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
        return round(subtotal - (subtotal * discount_percent / 100), 2)
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
        return round(subtotal - (subtotal * discount_percent / 100), 2)
```
