WITH satis_ozeti AS (
    SELECT 
        sk.urun_id,
        SUM(sk.adet) AS toplam_satilan
    FROM siparis_kalemleri sk
    GROUP BY sk.urun_id
),
iade_ozeti AS (
    SELECT 
        i.urun_id,
        SUM(i.adet) AS toplam_iade
    FROM iadeler i
    GROUP BY i.urun_id
),
siparis_iade_detay AS (
    SELECT 
        sk.siparis_id,
        sk.urun_id,
        sk.adet AS satilan_adet,
        sk.birim_fiyat,
        COALESCE(SUM(i.adet), 0) AS iade_adet
    FROM siparis_kalemleri sk
    LEFT JOIN iadeler i 
        ON i.siparis_id = sk.siparis_id 
       AND i.urun_id = sk.urun_id
    GROUP BY sk.siparis_id, sk.urun_id
),
net_ciro_hesap AS (
    SELECT 
        urun_id,
        SUM((satilan_adet - iade_adet) * birim_fiyat) AS net_ciro
    FROM siparis_iade_detay
    GROUP BY urun_id
)
SELECT 
    u.ad AS urun_adi,
    COALESCE(so.toplam_satilan, 0) - COALESCE(io.toplam_iade, 0) AS net_adet,
    ROUND(COALESCE(nch.net_ciro, 0), 2) AS net_ciro
FROM urunler u
LEFT JOIN satis_ozeti so ON u.id = so.urun_id
LEFT JOIN iade_ozeti io ON u.id = io.urun_id
LEFT JOIN net_ciro_hesap nch ON u.id = nch.urun_id
ORDER BY net_ciro DESC, urun_adi ASC
LIMIT 5;