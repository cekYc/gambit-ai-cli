WITH iade_toplam AS (
    SELECT siparis_id, urun_id, SUM(adet) AS iade_adet
    FROM iadeler
    GROUP BY siparis_id, urun_id
),
kalem_net AS (
    SELECT 
        sk.urun_id,
        sk.siparis_id,
        sk.adet,
        sk.birim_fiyat,
        COALESCE(it.iade_adet, 0) AS iade_adet,
        (sk.adet - COALESCE(it.iade_adet, 0)) AS net_adet,
        (sk.adet - COALESCE(it.iade_adet, 0)) * sk.birim_fiyat AS net_ciro
    FROM siparis_kalemleri sk
    LEFT JOIN iade_toplam it ON sk.siparis_id = it.siparis_id AND sk.urun_id = it.urun_id
),
urun_ozet AS (
    SELECT 
        u.ad AS urun_adi,
        SUM(kn.net_adet) AS net_adet,
        SUM(kn.net_ciro) AS net_ciro
    FROM kalem_net kn
    JOIN urunler u ON kn.urun_id = u.id
    GROUP BY u.id, u.ad
)
SELECT 
    urun_adi,
    net_adet,
    ROUND(net_ciro, 2) AS net_ciro
FROM urun_ozet
ORDER BY net_ciro DESC, urun_adi ASC
LIMIT 5;