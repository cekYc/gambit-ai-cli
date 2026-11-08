WITH iade_toplamlari AS (
    SELECT siparis_id, urun_id, SUM(adet) AS iade_adet
    FROM iadeler
    GROUP BY siparis_id, urun_id
),
kalem_net AS (
    SELECT sk.siparis_id, sk.urun_id,
           sk.adet - COALESCE(it.iade_adet, 0) AS net_adet_kalem,
           (sk.adet - COALESCE(it.iade_adet, 0)) * sk.birim_fiyat AS net_ciro_kalem
    FROM siparis_kalemleri sk
    LEFT JOIN iade_toplamlari it
      ON it.siparis_id = sk.siparis_id
     AND it.urun_id = sk.urun_id
),
urun_ozet AS (
    SELECT kn.urun_id,
           SUM(kn.net_adet_kalem) AS net_adet,
           SUM(kn.net_ciro_kalem) AS net_ciro
    FROM kalem_net kn
    GROUP BY kn.urun_id
)
SELECT u.ad AS urun_adi,
       uo.net_adet,
       printf('%.2f', uo.net_ciro) AS net_ciro
FROM urun_ozet uo
JOIN urunler u ON u.id = uo.urun_id
ORDER BY uo.net_ciro DESC, u.ad ASC
LIMIT 5;