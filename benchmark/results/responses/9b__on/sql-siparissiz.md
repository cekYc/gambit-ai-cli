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

## Düşünme

The user wants a SQL query that lists the names of customers who have never placed any orders, in alphabetical order.

Let me analyze the schema:
- `customers` table has id, name, city
- `products` table has id, name, category, price
- `orders` table links customers to products with customer_id and product_id

To find customers who have never ordered anything, I need to:
1. Get all customers from the customers table
2. Exclude those who appear in the orders table (LEFT JOIN or NOT IN/NOT EXISTS)
3. Order alphabetically by name

The cleanest approach would be using a LEFT JOIN with IS NULL check on the order_id, or using NOT EXISTS, or NOT IN.

Let me write the query:

```sql
SELECT c.name
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
WHERE o.id IS NULL
ORDER BY c.name;
```

Or alternatively with NOT EXISTS:
```sql
SELECT name
FROM customers
WHERE id NOT IN (SELECT DISTINCT customer_id FROM orders)
ORDER BY name;
```

Both should work. The LEFT JOIN approach is often preferred for performance and clarity. Let me use the LEFT JOIN version as it's more explicit about what we're doing.

The user wants only the SELECT query in a single ```sql block, no explanations outside of that.


## Cevap

```sql
SELECT c.name
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
WHERE o.id IS NULL
ORDER BY c.name;
```

## Notlandırılan kod/komut

```
SELECT c.name
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
WHERE o.id IS NULL
ORDER BY c.name;
```
