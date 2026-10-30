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

Thinking Process:

1.  **Analyze the Request:**
    *   Role: Experienced Software Developer.
    *   Task: Write a single SQL query to retrieve data from an SQLite database schema provided.
    *   Schema: `customers` (id, name, city), `products` (id, name, category, price), `orders` (id, customer_id, product_id, quantity, order_date).
    *   Goal: List the top 3 customers with the highest spending in the year 2026.
    *   Spending Calculation: Sum of (`products.price` * `orders.quantity`).
    *   Output Columns: Customer Name, Total Spending (topharca).
    *   Sorting: Descending order by total spending.
    *   Constraint: Only one SELECT query within a single ```sql block.

2.  **Determine the SQL Logic:**
    *   Need to join `orders`, `customers`, and `products`.
        *   `customers` -> `orders` (on `customer_id`)
        *   `orders` -> `products` (on `product_id`)
    *   Filter for year 2026: `order_date` starts with '2026'. Since it's stored as TEXT ('YYYY-MM-DD'), using `LIKE '2026%'` or `SUBSTR(order_date, 1, 4) = '2026'` works. SQLite supports `date()` function too but string matching is straightforward given the schema description.
    *   Calculate spending: `products.price * orders.quantity`.
    *   Group by customer to aggregate spending per customer: GROUP BY `customers.id`, `customers.name`.
    *   Order by total spending descending: ORDER BY SUM(...) DESC.
    *   Limit results to 3: LIMIT 3.

3.  **Drafting the Query:**
    ```sql
    SELECT c.name, SUM(p.price * o.quantity) as total_spending
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    JOIN products p ON o.product_id = p.id
    WHERE SUBSTR(o.order_date, 1, 4) = '2026'
    GROUP BY c.id
    ORDER BY total_spending DESC
    LIMIT 3;
    ```

4.  **Refining the Query:**
    *   SQLite allows `ORDER BY SUM(...)` directly? No, usually you alias it or group by is required. I aliased it as `total_harcama` (Turkish name requested implicitly or explicitly?). The prompt asks for "müsiteri adı, toplam harcama" in the description ("Sütunlar: müşteri adı, toplam harcama"). It doesn't specify column names exactly but implies standard Turkish naming convention if I were writing locally. However, SQL column aliases should be consistent with the request.
    *   The prompt asks for "müsiteri adı" (customer name) and "toplam harcama". Let's use meaningful English or Turkish aliases. Since the schema is in English but the instruction text is Turkish, I will follow standard practice: usually English column names are preferred in code unless specified otherwise, but to match the request context better, I can use descriptive names. However, SQL best practices suggest consistency with the DB design (English). Let's stick to a clear alias for spending.
    *   The prompt explicitly asks for "Sütunlar: müşteri adı, toplam harcama". I will name the columns `name` and `toplam_harcama` (or just let it be aliased clearly). Actually, standard SQL output column names often follow English conventions unless specified. But given the instruction is in Turkish ("müsiteri adı"), providing an alias like `total_spending` or `toplam_harcama` is fine. Let's use `total_harcama` to match the Turkish context slightly better, or just a standard English one. I will use `name` and `total_harcama`.
    *   Wait, strict SQLite syntax check: `GROUP BY c.id` ensures uniqueness per customer (even though name is functionally dependent on id in this schema). Grouping by all selected non-aggregated columns (`c.name`) would also work, but grouping by primary key `id` is safer. The prompt asks for `customers` table structure where `id` is PK.
    *   Date filter: `order_date TEXT`. `LIKE '2026%'` is standard and efficient in SQLite for text columns starting with specific strings. Or `WEEKOFYEAR`? No, date string manipulation. `SUBSTR(order_date, 1, 4) = '2026'` is precise.
    *   Join types: INNER JOIN is correct because we only want customers who have orders in that year (though the prompt implies "customers spending", if they didn't spend anything in 2026 they wouldn't appear in top 3 anyway).

5.  **Final Polish:**
    ```sql
    SELECT c.name, SUM(p.price * o.quantity) AS toplam_harcama
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    JOIN products p ON o.product_id = p.id
    WHERE SUBSTR(o.order_date, 1, 4) = '2026'
    GROUP BY c.id
    ORDER BY toplam_harcama DESC
    LIMIT 3;
    ```
    Wait, `GROUP BY` clause in SQLite. Since `c.name` is selected without aggregation but depends on `c.id`, grouping by `c.id` is sufficient for correctness in newer SQLite versions (which allow functional dependencies), or I can group by both `c.id, c.name`. Given strict compliance, grouping by `c.id` is best practice if name is unique per id.
    Also, column alias: The prompt says "Sütunlar: müşteri adı, toplam harcama". This describes the *content* of columns, not necessarily the literal names in SQL `SELECT`, but aliases make it clear. I'll use `name` and `toplam_harcama`.

6.  **Review Constraints:**
    *   Single SELECT query? Yes.
    *   Single ```sql block? Yes.
    *   Top 3 spending customers? Yes (LIMIT 3).
    *   Year 2026 filter? Yes (`SUBSTR(...,1,4) = '2026'`).
    *   Calculation correct? `price * quantity`.

