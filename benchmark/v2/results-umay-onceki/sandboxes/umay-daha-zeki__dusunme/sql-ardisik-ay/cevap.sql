WITH MonthlyOrders AS (
    -- 1. Get distinct ordering months (YYYYMM key) per customer
    SELECT
        m.ad AS customer_name,
        strftime('%Y%m', s.tarih) AS month_key
    FROM musteriler m
    JOIN siparisler s ON m.id = s.musteri_id
    GROUP BY m.id, month_key
),
RankedMonths AS (
    -- 2. Rank months and assign sequence IDs (Gaps and Islands)
    SELECT
        customer_name,
        month_key,
        ROW_NUMBER() OVER (PARTITION BY customer_name ORDER BY month_key) AS rn,
        (CAST(month_key AS INTEGER) - ROW_NUMBER() OVER (PARTITION BY customer_name ORDER BY month_key)) AS sequence_id
    FROM MonthlyOrders
)
-- 3. Aggregate sequences, filter, and select final result
SELECT
    customer_name,
    COUNT(month_key) AS sequence_length,
    -- Reconstruct 'YYYY-MM' from the minimum month_key of the sequence
    SUBSTR(CAST(MIN(month_key) AS TEXT), 1, 4) || '-' || SUBSTR(CAST(MIN(month_key) AS TEXT), 5, 2) AS start_month
FROM RankedMonths
GROUP BY customer_name, sequence_id
HAVING COUNT(month_key) >= 3
ORDER BY
    sequence_length DESC,
    customer_name ASC;