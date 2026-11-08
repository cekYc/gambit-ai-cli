WITH aylar AS (
    SELECT
        s.musteri_id,
        strftime('%Y-%m', s.tarih) AS ay
    FROM siparisler s
    GROUP BY s.musteri_id, ay
),
sayilar AS (
    SELECT
        musteri_id,
        ay,
        CAST(substr(ay, 1, 4) AS INTEGER) * 12 + CAST(substr(ay, 6, 2) AS INTEGER) AS ay_no
    FROM aylar
),
gruplar AS (
    SELECT
        musteri_id,
        ay_no,
        ay_no - ROW_NUMBER() OVER (PARTITION BY musteri_id ORDER BY ay_no) AS grp
    FROM sayilar
),
seriler AS (
    SELECT
        musteri_id,
        MIN(ay_no) AS baslangic_ay_no,
        COUNT(*) AS uzunluk
    FROM gruplar
    GROUP BY musteri_id, grp
),
max_seri AS (
    SELECT
        musteri_id,
        MAX(uzunluk) AS max_uzunluk
    FROM seriler
    GROUP BY musteri_id
),
secim AS (
    SELECT
        s.musteri_id,
        s.uzunluk,
        s.baslangic_ay_no,
        ROW_NUMBER() OVER (
            PARTITION BY s.musteri_id
            ORDER BY s.uzunluk DESC, s.baslangic_ay_no ASC
        ) AS rn
    FROM seriler s
    JOIN max_seri m ON m.musteri_id = s.musteri_id AND m.max_uzunluk = s.uzunluk
)
SELECT
    m.ad AS musteri_adi,
    s.uzunluk AS seri_uzunlugu,
    printf('%04d-%02d', s.baslangic_ay_no / 12, s.baslangic_ay_no % 12 + 1) AS baslangic_ayi
FROM secim s
JOIN musteriler m ON m.id = s.musteri_id
WHERE s.rn = 1
  AND s.uzunluk >= 3
ORDER BY s.uzunluk DESC, m.ad ASC;