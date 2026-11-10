WITH veriler AS (
  SELECT u.kategori AS kategori,
         SUM(sk.adet * sk.birim_fiyat) AS ciro
  FROM urunler u
  JOIN siparis_kalemleri sk ON sk.urun_id = u.id
  JOIN siparisler s ON s.id = sk.siparis_id
  WHERE s.tarih LIKE '2025-%'
  GROUP BY u.kategori
),
kategoriler AS (
  SELECT DISTINCT kategori FROM urunler
),
ciro_tum AS (
  SELECT k.kategori AS kategori,
         COALESCE(v.ciro, 0) AS ciro
  FROM kategoriler k
  LEFT JOIN veriler v ON v.kategori = k.kategori
),
sonuc AS (
  SELECT kategori,
         ciro,
         CASE WHEN SUM(ciro) OVER () = 0 THEN 0.0
              ELSE ROUND(ciro * 100.0 / SUM(ciro) OVER (), 1)
         END AS yuzde,
         DENSE_RANK() OVER (ORDER BY ciro DESC, kategori ASC) AS sira
  FROM ciro_tum
)
SELECT kategori,
       ROUND(ciro, 2) AS ciro,
       yuzde AS yüzde,
       sira AS sıra
FROM sonuc
ORDER BY sira, kategori ASC;
