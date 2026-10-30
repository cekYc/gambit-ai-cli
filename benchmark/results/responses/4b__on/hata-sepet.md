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

Kullanıcının verdiği Python kodunda iki hata var:

1. **Sınıf değişkeni problemi**: `items` sınıf sınıf değişkeni (class variable), bu yüzden tüm Cart nesneleri aynı liste kullanıyorlar. Bu yüzden farklı cart'ler birbirinin ürünlerini görüyor.

2. **İndirim hesaplama hatası**: `subtotal * discount_percent` yerine doğru indirim hesaplaması yapılması gerekiyor. Eğer discount_percent=10 ise %10 indirim anlamına geliyor, yani subtotal'tan 10/100'ü kesilmeli. Şu anki kodda 10 * 10 = 100 olan bir miktar düşülüyor.

Düzeltmeler:
1. `items`'i instance değişkenine çevir (her Cart nesnesinin kendi listesi olsun)
2. İndirim hesaplamasında doğru formülü kullan: `subtotal - subtotal * (discount_percent / 100)`

Şimdi düzeltilmiş kodu oluşturayım:

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

Bu kod hem her Cart nesnesinin kendi items listesini tutmasını sağlar (instance variable), hem de indirim doğru şekilde hesaplanır.


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
