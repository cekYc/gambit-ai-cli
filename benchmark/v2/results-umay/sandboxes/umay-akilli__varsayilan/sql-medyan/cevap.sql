WITH siparis_tutarlari AS (
    SELECT 
        m.sehir,
        s.id AS siparis_id,
        SUM(sk.adet * sk.birim_fiyat) AS tutar
    FROM siparisler s
    JOIN musteriler m ON s.musteri_id = m.id
    JOIN siparis_kalemleri sk ON s.id = sk.siparis_id
    GROUP BY s.id, m.sehir
),
sehir_siparis_sayilari AS (
    SELECT 
        sehir,
        COUNT(*) AS siparis_sayisi
    FROM siparis_tutarlari
    GROUP BY sehir
    HAVING COUNT(*) >= 2
),
medyan_hesaplama AS (
    SELECT 
        st.sehir,
        st.tutar,
        ROW_NUMBER() OVER (PARTITION BY st.sehir ORDER BY st.tutar) AS rn,
        COUNT(*) OVER (PARTITION BY st.sehir) AS cnt
    FROM siparis_tutarlari st
    JOIN sehir_siparis_sayilari sss ON st.sehir = sss.sehir
)
SELECT 
    mh.sehir,
    sss.siparis_sayisi,
    ROUND(
        CASE 
            WHEN mh.cnt % 2 = 1 THEN
                MAX(CASE WHEN mh.rn = (mh.cnt + 1) / 2 THEN mh.tutar END)
            ELSE
                (MAX(CASE WHEN mh.rn = mh.cnt / 2 THEN mh.tutar END) +
                 MAX(CASE WHEN mh.rn = mh.cnt / 2 + 1 THEN mh.tutar END)) / 2.0
        END, 2
    ) AS medyan
FROM medyan_hesaplama mh
JOIN sehir_siparis_sayilari sss ON mh.sehir = sss.sehir
GROUP BY mh.sehir, sss.siparis_sayisi
ORDER BY medyan DESC, mh.sehir ASC;