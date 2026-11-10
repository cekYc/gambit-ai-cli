WITH satis_hesapla AS (
  SELECT
    u.id AS urun_id,
    u.ad AS urun_adi,
    SUM(sk.adet) AS brut_adet,
    SUM(COALESCE(iade_toplami.iade_adet, 0)) AS iade_adet_toplami,
    SUM((sk.adet - COALESCE(iade_toplami.iade_adet, 0)) * sk.birim_fiyat) AS net_ciro
  FROM urunler u
  LEFT JOIN siparis_kalemleri sk ON sk.urun_id = u.id
  LEFT JOIN (
    SELECT urun_id, siparis_id, SUM(adet) AS iade_adet
    FROM iadeler
    GROUP BY urun_id, siparis_id
  ) iade_toplami
    ON iade_toplami.siparis_id = sk.siparis_id
   AND iade_toplami.urun_id = sk.urun_id
  GROUP BY u.id, u.ad
)
SELECT
  urun_adi,
  (brut_adet - iade_adet_toplami) AS net_adet,
  ROUND(net_ciro, 2) AS net_ciro
FROM satis_hesapla
ORDER BY net_ciro DESC, urun_adi ASC
LIMIT 5;