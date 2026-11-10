WITH aylar AS (
  SELECT DISTINCT
    m.id AS musteri_id,
    m.ad AS musteri_ad,
    strftime('%Y-%m', s.tarih) AS ay_ym
  FROM musteriler m
  JOIN siparisler s ON s.musteri_id = m.id
),
ay_no AS (
  SELECT
    musteri_id,
    musteri_ad,
    ay_ym,
    (CAST(substr(ay_ym, 1, 4) AS INTEGER) * 12 + CAST(substr(ay_ym, 6, 2) AS INTEGER)) AS ay_sayi
  FROM aylar
),
gruplar AS (
  SELECT
    musteri_id,
    musteri_ad,
    ay_ym,
    ay_sayi,
    (ay_sayi - ROW_NUMBER() OVER (PARTITION BY musteri_id ORDER BY ay_sayi)) AS grp
  FROM ay_no
),
seriler AS (
  SELECT
    musteri_id,
    musteri_ad,
    MIN(ay_ym) AS baslangic_ay,
    COUNT(*) AS uzunluk
  FROM gruplar
  GROUP BY musteri_id, musteri_ad, grp
),
en_uzun AS (
  SELECT
    musteri_id,
    musteri_ad,
    baslangic_ay,
    uzunluk,
    ROW_NUMBER() OVER (PARTITION BY musteri_id ORDER BY uzunluk DESC, baslangic_ay ASC) AS rn
  FROM seriler
)
SELECT
  musteri_ad AS musteri_adi,
  uzunluk AS seri_uzunlugu_ay,
  baslangic_ay AS seri_baslangic_ay
FROM en_uzun
WHERE rn = 1 AND uzunluk >= 3
ORDER BY uzunluk DESC, musteri_ad ASC;