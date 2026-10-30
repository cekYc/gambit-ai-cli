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

Hataların iki sebebi var: `items` listesi sınıf seviyesinde (class attribute) tanımlandığı için tüm Cart nesneleri aynı ortak listeyi paylaşıyor; her sepetin kendi ürünlerini tutması için örnek metodunda (`__init__`) örnek değişkenine (instance attribute) taşındı. İkinci hata ise indirim hesaplamasında: kullanıcı 10 girdiğinde %10 kastettiği için formül `discount_percent / 100` şeklinde düzeltildi; aksi takdirde inputu doğrudan çarpan olarak kullanıyor ve yanlış sonuç veriyordu.

```python
class Cart:
    def __init__(self):
        self.items = []

    def add(self, name, price, qty=1):
        self.items.append((name, price, qty))

    def total(self, discount_percent=0):
        """İndirimli toplam tutar; indirim yüzde olarak verilir (ör. 10 → %10)."""
        subtotal = sum(price * qty for _, price, qty in self.items)
        discount = subtotal * (discount_percent / 100)
        return round(subtotal - discount, 2)
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
        discount = subtotal * (discount_percent / 100)
        return round(subtotal - discount, 2)
```
