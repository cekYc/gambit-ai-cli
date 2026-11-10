WITH urun_iade AS (
    SELECT urun_id, SUM(adet) AS iade_adet
    FROM iadeler
    GROUP BY urun_id
),
siparis_urun_toplam AS (
    SELECT sk.urun_id,
           SUM(sk.adet) AS toplam_adet,
           SUM(sk.adet * sk.birim_fiyat) AS toplam_ciro
    FROM siparis_kalemleri sk
    GROUP BY sk.urun_id
),
siparis_iade_detay AS (
    SELECT sk.siparis_id,
           sk.urun_id,
           SUM(COALESCE(i.adet, 0)) AS iade_adet,
           SUM(COALESCE(i.adet, 0) * sk.birim_fiyat) AS iade_ciro
    FROM siparis_kalemleri sk
    LEFT JOIN iadeler i
      ON i.siparis_id = sk.siparis_id
     AND i.urun_id = sk.urun_id
    GROUP BY sk.siparis_id, sk.urun_id
),
net_hesap AS (
    SELECT u.ad AS urun_adi,
           COALESCE(s.toplam_adet, 0) - COALESCE(ui.iade_adet, 0) AS net_adet,
           COALESCE(s.toplam_ciro, 0) - COALESCE(sd.iade_ciro, 0) AS net_ciro
    FROM urunler u
    LEFT JOIN siparis_urun_toplam s ON s.urun_id = u.id
    LEFT JOIN urun_iade ui ON ui.urun_id = u.id
    LEFT JOIN (
        SELECT urun_id, SUM(iade_adet) AS iade_adet, SUM(iade_ciro) AS iade_ciro
        FROM siparis_iade_detay
        GROUP BY urun_id
    ) sd ON sd.urun_id = u.id
)
SELECT urun_adi,
       net_adet,
       printf('%.2f', net_ciro) AS net_ciro
FROM net_hesap
ORDER BY net_ciro DESC, urun_adi ASC
LIMIT 5;