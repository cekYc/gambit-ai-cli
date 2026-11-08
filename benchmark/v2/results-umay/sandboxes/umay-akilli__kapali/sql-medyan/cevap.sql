WITH siparis_tutar AS (
    SELECT 
        s.id AS siparis_id,
        m.sehir,
        SUM(sk.adet * sk.birim_fiyat) AS tutar
    FROM siparisler s
    JOIN musteriler m ON s.musteri_id = m.id
    JOIN siparis_kalemleri sk ON s.id = sk.siparis_id
    GROUP BY s.id, m.sehir
),
sehir_siparis AS (
    SELECT 
        sehir,
        tutar,
        ROW_NUMBER() OVER (PARTITION BY sehir ORDER BY tutar) AS rn,
        COUNT(*) OVER (PARTITION BY sehir) AS cnt
    FROM siparis_tutar
)
SELECT 
    sehir,
    cnt AS siparis_sayisi,
    ROUND(
        CASE 
            WHEN cnt % 2 = 1 THEN 
                MAX(CASE WHEN rn = (cnt + 1) / 2 THEN tutar END)
            ELSE 
                (MAX(CASE WHEN rn = cnt / 2 THEN tutar END) + MAX(CASE WHEN rn = cnt / 2 + 1 THEN tutar END)) / 2.0
        END, 2
    ) AS medyan
FROM sehir_siparis
WHERE cnt >= 2
GROUP BY sehir, cnt
ORDER BY medyan DESC, sehir ASC;