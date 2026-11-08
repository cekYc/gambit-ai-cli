WITH 
satis_toplam AS (
    SELECT 
        urun_id,
        SUM(adet) AS toplam_satilan
    FROM siparis_kalemleri
    GROUP BY urun_id
),
iade_toplam AS (
    SELECT 
        urun_id,
        SUM(adet) AS toplam_iade
    FROM iadeler
    GROUP BY urun_id
),
net_satis AS (
    SELECT 
        sk.urun_id,
        sk.siparis_id,
        sk.adet,
        sk.birim_fiyat,
        COALESCE(i.toplam_iade_siparis, 0) AS iade_adet
    FROM siparis_kalemleri sk
    LEFT JOIN (
        SELECT 
            siparis_id,
            urun_id,
            SUM(adet) AS toplam_iade_siparis
        FROM iadeler
        GROUP BY siparis_id, urun_id
    ) i ON sk.siparis_id = i.siparis_id AND sk.urun_id = i.urun_id
),
urun_net AS (
    SELECT 
        u.ad AS urun_adi,
        COALESCE(st.toplam_satilan, 0) - COALESCE(it.toplam_iade, 0) AS net_adet,
        SUM((ns.adet - ns.iade_adet) * ns.birim_fiyat) AS net_ciro
    FROM urunler u
    LEFT JOIN satis_toplam st ON u.id = st.urun_id
    LEFT JOIN iade_toplam it ON u.id = it.urun_id
    LEFT JOIN net_satis ns ON u.id = ns.urun_id
    GROUP BY u.id, u.ad, st.toplam_satilan, it.toplam_iade
)
SELECT 
    urun_adi,
    net_adet,
    ROUND(net_ciro, 2) AS net_ciro
FROM urun_net
ORDER BY net_ciro DESC, urun_adi ASC
LIMIT 5;