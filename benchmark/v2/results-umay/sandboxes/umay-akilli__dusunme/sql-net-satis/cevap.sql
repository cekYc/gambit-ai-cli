WITH 
-- Aggregate returns per (siparis_id, urun_id)
iade_agg AS (
    SELECT siparis_id, urun_id, SUM(adet) AS iade_adet
    FROM iadeler
    GROUP BY siparis_id, urun_id
),
-- Calculate net per order line
satis_net AS (
    SELECT 
        sk.urun_id,
        sk.adet - COALESCE(ia.iade_adet, 0) AS net_adet,
        (sk.adet - COALESCE(ia.iade_adet, 0)) * sk.birim_fiyat AS net_ciro
    FROM siparis_kalemleri sk
    LEFT JOIN iade_agg ia ON sk.siparis_id = ia.siparis_id AND sk.urun_id = ia.urun_id
)
SELECT 
    u.ad AS urun_adi,
    SUM(sn.net_adet) AS net_adet,
    ROUND(SUM(sn.net_ciro), 2) AS net_ciro
FROM satis_net sn
JOIN urunler u ON sn.urun_id = u.id
GROUP BY u.id, u.ad
ORDER BY net_ciro DESC, urun_adi ASC
LIMIT 5;