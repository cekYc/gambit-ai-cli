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
siralanmis AS (
    SELECT 
        sehir,
        tutar,
        ROW_NUMBER() OVER (PARTITION BY sehir ORDER BY tutar) as rn,
        COUNT(*) OVER (PARTITION BY sehir) as cnt
    FROM siparis_tutarlari
),
medyan_hesapla AS (
    SELECT 
        sehir,
        cnt as siparis_sayisi,
        CASE 
            WHEN cnt % 2 = 1 THEN 
                MAX(CASE WHEN rn = (cnt + 1) / 2 THEN tutar END)
            ELSE 
                (MAX(CASE WHEN rn = cnt / 2 THEN tutar END) + 
                 MAX(CASE WHEN rn = cnt / 2 + 1 THEN tutar END)) / 2.0
        END as medyan
    FROM siralanmis
    WHERE cnt >= 2
    GROUP BY sehir, cnt
)
SELECT 
    sehir,
    siparis_sayisi,
    ROUND(medyan, 2) as medyan
FROM medyan_hesapla
ORDER BY medyan DESC, sehir ASC;