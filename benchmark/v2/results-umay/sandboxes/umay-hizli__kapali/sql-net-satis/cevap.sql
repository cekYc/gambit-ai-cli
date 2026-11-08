WITH iade_toplamlari AS (
    SELECT siparis_id, urun_id, SUM(adet) AS iade_adet
    FROM iadeler
    GROUP BY siparis_id, urun_id
),
kalem_net AS (
    SELECT sk.urun_id,
           sk.adet - COALESCE(it.iade_adet, 0) AS net_adet,
           (sk.adet - COALESCE(it.iade_adet, 0)) * sk.birim_fiyat AS net_ciro
    FROM siparis_kalemleri sk
    LEFT JOIN iade_toplamlari it
      ON it.siparis_id = sk.siparis_id
     AND it.urun_id = sk.urun_id
),
urun_ozet AS (
    SELECT urun_id,
           SUM(net_adet) AS toplam_net_adet,
           SUM(net_ciro) AS toplam_net_ciro
    FROM kalem_net
    GROUP BY urun_id
)
SELECT u.ad AS urun_adi,
       zo.toplam_net_adet AS net_adet,
       ROUND(zo.toplam_net_ciro, 2) AS net_ciro
FROM urun_ozet zo
JOIN urunler u ON u.id = zo.urun_id
ORDER BY zo.toplam_net_ciro DESC, u.ad ASC
LIMIT 5;