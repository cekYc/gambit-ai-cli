# sql-en-pahali · puan 0.00

**Not:** beklenen [('Elektronik', 'Laptop', 25000.0), ('Kırtasiye', 'Ajanda', 180.0), ('Kırtasiye', 'Kitap', 180.0), ('Mutfak', 'Termos', 600.0)], sonuç [('Elektronik', 'Laptop', 25000.0), ('Elektronik', 'Kulaklık', 1800.0), ('Elektronik', 'Mouse', 450.0), ('Kırtasiye', 'Kitap', 180.0)]

## Prompt

SQLite veritabanında şu tablolar var:
```sql
CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, city TEXT);
CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL);
CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER REFERENCES customers(id),
                     product_id INTEGER REFERENCES products(id), quantity INTEGER,
                     order_date TEXT);  -- 'YYYY-MM-DD'
```
Her kategorideki en pahalı ürünü listele; aynı en yüksek fiyata sahip birden fazla ürün varsa hepsini göster. Sütunlar: kategori, ürün adı, fiyat. Kategoriye, sonra ürün adına göre artan sırala.
Tek bir SELECT sorgusu yaz. Sadece sorguyu tek bir ```sql bloğu içinde ver.

## Cevap

Aşağıdaki SQL sorgusu her kategorideki en pahalı ürünü listeleri:

```sql
SELECT category, name, price
FROM products
ORDER BY category ASC, price DESC;
```

Buunuzda:
- Her kategoriye göre `category` sütunu artan sıralama (`ASC`) yaparız.
- `price` sütunu azalan sıralama (`DESC`) yaparız, böylece en pahalı ürünlerin listesi elde edersiniz.

## Notlandırılan kod/komut

```
SELECT category, name, price
FROM products
ORDER BY category ASC, price DESC;
```
