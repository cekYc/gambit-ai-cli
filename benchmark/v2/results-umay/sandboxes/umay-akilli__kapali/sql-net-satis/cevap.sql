WITH 
satis_ozet AS (
    SELECT 
        sk.urun_id,
        SUM(sk.adet) AS toplam_satilan_adet,
        SUM(sk.adet * sk.birim_fiyat) AS brut_ciro
    FROM siparis_kalemleri sk
    GROUP BY sk.urun_id
),
iade_ozet AS (
    SELECT 
        i.urun_id,
        SUM(i.adet) AS toplam_iade_adet
    FROM iadeler i
    GROUP BY i.urun_id
),
siparis_kalem_iade AS (
    SELECT 
        i.siparis_id,
        i.urun_id,
        SUM(i.adet) AS iade_adet
    FROM iadeler i
    GROUP BY i.siparis_id, i.urun_id
),
net_ciro_hesap AS (
    SELECT 
        sk.urun_id,
        SUM((sk.adet - COALESCE(ski.iade_adet, 0)) * sk.birim_fiyat) AS net_ciro
    FROM siparis_kalemleri sk
    LEFT JOIN siparis_kalem_iade ski 
        ON sk.siparis_id = ski.siparis_id AND sk.urun_id = ski.urun_id
    GROUP BY sk.urun_id
)
SELECT 
    u.ad AS urun_adi,
    COALESCE(so.toplam_satilan_adet, 0) - COALESCE(io.toplam_iade_adet, 0) AS net_adet,
    ROUND(COALESCE(nch.net_ciro, 0), 2) AS net_ciro
FROM urunler u
LEFT JOIN satis_ozet so ON u.id = so.urun_id
LEFT JOIN iade_ozet io ON u.id = io.urun_id
LEFT JOIN net_ciro_hesap nch ON u.id = nch.urun_id
ORDER BY net_ciro DESC, urun_adi ASC
LIMIT 5;