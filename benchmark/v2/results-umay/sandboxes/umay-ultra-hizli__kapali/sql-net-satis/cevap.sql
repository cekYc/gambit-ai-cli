WITH IadeToplam AS (
  -- Her ürün için toplam iade edilen adedi hesapla
  SELECT urun_id, SUM(adet) AS toplam_iade_adedi FROM iadeler GROUP BY urun_id
),
SiparisKalemleri AS (
  -- Tüm sipariş kalemlerini al
  SELECT
    sk.urun_id,
    sk.adet AS siparis_adeti,
    sk.birim_fiyat,
    sk.siparis_id
  FROM siparis_kalemleri sk
),
UrunNetSatis AS (
  -- Net adedi hesapla
  SELECT
    sk.urun_id,
    SUM(sk.siparis_adeti) - COALESCE(SUM(it.toplam_iade_adedi), 0) AS net_adet
  FROM SiparisKalemleri sk
  LEFT JOIN IadeToplam it ON sk.urun_id = it.urun_id
  GROUP BY sk.urun_id
),
UrunNetCiro AS (
  -- Net ciroyu hesapla: (Toplam Sipariş Adedi - Toplam İade Edilen Adet) * Ortalama Birim Fiyat
  -- Daha doğru hesaplama için, her ürünün toplam net adedi üzerinden ortalama birim fiyatı kullanmak yerine,
  -- tüm sipariş kalemlerinin fiyatlarını kullanarak net ciroyu hesaplamalıyız.
  SELECT
    sk.urun_id,
    SUM(sk.siparis_adeti * sk.birim_fiyat) - 
    SUM(i.adet * sk.birim_fiyat) AS net_ciro
  FROM SiparisKalemleri sk
  LEFT JOIN iadeler i ON sk.siparis_id = i.siparis_id AND sk.urun_id = i.urun_id
  GROUP BY sk.urun_id
)
SELECT
  u.ad AS urun_adi,
  uns.net_adet,
  ROUND(unc.net_ciro, 2) AS net_ciro
FROM urunler u
JOIN UrunNetSatis uns ON u.id = uns.urun_id
JOIN UrunNetCiro unc ON u.id = unc.urun_id
ORDER BY
  net_ciro DESC,
  urun_adi ASC
LIMIT 5;