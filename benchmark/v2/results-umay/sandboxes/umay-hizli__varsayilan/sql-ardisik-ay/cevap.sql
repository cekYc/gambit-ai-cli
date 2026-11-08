WITH aylar AS (
  SELECT DISTINCT musteri_id, substr(tarih, 1, 7) AS ay
  FROM siparisler
),
sira AS (
  SELECT musteri_id, ay,
         ROW_NUMBER() OVER (PARTITION BY musteri_id ORDER BY ay) AS rn,
         CAST(substr(ay, 1, 4) AS INTEGER) * 12 + CAST(substr(ay, 6, 2) AS INTEGER) AS ay_idx
  FROM aylar
),
gruplar AS (
  SELECT musteri_id, ay,
         ay_idx - rn AS grp
  FROM sira
),
seriler AS (
  SELECT musteri_id,
         COUNT(*) AS uzunluk,
         MIN(ay) AS baslangic_ay
  FROM gruplar
  GROUP BY musteri_id, grp
),
en_uzun AS (
  SELECT musteri_id, uzunluk, baslangic_ay,
         ROW_NUMBER() OVER (
           PARTITION BY musteri_id
           ORDER BY uzunluk DESC, baslangic_ay ASC
         ) AS rnk
  FROM seriler
)
SELECT m.ad AS musteri_adi,
       e.uzunluk AS seri_uzunlugu,
       e.baslangic_ay AS baslangic_ay
FROM en_uzun e
JOIN musteriler m ON m.id = e.musteri_id
WHERE e.rnk = 1 AND e.uzunluk >= 3
ORDER BY e.uzunluk DESC, m.ad ASC;