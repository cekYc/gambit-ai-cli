# sql-siparissiz · puan 1.00

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
Hiç sipariş vermemiş müşterilerin adlarını alfabetik sırayla listele. Tek sütun: müşteri adı.
Tek bir SELECT sorgusu yaz. Sadece sorguyu tek bir ```sql bloğu içinde ver.

## Cevap

```sql
SELECT name 
FROM customers 
WHERE id NOT IN (SELECT customer_id FROM orders) 
ORDER BY name ASC;
```

## Notlandırılan kod/komut

```
SELECT name 
FROM customers 
WHERE id NOT IN (SELECT customer_id FROM orders) 
ORDER BY name ASC;
```
