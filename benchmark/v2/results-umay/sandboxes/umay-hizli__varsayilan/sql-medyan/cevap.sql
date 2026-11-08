WITH siparis_tutar AS (
    SELECT
        s.id AS siparis_id,
        m.sehir,
        SUM(sk.adet * sk.birim_fiyat) AS tutar
    FROM siparisler s
    JOIN musteriler m ON s.musteri_id = m.id
    JOIN siparis_kalemleri sk ON sk.siparis_id = s.id
    GROUP BY s.id, m.sehir
),
sirali AS (
    SELECT
        sehir,
        tutar,
        ROW_NUMBER() OVER (PARTITION BY sehir ORDER BY tutar) AS sira,
        COUNT(*) OVER (PARTITION BY sehir) AS adet
    FROM siparis_tutar
),
medyan_hesap AS (
    SELECT
        sehir,
        adet AS siparis_sayisi,
        CASE
            WHEN adet % 2 = 1 THEN
                MAX(CASE WHEN sira = (adet + 1) / 2 THEN tutar END)
            ELSE
                (MAX(CASE WHEN sira = adet / 2 THEN tutar END) +
                 MAX(CASE WHEN sira = adet / 2 + 1 THEN tutar END)) / 2.0
        END AS medyan_deger
    FROM sirali
    GROUP BY sehir, adet
    HAVING adet >= 2
)
SELECT
    sehir,
    siparis_sayisi,
    ROUND(medyan_deger, 2) AS medyan
FROM medyan_hesap
ORDER BY medyan DESC, sehir ASC;