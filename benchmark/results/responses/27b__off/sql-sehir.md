# sql-sehir · puan 1.00

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
Her şehirdeki müşteri sayısını listele. Sütunlar: şehir, müşteri sayısı. Müşteri sayısına göre azalan, eşitlikte şehir adına göre artan sırala.
Tek bir SELECT sorgusu yaz. Sadece sorguyu tek bir ```sql bloğu içinde ver.

## Cevap

```sql
SELECT city, COUNT(*) AS customer_count FROM customers GROUP BY city ORDER BY customer_count DESC, city ASC;
```

## Notlandırılan kod/komut

```
SELECT city, COUNT(*) AS customer_count FROM customers GROUP BY city ORDER BY customer_count DESC, city ASC;
```
