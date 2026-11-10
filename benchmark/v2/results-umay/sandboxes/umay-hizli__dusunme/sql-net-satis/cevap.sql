WITH iade_urun_toplam AS (
  SELECT urun_id, SUM(adet) AS iade_toplam
  FROM iadeler
  GROUP BY urun_id
),
iade_kalem_toplam AS (
  SELECT siparis_id, urun_id, SUM(adet) AS iade_adet
  FROM iadeler
  GROUP BY siparis_id, urun_id
),
urun_ozet AS (
  SELECT u.id AS urun_id,
         u.ad AS urun_adi,
         SUM(sk.adet) AS satilan_toplam,
         COALESCE(iu.iade_toplam, 0) AS iade_toplam,
         SUM(sk.adet) - COALESCE(iu.iade_toplam, 0) AS net_adet,
         SUM((sk.adet - COALESCE(ik.iade_adet, 0)) * sk.birim_fiyat) AS net_ciro
  FROM urunler u
  JOIN siparis_kalemleri sk ON sk.urun_id = u.id
  LEFT JOIN iade_urun_toplam iu ON iu.urun_id = u.id
  LEFT JOIN iade_kalem_toplam ik ON ik.siparis_id = sk.siparis_id AND ik.urun_id = sk.urun_id
  GROUP BY u.id, u.ad
)
SELECT urun_adi,
       net_adet,
       printf('%.2f', net_ciro) AS net_ciro
FROM urun_ozet
ORDER BY net_ciro DESC, urun_adi ASC
LIMIT 5;
