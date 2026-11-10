WITH aylar AS (
  SELECT DISTINCT m.id AS musteri_id, m.ad, substr(s.tarih, 1, 7) AS ay
  FROM musteriler m
  JOIN siparisler s ON s.musteri_id = m.id
),
tekil AS (
  SELECT DISTINCT musteri_id, ad, ay FROM aylar
),
grup AS (
  SELECT *, date(ay || '-01', '-' || (strftime('%m', ay) - 1) || ' months') AS gkey
  FROM tekil
),
seriler AS (
  SELECT musteri_id, ad, COUNT(*) AS seri_uzunlugu, MIN(ay) AS baslangic_ay
  FROM grup
  GROUP BY musteri_id, ad, gkey
),
sirala AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY musteri_id ORDER BY seri_uzunlugu DESC, baslangic_ay ASC) AS rn
  FROM seriler
)
SELECT ad, seri_uzunlugu, baslangic_ay
FROM sirala
WHERE rn = 1 AND seri_uzunlugu >= 3
ORDER BY seri_uzunlugu DESC, ad;
