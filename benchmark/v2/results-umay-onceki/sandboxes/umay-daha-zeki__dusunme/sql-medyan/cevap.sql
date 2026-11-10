WITH OrderTotals AS (
    -- Her siparişin toplam tutarını ve şehir bilgisini hesaplar
    SELECT
        s.id AS siparis_id,
        m.sehir,
        SUM(sk.adet * sk.birim_fiyat) AS total_amount
    FROM siparisler s
    JOIN musteriler m ON s.musteri_id = m.id
    JOIN siparis_kalemleri sk ON s.id = sk.siparis_id
    GROUP BY s.id, m.sehir
),
RankedTotals AS (
    -- Her şehirdeki sipariş tutarlarını sıralar ve istatistiksel verileri hesaplar
    SELECT
        sehir,
        total_amount,
        COUNT(siparis_id) OVER (PARTITION BY sehir) AS siparis_sayisi,
        COUNT(*) OVER (PARTITION BY sehir) AS total_count,
        ROW_NUMBER() OVER (PARTITION BY sehir ORDER BY total_amount ASC) AS rn
    FROM OrderTotals
)
-- Sonuçları çeker, 2 veya daha fazla siparişli şehirleri filtreler ve medyanı hesaplar
SELECT
    rt.sehir,
    rt.siparis_sayisi,
    ROUND(
        (SELECT AVG(T.total_amount) FROM RankedTotals AS T WHERE T.sehir = rt.sehir AND T.rn IN (rt.total_count / 2, rt.total_count / 2 + 1)),
        2
    ) AS medyan
FROM RankedTotals AS rt
WHERE rt.total_count >= 2
GROUP BY rt.sehir, rt.siparis_sayisi
ORDER BY medyan DESC, rt.sehir ASC;