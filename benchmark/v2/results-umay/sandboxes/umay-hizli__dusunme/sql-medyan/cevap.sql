WITH siparis_tutarlari AS (
  SELECT s.id AS siparis_id,
         m.sehir,
         SUM(sk.adet * sk.birim_fiyat) AS tutar
  FROM siparisler s
  JOIN musteriler m ON s.musteri_id = m.id
  JOIN siparis_kalemleri sk ON sk.siparis_id = s.id
  GROUP BY s.id, m.sehir
),
siralanmis AS (
  SELECT sehir,
         tutar,
         ROW_NUMBER() OVER (PARTITION BY sehir ORDER BY tutar) AS rn,
         COUNT(*) OVER (PARTITION BY sehir) AS cnt
  FROM siparis_tutarlari
),
medyanlar AS (
  SELECT sehir,
         COUNT(*) AS siparis_sayisi,
         ROUND(
           (MAX(CASE WHEN rn = (cnt + 1) / 2 THEN tutar END) +
            MAX(CASE WHEN rn = (cnt + 2) / 2 THEN tutar END)) / 2.0,
           2
         ) AS medyan
  FROM siralanmis
  GROUP BY sehir
  HAVING COUNT(*) >= 2
)
SELECT sehir,
       siparis_sayisi,
       medyan
FROM medyanlar
ORDER BY medyan DESC, sehir ASC;