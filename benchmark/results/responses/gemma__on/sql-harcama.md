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

## Düşünme

*   `customers`: `id`, `name`, `city`.
    *   `products`: `id`, `name`, `category`, `price`.
    *   `orders`: `id`, `customer_id`, `product_id`, `quantity`, `order_date`.

    *   Filter: Orders in the year 2026 (`order_date` starts with '2026').
    *   Calculation: Total spending per customer = $\sum (\text{products.price} \times \text{orders.quantity})$.
    *   Goal: Top 3 customers by total spending.
    *   Output Columns: `name` (customer name), total spending.
    *   Ordering: Descending order of total spending.
    *   Constraint: Single SELECT query, only the SQL block in response.

    *   Join `customers`, `orders`, and `products`.
    *   Filter condition: `order_date LIKE '2026%'`.
    *   Group by customer (either `customers.id` or `customers.name`). Since names might not be unique, grouping by `customers.id` is safer, but the output requires name.
    *   Aggregate function: `SUM(products.price * orders.quantity)`.
    *   Limit: 3.

    ```sql
    SELECT c.name, SUM(p.price * o.quantity) AS total_spending
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    JOIN products p ON o.product_id = p.id
    WHERE o.order_date LIKE '2026%'
    GROUP BY c.id, c.name
    ORDER BY total_spending DESC
    LIMIT 3;
    ```

    *   `customers.name`: Yes.
    *   Total spending: Yes.
    *   Order by descending: Yes.
    *   Top 3: Yes.
    *   Year filter (starts with '2026'): `LIKE '2026%'`.
    *   Single SELECT query? Yes.

    ```sql
    SELECT c.name, SUM(p.price * o.quantity) AS total_spending
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    JOIN products p ON o.product_id = p.id
    WHERE o.order_date LIKE '2026%'
    GROUP BY c.id, c.name
    ORDER BY total_spending DESC
    LIMIT 3;
    ```

    *Self-Correction on Grouping:* In SQLite, grouping by `c.id` is sufficient to get the correct name if we select it, but standard SQL often requires all non-aggregated columns in the GROUP BY clause. I'll include both for robustness.

    Wait, let me check the prompt requirements again: "Sütunlar: müşteri adı, toplam harcama."
    The column names aren't strictly specified as aliases, but `name` and `total_spending` (or similar) is standard.

    Final SQL structure:
    ```sql
    SELECT c.name, SUM(p.price * o.quantity) AS total_spent
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    JOIN products p ON o.product_id = p.id
    WHERE o.order_date LIKE '2026%'
    GROUP BY c.id
    ORDER BY total_spent DESC
    LIMIT 3;
    ```

    *Refining the filter:* `order_date` is TEXT in format 'YYYY-MM-DD'. `LIKE '2026%'` works perfectly for SQLite to find anything starting with that year.

    Final check of columns: "müşteri adı, toplam harcama".
    SQL:
    ```sql
    SELECT c.name, SUM(p.price * o.quantity) AS total_spending
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    JOIN products p ON o.product_id = p.id
    WHERE o.order_date LIKE '2026%'
    GROUP BY c.id, c.name
    ORDER BY total_spending DESC
    LIMIT 3;
    ```

    Wait, the prompt says "Sadece sorguyu tek bir ```sql bloğu içinde ver." (Give only the query in a single sql block).

    Let's double check if `GROUP BY c.id` is enough for SQLite when selecting `c.name`. Yes, it is, but `GROUP BY c.id, c.name` is safer and more standard. I will use that.

    One detail: "Harcama, products.price * orders.quantity değerlerinin toplamıdır."
    Calculation: `SUM(products.price * orders.quantity)`. Correct.

    Final Query Construction:
    ```sql
    SELECT c.name, SUM(p.price * o.quantity) AS total_spending
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    JOIN products p ON o.product_id = p.id
    WHERE o.order_date LIKE '2026%'
    GROUP BY c.id, c.name
    ORDER BY total_spending DESC
    LIMIT 3;
    ```

## Cevap

```sql
SELECT c.name, SUM(p.price * o.quantity) AS total_spending
FROM customers c
JOIN orders o ON c.id = o.customer_id
JOIN products p ON o.product_id = p.id
WHERE o.order_date LIKE '2026%'
GROUP BY c.id, c.name
ORDER BY total_spending DESC
LIMIT 3;
```

## Notlandırılan kod/komut

```
SELECT c.name, SUM(p.price * o.quantity) AS total_spending
FROM customers c
JOIN orders o ON c.id = o.customer_id
JOIN products p ON o.product_id = p.id
WHERE o.order_date LIKE '2026%'
GROUP BY c.id, c.name
ORDER BY total_spending DESC
LIMIT 3;
```
