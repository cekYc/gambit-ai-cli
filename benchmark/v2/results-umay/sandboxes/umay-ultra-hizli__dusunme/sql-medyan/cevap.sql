WITH OrderTotals AS (
    -- Her siparişin toplam tutarını hesapla
    SELECT
        s.id AS siparis_id,
        m.sehir,
        SUM(sk.adet * sk.birim_fiyat) AS tutar
    FROM siparisler s
    JOIN musteriler m ON s.musteri_id = m.id
    JOIN siparis_kalemleri sk ON s.id = sk.siparis_id
    GROUP BY s.id, m.sehir
),
RankedCityData AS (
    -- Şehir bazında sipariş sayısını hesapla ve tutarlara göre sıralama (rank) yap
    SELECT
        sehir,
        tutar,
        COUNT(siparis_id) OVER (PARTITION BY sehir) AS n_orders,
        ROW_NUMBER() OVER (PARTITION BY sehir ORDER BY tutar ASC) AS rn
    FROM OrderTotals
)
-- Sonuçları hesapla, filtrele ve sırala
SELECT
    sehir,
    n_orders AS siparis_sayisi,
    ROUND(
        -- Medyan hesaplaması: Tek sayıda siparişse ortadaki değeri, çift sayıda ise ortadaki iki değerin ortalamasını al.
        ( 
            SUM(CASE
                WHEN n_orders % 2 = 1 AND rn = (n_orders + 1) / 2 THEN tutar
                WHEN n_orders % 2 = 0 AND rn = n_orders / 2 THEN tutar
                WHEN n_orders % 2 = 0 AND rn = n_orders / 2 + 1 THEN tutar
                ELSE 0
            END)
        ) / 
        CASE
            WHEN n_orders % 2 = 1 THEN 1.0
            WHEN n_orders % 2 = 0 THEN 2.0
            ELSE 1.0
        END
    , 2) AS medyan
FROM RankedCityData
WHERE n_orders >= 2
GROUP BY sehir, n_orders
ORDER BY medyan DESC, sehir ASC;