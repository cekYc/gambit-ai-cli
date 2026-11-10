WITH OrderTotals AS (
    SELECT m.sehir, SUM(sk.adet * sk.birim_fiyat) AS tutar
    FROM musteriler m
    JOIN siparisler s ON m.id = s.musteri_id
    JOIN siparis_kalemleri sk ON s.id = sk.siparis_id
    GROUP BY m.sehir, s.id
),
CityOrderCounts AS (
    SELECT sehir, COUNT(*) AS siparis_sayisi
    FROM OrderTotals
    GROUP BY sehir
    HAVING COUNT(*) >= 2
),
OrderedOrders AS (
    SELECT o.sehir, o.tutar,
           ROW_NUMBER() OVER (PARTITION BY o.sehir ORDER BY o.tutar) AS rn,
           COUNT(*) OVER (PARTITION BY o.sehir) AS total_count
    FROM OrderTotals o
),
MedianCalc AS (
    SELECT sehir, total_count,
        CASE WHEN total_count % 2 = 1 THEN
            MAX(CASE WHEN rn = (total_count + 1) / 2 THEN tutar END)
        ELSE
            (MAX(CASE WHEN rn = total_count / 2 THEN tutar END) + MAX(CASE WHEN rn = total_count / 2 + 1 THEN tutar END)) / 2
        END AS medyan
    FROM OrderedOrders
    GROUP BY sehir, total_count
)
SELECT m.sehir, m.siparis_sayisi, ROUND(mc.medyan, 2) AS medyan
FROM CityOrderCounts m
JOIN MedianCalc mc ON m.sehir = mc.sehir
ORDER BY medyan DESC, m.sehir ASC;