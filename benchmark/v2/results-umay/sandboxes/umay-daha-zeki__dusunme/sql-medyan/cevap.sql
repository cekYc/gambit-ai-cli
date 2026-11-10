WITH OrderTotals AS (
    SELECT
        m.sehir,
        s.id AS siparis_id,
        SUM(sk.adet * sk.birim_fiyat) AS order_total
    FROM siparisler s
    JOIN musteriler m ON s.musteri_id = m.id
    JOIN siparis_kalemleri sk ON s.id = sk.siparis_id
    GROUP BY s.id, m.sehir
),
RankedCityStats AS (
    SELECT
        sehir,
        siparis_id,
        order_total,
        COUNT(siparis_id) OVER (PARTITION BY sehir) AS total_orders,
        ROW_NUMBER() OVER (PARTITION BY sehir ORDER BY order_total ASC) AS rn_asc
    FROM OrderTotals
)
-- Final Selection: Calculate median and filter
SELECT
    T1.sehir,
    T1.total_orders AS siparis_sayisi,
    CAST(
        CASE
            -- Tek sayıda sipariş (N): Medyan, ortadaki sıradaki değerdir ((N+1)/2)
            WHEN T1.total_orders % 2 = 1 THEN (
                SELECT order_total FROM RankedCityStats WHERE sehir = T1.sehir AND rn_asc = (T1.total_orders + 1) / 2
            )
            -- Çift sayıda sipariş (N): Medyan, N/2 ve N/2 + 1 sıradaki değerlerin ortalamasıdır
            WHEN T1.total_orders % 2 = 0 THEN (
                SELECT AVG(order_total)
                FROM RankedCityStats
                WHERE sehir = T1.sehir
                AND rn_asc IN (T1.total_orders / 2, T1.total_orders / 2 + 1)
            )
            ELSE NULL
        END AS REAL) AS medyan
FROM RankedCityStats T1
WHERE T1.total_orders >= 2
GROUP BY T1.sehir, T1.total_orders
ORDER BY medyan DESC, T1.sehir ASC;