WITH customer_months AS (
    SELECT 
        m.ad as musteri_adi,
        strftime('%Y-%m', s.tarih) as ay,
        (CAST(strftime('%Y', s.tarih) AS INTEGER) * 12 + CAST(strftime('%m', s.tarih) AS INTEGER)) as ay_num
    FROM siparisler s
    JOIN musteriler m ON s.musteri_id = m.id
    GROUP BY m.ad, strftime('%Y-%m', s.tarih)
),
sequenced AS (
    SELECT 
        musteri_adi,
        ay,
        ay_num,
        ROW_NUMBER() OVER (PARTITION BY musteri_adi ORDER BY ay_num) as rn
    FROM customer_months
),
grouped AS (
    SELECT 
        musteri_adi,
        ay,
        ay_num,
        (ay_num - rn) as grp
    FROM sequenced
),
sequences AS (
    SELECT 
        musteri_adi,
        MIN(ay) as baslangic_ay,
        COUNT(*) as uzunluk
    FROM grouped
    GROUP BY musteri_adi, grp
),
ranked AS (
    SELECT 
        musteri_adi,
        uzunluk,
        baslangic_ay,
        ROW_NUMBER() OVER (PARTITION BY musteri_adi ORDER BY uzunluk DESC, baslangic_ay ASC) as rn
    FROM sequences
    WHERE uzunluk >= 3
)
SELECT musteri_adi, uzunluk, baslangic_ay
FROM ranked
WHERE rn = 1
ORDER BY uzunluk DESC, musteri_adi ASC;