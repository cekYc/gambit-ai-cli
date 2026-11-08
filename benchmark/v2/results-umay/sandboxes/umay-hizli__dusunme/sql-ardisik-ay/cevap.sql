WITH aylar AS (
  SELECT DISTINCT
    s.musteri_id,
    strftime('%Y', s.tarih) || '-' || strftime('%m', s.tarih) AS ay,
    CAST(strftime('%Y', s.tarih) AS INTEGER) * 12 + CAST(strftime('%m', s.tarih) AS INTEGER) AS ay_deger
  FROM siparisler s
),
gruplar AS (
  SELECT
    a.*,
    ROW_NUMBER() OVER (PARTITION BY musteri_id ORDER BY ay_deger) AS rn,
    ay_deger - ROW_NUMBER() OVER (PARTITION BY musteri_id ORDER BY ay_deger) AS grp
  FROM aylar a
),
seriler AS (
  SELECT
    musteri_id,
    COUNT(*) AS uzunluk,
    MIN(ay) AS baslangic_ay,
    MIN(ay_deger) AS baslangic_deger
  FROM gruplar
  GROUP BY musteri_id, grp
),
en_uzun_seri AS (
  SELECT
    s.musteri_id,
    s.uzunluk,
    s.baslangic_ay,
    ROW_NUMBER() OVER (
      PARTITION BY s.musteri_id
      ORDER BY s.uzunluk DESC, s.baslangic_deger
    ) AS rn
  FROM seriler s
)
SELECT
  m.ad AS mustteri_adi,
  e.uzunluk AS seri_uzunlugu,
  e.baslangic_ay AS baslangic_ay
FROM en_uzun_seri e
JOIN musteriler m ON m.id = e.musteri_id
WHERE e.rn = 1
  AND e.uzunluk >= 3
ORDER BY e.uzunluk DESC, m.ad ASC;