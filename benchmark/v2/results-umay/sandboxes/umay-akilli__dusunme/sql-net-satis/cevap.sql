WITH 
satislar AS (
    SELECT 
        sk.urun_id,
        sk.siparis_id,
        sk.adet,
        sk.birim_fiyat
    FROM siparis_kalemleri sk
),
iade_toplam AS (
    SELECT 
        i.siparis_id,
        i.urun_id,
        SUM(i.adet) AS iade_adet
    FROM iadeler i
    GROUP BY i.siparis_id, i.urun_id
),
net_satis AS (
    SELECT 
        s.urun_id,
        s.siparis_id,
        s.adet,
        s.birim_fiyat,
        COALESCE(it.iade_adet, 0) AS iade_adet,
        (s.adet - COALESCE(it.iade_adet, 0)) AS net_adet,
        (s.adet - COALESCE(it.iade_adet, 0)) * s.birim_fiyat AS net_ciro
    FROM satislar s
    LEFT JOIN iade_toplam it ON s.siparis_id = it.siparis_id AND s.urun_id = it.urun_id
)
SELECT 
    u.ad AS urun_adi,
    SUM(ns.net_adet) AS net_adet,
    ROUND(SUM(ns.net_ciro), 2) AS net_ciro
FROM net_satis ns
JOIN urunler u ON ns.urun_id = u.id
GROUP BY u.id, u.ad
ORDER BY net_ciro DESC, urun_adi ASC
LIMIT 5;