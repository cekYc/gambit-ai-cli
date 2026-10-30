# sql-harcama · puan 1.00

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
2026 yılında (order_date '2026' ile başlayan siparişler) en çok harcama yapan 3 müşteriyi listele. Harcama, products.price * orders.quantity değerlerinin toplamıdır. Sütunlar: müşteri adı, toplam harcama. Toplam harcamaya göre azalan sırala.
Tek bir SELECT sorgusu yaz. Sadece sorguyu tek bir ```sql bloğu içinde ver.

## Cevap

```sql
SELECT c.name, SUM(p.price * o.quantity) AS total_spent
FROM customers c
JOIN orders o ON c.id = o.customer_id
JOIN products p ON o.product_id = p.id
WHERE o.order_date LIKE '2026%'
GROUP BY c.id, c.name
ORDER BY total_spent DESC
LIMIT 3;
```

## Notlandırılan kod/komut

```
SELECT c.name, SUM(p.price * o.quantity) AS total_spent
FROM customers c
JOIN orders o ON c.id = o.customer_id
JOIN products p ON o.product_id = p.id
WHERE o.order_date LIKE '2026%'
GROUP BY c.id, c.name
ORDER BY total_spent DESC
LIMIT 3;
```
