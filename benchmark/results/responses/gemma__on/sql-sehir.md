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

## Düşünme

*   `customers`: `id`, `name`, `city`.
    *   `products`: `id`, `name`, `category`, `price`.
    *   `orders`: `id`, `customer_id`, `product_id`, `quantity`, `order_date`.

    *   List the number of customers in each city.
    *   Columns: `city`, customer count (let's call it `customer_count`).
    *   Ordering:
        1.  By customer count descending (`DESC`).
        2.  By city name ascending (`ASC`) if counts are equal.

    *   `SELECT city, COUNT(*) as customer_count` (or just `COUNT(id)`)
    *   `FROM customers`
    *   `GROUP BY city`
    *   `ORDER BY customer_count DESC, city ASC`

    *   "Her şehirdeki müşteri sayısını listele." -> Done.
    *   "Sütunlar: şehir, müşteri sayısı." -> `city`, `COUNT(*)` (or similar).
    *   "Müşteri sayısına göre azalan, eşitlikte şehir adına göre artan sırala." -> `ORDER BY COUNT(*) DESC, city ASC`.
    *   "Tek bir SELECT sorgusu yaz. Sadece sorguyu tek bir ```sql bloğu içinde ver."

    ```sql
    SELECT city, COUNT(*) AS customer_count
    FROM customers
    GROUP BY city
    ORDER BY customer_count DESC, city ASC;
    ```

    Wait, the prompt asks for columns "şehir, müşteri sayısı". I should probably name them clearly or just ensure they are present. Usually, in these types of SQL challenges, standard naming is fine. Let's use `city` and `customer_count`.

    Let's double-check the sorting:
    "Müşteri sayısına göre azalan (DESC), eşitlikte şehir adına göre artan (ASC)". Correct.

    ```sql
    SELECT city, COUNT(*) AS customer_count
    FROM customers
    GROUP BY city
    ORDER BY customer_count DESC, city ASC;
    ```

## Cevap

```sql
SELECT city, COUNT(*) AS customer_count
FROM customers
GROUP BY city
ORDER BY customer_count DESC, city ASC;
```

## Notlandırılan kod/komut

```
SELECT city, COUNT(*) AS customer_count
FROM customers
GROUP BY city
ORDER BY customer_count DESC, city ASC;
```
