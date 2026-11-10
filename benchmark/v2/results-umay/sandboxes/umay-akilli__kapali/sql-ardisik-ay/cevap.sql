WITH 
-- Her müşteri için benzersiz aylar ve sıralı ay numarası
aylar AS (
    SELECT 
        m.id AS musteri_id,
        m.ad AS musteri_ad,
        strftime('%Y-%m', s.tarih) AS ay,
        (CAST(strftime('%Y', s.tarih) AS INTEGER) * 12 + CAST(strftime('%m', s.tarih) AS INTEGER)) AS ay_no
    FROM siparisler s
    JOIN musteriler m ON s.musteri_id = m.id
    GROUP BY m.id, strftime('%Y-%m', s.tarih)
),
-- Gaps-and-islands: ardışık aylar için (ay_no - row_number) sabit olur
gruplar AS (
    SELECT 
        musteri_id,
        musteri_ad,
        ay,
        ay_no,
        ROW_NUMBER() OVER (PARTITION BY musteri_id ORDER BY ay_no) AS rn,
        ay_no - ROW_NUMBER() OVER (PARTITION BY musteri_id ORDER BY ay_no) AS grp
    FROM aylar
),
-- Her grup için seri uzunluğu ve başlangıç ayı
seriler AS (
    SELECT 
        musteri_id,
        musteri_ad,
        MIN(ay) AS baslangic_ay,
        COUNT(*) AS seri_uzunlugu
    FROM gruplar
    GROUP BY musteri_id, grp
),
-- Her müşterinin en uzun serisi (eşitlikte en erken başlayan)
encok AS (
    SELECT 
        musteri_id,
        musteri_ad,
        seri_uzunlugu,
        baslangic_ay,
        ROW_NUMBER() OVER (PARTITION BY musteri_id ORDER BY seri_uzunlugu DESC, baslangic_ay ASC) AS rn
    FROM seriler
    WHERE seri_uzunlugu >= 3
)
SELECT 
    musteri_ad,
    seri_uzunlugu,
    baslangic_ay
FROM encok
WHERE rn = 1
ORDER BY seri_uzunlugu DESC, musteri_ad ASC;