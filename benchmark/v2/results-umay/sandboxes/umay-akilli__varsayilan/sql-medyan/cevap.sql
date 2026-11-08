WITH siparis_tutarlari AS (
    SELECT 
        m.sehir,
        s.id as siparis_id,
        SUM(sk.adet * sk.birim_fiyat) as tutar
    FROM siparisler s
    JOIN musteriler m ON s.musteri_id = m.id
    JOIN siparis_kalemleri sk ON s.id = sk.siparis_id
    GROUP BY s.id, m.sehir
),
sehir_siparis_sayilari AS (
    SELECT 
        sehir,
        COUNT(*) as siparis_sayisi
    FROM siparis_tutarlari
    GROUP BY sehir
    HAVING COUNT(*) >= 2
),
siralanmis_tutalar AS (
    SELECT 
        st.sehir,
        st.tutar,
        ROW_NUMBER() OVER (PARTITION BY st.sehir ORDER BY st.tutar) as rn,
        COUNT(*) OVER (PARTITION BY st.sehir) as cnt
    FROM siparis_tutarlari st
    JOIN sehir_siparis_sayilari sss ON st.sehir = sss.sehir
),
medyan_hesapla AS (
    SELECT 
        sehir,
        CASE 
            WHEN cnt % 2 = 1 THEN 
                MAX(CASE WHEN rn = (cnt + 1) / 2 THEN tutar END)
            ELSE 
                (MAX(CASE WHEN rn = cnt / 2 THEN tutar END) + 
                 MAX(CASE WHEN rn = cnt / 2 + 1 THEN tutar END)) / 2.0
        END as medyan
    FROM siralanmis_tutalar
    GROUP BY sehir, cnt
)
SELECT 
    mh.sehir,
    sss.siparis_sayisi,
    ROUND(mh.medyan, 2) as medyan
FROM medyan_hesapla mh
JOIN sehir_siparis_sayilari sss ON mh.sehir = sss.sehir
ORDER BY mh.medyan DESC, mh.sehir ASC;