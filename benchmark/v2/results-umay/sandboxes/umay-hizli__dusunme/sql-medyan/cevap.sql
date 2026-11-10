-- Her şehir için: sipariş sayısı ve sipariş tutarlarının medyanı (2 ondalık)
-- Sadece en az 2 siparişi olan şehirler; medyana göre azalan, eşitlikte şehre göre artan
WITH order_totals AS (
    SELECT
        s.id AS siparis_id,
        m.sehir,
        COALESCE(SUM(sk.adet * sk.birim_fiyat), 0) AS toplam
    FROM siparisler s
    JOIN musteriler m ON m.id = s.musteri_id
    LEFT JOIN siparis_kalemleri sk ON sk.siparis_id = s.id
    GROUP BY s.id, m.sehir
),
ranked AS (
    SELECT
        sehir,
        toplam,
        ROW_NUMBER() OVER (PARTITION BY sehir ORDER BY toplam) AS rn_asc,
        COUNT(*) OVER (PARTITION BY sehir) AS cnt
    FROM order_totals
),
medians AS (
    SELECT
        sehir,
        AVG(toplam) AS medyan
    FROM ranked
    WHERE (cnt % 2 = 1 AND rn_asc = (cnt + 1) / 2)
       OR (cnt % 2 = 0 AND rn_asc IN (cnt / 2, cnt / 2 + 1))
    GROUP BY sehir
)
SELECT
    m.sehir AS sehir,
    COUNT(o.siparis_id) AS siparis_sayisi,
    ROUND(m.medyan, 2) AS medyan
FROM medians m
JOIN order_totals o ON o.sehir = m.sehir
GROUP BY m.sehir, m.medyan
HAVING COUNT(o.siparis_id) >= 2
ORDER BY medyan DESC, m.sehir ASC;