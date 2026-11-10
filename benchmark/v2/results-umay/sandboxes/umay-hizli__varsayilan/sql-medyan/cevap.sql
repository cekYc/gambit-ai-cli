WITH siparis_tutar AS (
    SELECT
        s.id AS siparis_id,
        m.sehir AS sehir,
        COALESCE(SUM(sk.adet * sk.birim_fiyat), 0.0) AS tutar
    FROM siparisler s
    JOIN musteriler m ON s.musteri_id = m.id
    LEFT JOIN siparis_kalemleri sk ON sk.siparis_id = s.id
    GROUP BY s.id, m.sehir
),
sehir_sira AS (
    SELECT
        sehir,
        tutar,
        COUNT(*) OVER (PARTITION BY sehir) AS siparis_sayisi,
        ROW_NUMBER() OVER (PARTITION BY sehir ORDER BY tutar) AS rn_asc,
        ROW_NUMBER() OVER (PARTITION BY sehir ORDER BY tutar DESC) AS rn_desc
    FROM siparis_tutar
),
sehir_medyan AS (
    SELECT
        sehir,
        siparis_sayisi,
        CASE
            WHEN siparis_sayisi % 2 = 1 THEN
                MAX(CASE WHEN rn_asc = (siparis_sayisi + 1) / 2 THEN tutar END)
            ELSE
                (
                    MAX(CASE WHEN rn_asc = siparis_sayisi / 2 THEN tutar END)
                    +
                    MAX(CASE WHEN rn_asc = siparis_sayisi / 2 + 1 THEN tutar END)
                ) / 2.0
        END AS medyan
    FROM sehir_sira
    GROUP BY sehir, siparis_sayisi
    HAVING COUNT(*) >= 2
)
SELECT
    sehir AS sehir,
    siparis_sayisi AS "sipariş sayısı",
    ROUND(medyan, 2) AS medyan
FROM sehir_medyan
ORDER BY medyan DESC, sehir ASC;