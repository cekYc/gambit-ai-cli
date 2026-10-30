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

Bu problemi en doğru şekilde `LEFT JOIN` ve `IS NULL` filtresiyle çözebilirsin; bu sayede her müşteriye bakılır, sipariş tablosunda karşılığı olmayanlar (hiç sipariş vermeyenler) seçilir ve alfabetik sıralama ile tek bir sorguda sonuç döndürülür.

```sql
SELECT c.name FROM customers c LEFT JOIN orders o ON c.id = o.customer_id WHERE o.id IS NULL ORDER BY c.name;
```

## Notlandırılan kod/komut

```
SELECT c.name FROM customers c LEFT JOIN orders o ON c.id = o.customer_id WHERE o.id IS NULL ORDER BY c.name;
```
