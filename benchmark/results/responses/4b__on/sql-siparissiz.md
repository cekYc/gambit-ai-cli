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

Thinking Process:

1.  **Analyze the Request:**
    *   Role: Experienced Software Developer.
    *   Task: Write a SQL query for SQLite.
    *   Schema: Three tables (`customers`, `products`, `orders`).
        *   `customers`: id, name, city.
        *   `products`: id, name, category, price.
        *   `orders`: id, customer_id (FK to customers), product_id (FK to products), quantity, order_date.
    *   Goal: List names of customers who have never placed an order.
    *   Ordering: Alphabetical order by name.
    *   Output Format: Single SELECT query only, inside a single ```sql block.

2.  **Determine the Logic:**
    *   I need to find rows in `customers` where there is no corresponding row in `orders`.
    *   This suggests a "NOT EXISTS" subquery or a "LEFT JOIN ... WHERE IS NULL".
    *   Since the requirement is "Never placed an order", I don't care about products. Just matching `customer_id`.

3.  **Drafting the Query:**
    *   Option 1 (NOT EXISTS):
        ```sql
        SELECT c.name
        FROM customers c
        WHERE NOT EXISTS (
            SELECT 1 FROM orders o WHERE o.customer_id = c.id
        )
        ORDER BY c.name ASC;
        ```
    *   Option 2 (LEFT JOIN):
        ```sql
        SELECT DISTINCT c.name
        FROM customers c
        LEFT JOIN orders o ON c.id = o.customer_id
        WHERE o.id IS NULL
        ORDER BY c.name ASC;
        ```

4.  **Refining the Query:**
    *   Both options work in SQLite.
    *   Option 1 is generally more readable for "no matches" logic, but Option 2 is often faster if indexes exist on `orders.customer_id`. However, given standard SQL best practices and clarity, either works. Let's stick to a clear, standard approach. NOT EXISTS is very explicit about the "no order exists" condition.
    *   Wait, I need to ensure only customer names are returned (Single column). Both do this.
    *   Sorting: Alphabetical (`ORDER BY c.name ASC`).

5.  **Final Check:**
    *   SQLite dialect? Yes, standard SQL works here.
    *   Tables used correctly? `customers` table for name and id, `orders` table for customer_id filter.
    *   Condition met? Customers who have no orders.
    *   Order met? Alphabetical.
    *   Output format? Single ```sql block containing only the query.

6.  **Constructing the Final Response:**
    *   Just the SQL code inside the markdown block as requested ("Sadece sorguyu tek bir ```sql bloğu içinde ver" - "Give only the query in a single ```sql block"). I should not add explanations outside the block if strictly interpreted, but usually, a polite intro is okay. However, the prompt says "Sadece sorguyu... ver" (Only give the query...). To be safe and precise as per "Görevi dikkatle çöz ve cevabını tam olarak istenen biçimde ver", I will provide just the code block to ensure compliance with "tek bir ... bloğu içinde". Actually, looking at previous instructions for similar tasks, usually a brief polite intro is acceptable, but strict adherence suggests minimizing text. Let's look closely: "Sadece sorguyu tek bir ```sql bloğu içinde ver." -> "Give only the query inside a single ```sql block."
    *   I will output the code block directly or with minimal surrounding text if necessary for context, but best to keep it clean. The prompt asks me to be an experienced developer and solve carefully. Usually, providing just the solution is better when explicitly asked for "only".

    Let's refine the query slightly for robustness (though `id` is INTEGER PRIMARY KEY).
    ```sql
    SELECT c.name
    FROM customers AS c
    WHERE NOT EXISTS (SELECT 1 FROM orders AS o WHERE o.customer_id = c.id)
    ORDER BY c.name ASC;
    ```

