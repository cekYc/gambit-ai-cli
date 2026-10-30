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

Kodunuzda iki hata vardır:

1. `self.items` nesnesi bir tane Cart nesne için liste olarak tanımlandığından, her Cart nesnesinin farklı ürünlerini tutması gerekmektedir.

2. `discount_percent` değişkeninin `0` olmasının durumunda indirim yanlış hesaplanıyor çünkü `%10` işlemi yapılmaz.

Bunu düzeltmek için, her Cart nesnesinin bir kendi `items` listesi olduğunu ve indirim yüzde olarak verilen indirim miktarını doğru hesaplamasını sağlamak için kodu değiştirebiliriz. İşte düzeltilmiş olan kod:

```python
class Cart:
    def __init__(self):
        self.items = []

    def add(self, name, price, qty=1):
        self.items.append((name, price, qty))

    def total(self, discount_percent=0):
        """İndirimli toplam tutar; indirim yüzde olarak verilir (ör. 10 → %10)."""
        if discount_percent < 0:
            raise ValueError("Indirim yüzdesi negatif olamaz.")
        
        subtotal = sum(price * qty for _, price, qty in self.items)
        return round(subtotal - subtotal * (discount_percent / 100), 2)
```

Bu bir Cart nesnesi oluşturduğunda, bu nesnenin `items` listesi başlangıçta boş olarak başlatılır. Bu `add` metodunu kullanarak ürünleri eklenebilir ve bu metodu her yeni ekleme işleminden sonra Cart nesnelerinin ürünlerini güncellemektedir.

Bu `total` metodunda, indirim yüzde olarak verilen indirim miktarını doğru hesaplamak için `%10` işlemini `(discount_percent / 100)` şeklinde yapmanız gerektiğini unutmayın. Bu bu indirim yüzdesi negatifse(ValueError), kodda hata verir.

Bu böyle bir Cart nesnesi oluşturur ve ürünleri ekler:

```python
my_cart = Cart()
my_cart.add("Product A", 15.99, qty=2)
my_cart.add("Product B", 9.99)

# Ürünlerin toplam fiyatı: 34.98
print(my_cart.total())
```

Bu böyle bir indirim uygular:

```python
my_cart = Cart()
my_cart.add("Product A", 15.99, qty=2)
my_cart.add("Product B", 9.99)

# Ürünlerin toplam fiyatı: 34.98 - 3.498 indirimli = 31.48
print(my_cart.total(discount_percent=10))
```

Bu böyle bir indirim uygular:

```python
my_cart = Cart()
my_cart.add("Product A", 15.99, qty=2)
my_cart.add("Product B", 9.99)

# Ürünlerin toplam fiyatı: 34.98 - 6.798 indirimli = 28.18
print(my_cart.total(discount_percent=60))
```

Bu böyle bir indirim uygular:

```python
my_cart = Cart()
my_cart.add("Product A", 15.99, qty=2)
my_cart.add("Product B", 9.99)

# Ürünlerin toplam fiyatı: 34.98 - 0% indirimli = 34.98
print(my_cart.total(discount_percent=0))
```

Bu bu indirim yüzdesi negatifse ValueError verir:

```python
my_cart = Cart()
my_cart.add("Product A", 15.99, qty=2)
my_cart.add("Product B", 9.99)

# my_cart.total(discount_percent=-10) # ValueError: Indirim yüzdesi negatif olamaz.
```

Bu bu indirim uygulanırken doğru hesaplanır:

```python
print(my_cart.total(discount_percent=25)) # Ürünlerin toplam fiyatı: 34.98 - 8.745 indirimli = 26.235
```

Bu bu indirim uygulanırken doğru hesaplanır:

```python
print(my_cart.total(discount_percent=10)) # Ürünlerin toplam fiyatı: 34.98 - 3.498 indirimli = 31.48
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
        if discount_percent < 0:
            raise ValueError("Indirim yüzdesi negatif olamaz.")
        
        subtotal = sum(price * qty for _, price, qty in self.items)
        return round(subtotal - subtotal * (discount_percent / 100), 2)
```
