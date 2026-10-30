# sql-en-pahali · puan 1.00

**Not:** doğru

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

```sql
WITH MaxPrices AS (
    SELECT category, MAX(price) as max_price
    FROM products
    GROUP BY category
)
SELECT p.category, p.name, p.price
FROM products p
JOIN MaxPrices mp ON p.category = mp.category AND p.price = mp.max_price
ORDER BY p.category ASC, p.name ASC;
```

## Notlandırılan kod/komut

```
WITH MaxPrices AS (
    SELECT category, MAX(price) as max_price
    FROM products
    GROUP BY category
)
SELECT p.category, p.name, p.price
FROM products p
JOIN MaxPrices mp ON p.category = mp.category AND p.price = mp.max_price
ORDER BY p.category ASC, p.name ASC;
```
