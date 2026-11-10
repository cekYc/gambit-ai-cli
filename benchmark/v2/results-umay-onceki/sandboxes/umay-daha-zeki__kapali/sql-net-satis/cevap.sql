
WITH SiparisAdetler AS (
    -- Her ürün için toplam satılan adeti bulma
    SELECT 
        sk.urun_id,
        SUM(sk.adet) AS toplam_satilan_adet
    FROM siparis_kalemleri sk
    GROUP BY sk.urun_id
),
IadeAdetler AS (
    -- Her ürün için toplam iade edilen adeti bulma
    SELECT 
        i.urun_id,
        SUM(i.adet) AS toplam_iade_adet
    FROM iadeler i
    GROUP BY i.urun_id
),
NetSatis AS (
    -- Net adeti hesaplama
    SELECT
        sa.urun_id,
        sa.toplam_satilan_adet - COALESCE(ia.toplam_iade_adet, 0) AS net_adet
    FROM SiparisAdetler sa
    LEFT JOIN IadeAdetler ia ON sa.urun_id = ia.urun_id
),
NetCiro AS (
    -- Net ciroyu hesaplama
    SELECT
        sk.urun_id,
        SUM((
            sk.adet - (SELECT COALESCE(SUM(i.adet), 0) FROM iadeler i WHERE i.siparis_id = sk.siparis_id AND i.urun_id = sk.urun_id)
        ) * sk.birim_fiyat)
        AS net_ciro
    FROM siparis_kalemleri sk
    GROUP BY sk.urun_id
)
-- Nihai listeleme ve sıralama
SELECT
    u.ad AS urun_adi,
    ns.net_adet,
    ROUND(nc.net_ciro, 2) AS net_ciro
FROM urunler u
JOIN NetSatis ns ON u.id = ns.urun_id
JOIN NetCiro nc ON u.id = nc.urun_id
ORDER BY
    net_ciro DESC,
    urun_adi ASC
LIMIT 5;
