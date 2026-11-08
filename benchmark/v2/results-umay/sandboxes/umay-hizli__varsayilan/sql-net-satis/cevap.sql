WITH iade_toplamlari AS (
    SELECT siparis_id, urun_id, SUM(adet) AS iade_adet
    FROM iadeler
    GROUP BY siparis_id, urun_id
),
kalem_net AS (
    SELECT sk.urun_id,
           sk.adet - COALESCE(i.iade_adet, 0) AS net_kalem_adet,
           (sk.adet - COALESCE(i.iade_adet, 0)) * sk.birim_fiyat AS net_kalem_ciro
    FROM siparis_kalemleri sk
    LEFT JOIN iade_toplamlari i
           ON i.siparis_id = sk.siparis_id
          AND i.urun_id = sk.urun_id
),
urun_ozeti AS (
    SELECT urun_id,
           SUM(net_kalem_adet) AS net_adet,
           SUM(net_kalem_ciro) AS net_ciro
    FROM kalem_net
    GROUP BY urun_id
)
SELECT u.ad AS urun_adi,
       uo.net_adet,
       ROUND(uo.net_ciro, 2) AS net_ciro
FROM urun_ozeti uo
JOIN urunler u ON u.id = uo.urun_id
ORDER BY uo.net_ciro DESC, u.ad ASC
LIMIT 5;