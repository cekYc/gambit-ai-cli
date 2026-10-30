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

Aşağıdaki SQL sorgusu, 2026 yılında siparişlerin toplam harcama miktarına göre en çok harcama yapan 3 müşteri adı ve toplam harcamayı listeler:

```sql
SELECT c.name AS customer_name, SUM(p.price * o.quantity) AS total_spent
FROM orders o
JOIN products p ON o.product_id = p.id
JOIN customers c ON o.customer_id = c.id
WHERE SUBSTR(o.order_date, 1, 4) = '2026'
GROUP BY c.name
ORDER BY total_spent DESC
LIMIT 3;
```

Buunuzda:
1. Sipariş tablosundan sipariş tarihini filtrelemek için `SUBSTR` fonksiyonu kullanılarak 2026 yılındaki siparişleri alırız.
2. Müşterileri siparişlerle ilişkilendiririz ve products.tablosunda ürün fiyatını alırız.
3. Toplam harcamayı hesaplarız ve `SUM` fonksiyonu ile toplarız.
4. Müşterilerin isimleri ve toplam harcamları gruplandırarak `GROUP BY` kullanılarak yapılır.
5. Toplam harcamaya göre sıralarız ve `ORDER BY` kullanılarak yapılır.
6. Sonuçları en çok harcama yapan 3 müşteriye sınırlarız ve `LIMIT 3` kullanılarak yapılır.

## Notlandırılan kod/komut

```
SELECT c.name AS customer_name, SUM(p.price * o.quantity) AS total_spent
FROM orders o
JOIN products p ON o.product_id = p.id
JOIN customers c ON o.customer_id = c.id
WHERE SUBSTR(o.order_date, 1, 4) = '2026'
GROUP BY c.name
ORDER BY total_spent DESC
LIMIT 3;
```