7.  **Final Polish:**
    Make sure no extra characters outside the block violate the "only" instruction too much. I will write a brief sentence introducing it if needed, but the core constraint is the block. Wait, re-reading: "Sadece sorguyu tek bir ```sql bloğu içinde ver." implies *only* that content should be visible or at least the query itself must be contained there exclusively. To be safest, I will provide just the markdown code block containing the SQL.

    Actually, standard behavior for these prompts is to allow a short sentence before/after unless specified "Do not write anything else". But "Sadece sorguyu ... ver" leans towards minimalism. I'll provide the query in the block.

    Wait, checking the instruction again: "Görevi dikkatle çöz ve cevabını tam olarak istenen biçimde ver." (Solve carefully and give your answer exactly as requested).
    Request: "Tek bir SELECT sorgusu yaz. Sadece sorguyu tek bir ```sql bloğu içinde ver." (Write a single SELECT query. Give only the query inside a single ```sql block.)

    Okay, I will output just the code block to be strictly compliant.

    Query:
    ```sql
    SELECT c.name
    FROM customers AS c
    WHERE NOT EXISTS (SELECT 1 FROM orders O WHERE o.customer_id = c.id)
    ORDER BY c.name ASC;
    ```

    Wait, case sensitivity for identifiers is irrelevant here but good to be consistent. `ORDER BY` should probably be uppercase or lowercase depending on SQLite config, standard is usually lowercase in output but keywords are case-insensitive. I'll stick to standard casing.

    One more check: "Hiç sipariş vermemiş müşterilerin adlarını alfabetik sırayla listele." -> List names of customers who have never ordered alphabetically sorted.
    My query does exactly that.

    Let's write it down.

```sql
SELECT c.name
FROM customers AS c
WHERE NOT EXISTS (SELECT 1 FROM orders AS o WHERE o.customer_id = c.id)
ORDER BY c.name ASC;
```

    Wait, is there any edge case? `orders` table might be empty. Query works. `customers` might have null names? Primary key implies integer, but name is TEXT. If NULL, ORDER BY usually puts them at bottom or top depending on collation. Standard SQL sorts NULLs to the end with ASC unless specified otherwise in SQLite (usually it's distinct). But since we list names of *existing* customers (id INTEGER PRIMARY KEY), and they exist in `customers` table, we don't filter out nulls explicitly. The requirement asks for names. If a name is NULL, it will be returned as NULL or empty string depending on context? In SQLite, `SELECT name FROM ... WHERE NOT EXISTS`. If `name` is NULL, it returns NULL. This is standard behavior and likely acceptable unless "non-empty names" was specified. I'll stick to the logic derived from requirements.

    Final check on constraints:
    - Single SELECT query.
    - Single ```sql block.
    - No extra text outside? The prompt says "Sadece sorguyu ... bloğu içinde ver". I will minimize surrounding text to ensure compliance.

    Let's prepare the response.

```sql
SELECT c.name FROM customers AS c WHERE NOT EXISTS (SELECT 1 FROM orders AS o WHERE o.customer_id = c.id) ORDER BY c.name ASC;
```
    Or formatted for readability? Usually formatted is better. I'll format it nicely within the block.

```sql
SELECT name
FROM customers
WHERE NOT EXISTS (
    SELECT 1
    FROM orders
    WHERE customer_id = customers.id
);
ORDER BY name ASC;
```
Wait, aliasing makes it cleaner.
Let's use `c` and `o`.

```sql
SELECT c.name
FROM customers AS c
WHERE NOT EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.customer_id = c.id
)
ORDER BY c.name ASC;
```

This looks good. I will output this. I'll check if I should include comments. No, keep it clean as "only query".

Wait, one detail: "Tek bir SELECT sorgusu yaz." (Write a single SELECT query). The block should contain the SQL code.

Okay, ready to generate.cs


## Cevap

```sql
SELECT c.name
FROM customers AS c
WHERE NOT EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.customer_id = c.id
)
ORDER BY c.name ASC;
```

## Notlandırılan kod/komut

```
SELECT c.name
FROM customers AS c
WHERE NOT EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.customer_id = c.id
)
ORDER BY c.name ASC;
```
