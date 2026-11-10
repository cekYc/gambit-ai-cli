WITH city_customers AS (
    SELECT m.sehir, COUNT(DISTINCT s.musteri_id) AS musteri_sayisi
    FROM musteriler m
    JOIN siparisler s ON m.id = s.musteri_id
    GROUP BY m.sehir
),
city_ciro_raw AS (
    SELECT m.sehir,
           SUM(CASE WHEN NOT EXISTS (
               SELECT 1 FROM iadeler i 
               WHERE i.siparis_id = sk.siparis_id 
               AND i.urun_id = sk.urun_id
           ) THEN sk.adet * sk.birim_fiyat ELSE 0 END) AS raw_ciro
    FROM musteriler m
    JOIN siparisler s ON m.id = s.musteri_id
    JOIN siparis_kalemleri sk ON s.id = sk.siparis_id
    GROUP BY m.sehir
)
SELECT 
    m.sehir,
    COALESCE(cc.musteri_sayisi, 0) AS musteri_sayisi,
    ROUND(COALESCE(cr.raw_ciro, 0), 2) AS ciro
FROM (SELECT DISTINCT sehir FROM musteriler) m
LEFT JOIN city_customers cc ON m.sehir = cc.sehir
LEFT JOIN city_ciro_raw cr ON m.sehir = cr.sehir
ORDER BY ciro DESC, m.sehir ASC;