7.  **Output Generation:** Ensure no markdown outside the code block if strictly requested ("Sadece sorguyu tek bir ```sql bloğu içinde ver" - "Provide only the query in a single ```sql block"). Wait, reading carefully: "Sadece sorguyu tek bir ```sql bloğu içinde ver." This usually means *only* the SQL content inside the block, but sometimes implies no explanatory text outside. However, as an AI assistant, I should follow instructions precisely. If it says "Give only...", I should avoid conversational filler before or after the code block if possible, though standard helpfulness often allows a brief intro. The instruction says "Sadece sorguyu... ver" (Only give the query...). So I will output just the markdown block containing the SQL.

    Wait, looking at previous interactions/style guidelines for this persona ("Sen deneyimli bir yazılım geliştiricisin"). Usually, I provide the solution clearly. But the constraint "Sadece sorguyu tek bir ```sql bloğu içinde ver" (Only give the query in a single ```sql block) is a hard constraint on formatting.

    Let's check the instruction again: "Tek bir SELECT sorgusu yaz. Sadece sorguyu tek bir ```sql bloğu içinde ver."
    This means: Write one SELECT query. Provide ONLY that query inside ONE ```sql block. No explanations outside.

8.  **Final Code Construction:**
    ```sql
    SELECT c.name, SUM(p.price * o.quantity) AS toplam_harcama
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    JOIN products p ON o.product_id = p.id
    WHERE SUBSTR(o.order_date, 1, 4) = '2026'
    GROUP BY c.id
    ORDER BY toplam_harcama DESC
    LIMIT 3;
    ```

    Wait, should I alias the columns as "müşteri adı" and "toplam harcama"? No, that's not valid SQL syntax. I will use `name` and `total_harcama` or similar, ensuring they represent the requested data. The prompt says "Sütunlar: müşteri adı, toplam harcama". This defines what should be in the output columns.
    Let's stick to standard aliases like `name` and `toplam_harcama`.

    One check on SQLite: `GROUP BY c.id` is safer than just names because names are unique via id but technically grouping by non-aggregated column requires them to be functionally dependent or explicitly included in group by. Grouping by primary key is best practice here.

    Final check on date filter: `order_date` is TEXT 'YYYY-MM-DD'. `SUBSTR(order_date, 1, 4) = '2026'` works perfectly for '2026-01-01' etc.

    Ready to write.

    Wait, one more check on the instruction "Sadece sorguyu tek bir ```sql bloğu içinde ver".
    Does it mean *nothing else*? Yes. I will ensure no introductory text like "İşte sorgu:" appears outside the block.

    One detail: "Toplam harcamaya göre azalan sırala." -> `ORDER BY toplam_harcama DESC`.
    "En çok harcama yapan 3 müşteriyi listele." -> `LIMIT 3`.

    Looks good.

    Wait, regarding Turkish vs English column aliases. Since the prompt description uses Turkish ("müşteri adı"), using a Turkish alias for clarity in the SQL block is acceptable and aligns with the user's context. I will use `toplam_harcama` as it matches "toplam harcama" request better than just `total_spending`.

    Final check on syntax:
    ```sql
    SELECT c.name, SUM(p.price * o.quantity) AS toplam_harcama
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    JOIN products p ON o.product_id = p.id
    WHERE SUBSTR(o.order_date, 1, 4) = '2026'
    GROUP BY c.id
    ORDER BY toplam_harcama DESC
    LIMIT 3;
    ```

    Wait, is `name` a valid column name? Yes. Is `c.name` valid aliasing? Yes.
    Okay. I'll produce the output now.
    Actually, to be extremely precise with "Sadece sorguyu tek bir ```sql bloğu içinde ver", I should not add any markdown explanation text before or after the block if possible, just the block itself is safer compliance. But usually, a code fence is part of the message content. The instruction means "Don't write paragraphs of text explaining it". Just the SQL inside the fence.

    Wait, one small optimization/standard: `JOIN ... JOIN` vs explicit subquery. Direct join is fine here.
    Also, check if any specific column names are mandated for output other than description. No, just "Sütunlar: müşteri adı, toplam harcama". So `c.name` and the alias `toplam_harcama` fits this.

    Final decision on SQL content:
    ```sql
    SELECT c.name, SUM(p.price * o.quantity) AS toplam_harcama
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    JOIN products p ON o.product_id = p.id
    WHERE SUBSTR(o.order_date, 1, 4) = '2026'
    GROUP BY c.id
    ORDER BY toplam_harcama DESC
    LIMIT 3;
    ```

    Wait, I need to make sure `name` is not ambiguous. Since `customers.name` is selected via alias logic, it's fine.

    One nuance: "Sadece sorguyu tek bir ```sql bloğu içinde ver."
    If I put text inside the block (like comments), that might be okay but usually users want just clean SQL. I will add a comment at top if needed? No, keep it clean.

    Let's refine the `WHERE` clause slightly to ensure robustness: `LIKE '2026%'` is also fine and often preferred over SUBSTR for string start matching in SQLite. `SUBSTR` might be slightly more explicit but both work. I'll stick with `SUBSTR` as it handles exactly "2026". Actually `LIKE '2026%'` is more idiomatic SQL. Let's use `LIKE`.
    Wait, `order_date` is TEXT. `LIKE '2026%'` matches '2026-...'.
    However, `SUBSTR(o.order_date, 1, 4) = '2026'` avoids potential case sensitivity issues or weird characters if not normalized, though unlikely here. `LIKE` is fine too. Let's use `SUBSTR` as it feels slightly more precise for year extraction logic without wildcard ambiguity (though there isn't much). I'll stick with `SUBSTR` just to be explicit about extracting the year part.
    Actually, standard practice in SQLite for date filtering on string columns often uses `LIKE`. I will use `LIKE '2026%'` as it's cleaner.

    Wait, re-reading constraint: "Sadece sorguyu tek bir ```sql bloğu içinde ver."
    Okay, I will output the block only.

    One last thought: Should I use Turkish column names? The schema is English (`customers`, `orders`). SQL identifiers usually follow casing conventions of the DB design (snake_case/camelCase). Aliases can be anything. Since the user asked in Turkish ("müsiteri adı"), using a Turkish alias for clarity is better.

    Revised Plan:
    1. Open ```sql block.
    2. Write Query.
    3. Close ``` block.
    4. No other text.

    Wait, looking at the instruction "Sadece sorguyu tek bir ```sql bloğu içinde ver." (Give ONLY the query in a single ```sql block). This is strict. I will not add any conversational filler.

    Query:
    SELECT c.name, SUM(p.price * o.quantity) AS toplam_harcama
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    JOIN products p ON o.product_id = p.id
    WHERE SUBSTR(o.order_date, 1, 4) = '2026'
    GROUP BY c.id
    ORDER BY toplam_harcama DESC
    LIMIT 3;

    Looks solid. I will verify `GROUP BY`. In SQLite, if you select columns not in the aggregation function, they must be in the `GROUP BY` clause OR functionally dependent on grouped keys. Since `c.name` is fully determined by `c.id` (PK), grouping by `c.id` is sufficient and correct.

    Final check on constraints again: "Toplam harcamaya göre azalan sırala." -> `ORDER BY toplam_harcama DESC`. Correct.
    "En çok harcama yapan 3 müşteriyi listele." -> `LIMIT 3`. Correct.
    "2026 yılında (order_date '2026' ile başlayan siparişler)" -> `WHERE ... = '2026'` or `LIKE '2026%'`. I will use `SUBSTR` for exactness on year string.

    Okay, ready.

    Wait, one detail in the instruction: "Sadece sorguyu tek bir ```sql bloğu içinde ver."
    Does it mean I shouldn't include markdown backticks around the code? No, it says "within a single ```sql block". So markdown is expected. It means no text outside the markdown block.

    Let's write it.


## Cevap

```sql
SELECT c.name, SUM(p.price * o.quantity) AS toplam_harcama
FROM customers c
JOIN orders o ON c.id = o.customer_id
JOIN products p ON o.product_id = p.id
WHERE SUBSTR(o.order_date, 1, 4) = '2026'
GROUP BY c.id
ORDER BY toplam_harcama DESC
LIMIT 3;
```

## Notlandırılan kod/komut

```
SELECT c.name, SUM(p.price * o.quantity) AS toplam_harcama
FROM customers c
JOIN orders o ON c.id = o.customer_id
JOIN products p ON o.product_id = p.id
WHERE SUBSTR(o.order_date, 1, 4) = '2026'
GROUP BY c.id
ORDER BY toplam_harcama DESC
LIMIT 3;
```
