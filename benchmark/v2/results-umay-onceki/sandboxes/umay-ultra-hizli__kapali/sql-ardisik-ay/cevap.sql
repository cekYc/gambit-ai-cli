WITH 
-- Get distinct customer-month pairs from orders
customer_months AS (
    SELECT DISTINCT m.ad, substr(s.tarih, 1, 7) as ay
    FROM musteriler m
    JOIN siparisler s ON m.id = s.musteri_id
),
-- Convert month to numeric and assign row number for consecutive grouping
numbered AS (
    SELECT ad, ay,
           (cast(substr(ay, 1, 4) as integer) * 12 + cast(substr(ay, 6, 2) as integer)) as ay_num,
           ROW_NUMBER() OVER (PARTITION BY ad ORDER BY ay) as rn
    FROM customer_months
),
-- Identify groups of consecutive months (same ay_num - rn means consecutive)
groups AS (
    SELECT ad, ay, ay_num - rn as grp
    FROM numbered
),
-- Count months in each group, filter sequences >= 3 months
group_counts AS (
    SELECT ad, grp, COUNT(*) as seq_len, MIN(ay) as start_ay
    FROM groups
    GROUP BY ad, grp
    HAVING seq_len >= 3
),
-- Select the longest sequence per customer (earliest start on tie)
longest_seq AS (
    SELECT ad, seq_len, start_ay,
           ROW_NUMBER() OVER (PARTITION BY ad ORDER BY seq_len DESC, start_ay ASC) as rn
    FROM group_counts
)
SELECT ad as müsteri_adı, seq_len as seri_uzunluğu, start_ay as serinin_basladığı_ay
FROM longest_seq
WHERE rn = 1
ORDER BY seq_len DESC, ad ASC;