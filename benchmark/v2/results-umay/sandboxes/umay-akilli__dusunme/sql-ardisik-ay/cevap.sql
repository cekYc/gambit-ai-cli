WITH customer_months AS (
    SELECT 
        m.ad AS musteri_adi,
        strftime('%Y-%m', s.tarih) AS ay,
        (CAST(strftime('%Y', s.tarih) AS INTEGER) * 12 + CAST(strftime('%m', s.tarih) AS INTEGER)) AS ay_num
    FROM siparisler s
    JOIN musteriler m ON s.musteri_id = m.id
    GROUP BY m.ad, strftime('%Y-%m', s.tarih)
),
sequences AS (
    SELECT 
        musteri_adi,
        ay,
        ay_num,
        ROW_NUMBER() OVER (PARTITION BY musteri_adi ORDER BY ay_num) AS rn,
        ay_num - ROW_NUMBER() OVER (PARTITION BY musteri_adi ORDER BY ay_num) AS grp
    FROM customer_months
),
grouped AS (
    SELECT 
        musteri_adi,
        MIN(ay) AS baslangic_ay,
        COUNT(*) AS seri_uzunlugu,
        MIN(ay_num) AS baslangic_ay_num
    FROM sequences
    GROUP BY musteri_adi, grp
),
ranked AS (
    SELECT 
        musteri_adi,
        seri_uzunlugu,
        baslangic_ay,
        baslangic_ay_num,
        ROW_NUMBER() OVER (
            PARTITION BY musteri_adi 
            ORDER BY seri_uzunlugu DESC, baslangic_ay_num ASC
        ) AS rn
    FROM grouped
    WHERE seri_uzunlugu >= 3
)
SELECT 
    musteri_adi,
    seri_uzunlugu,
    baslangic_ay
FROM ranked
WHERE rn = 1
ORDER BY seri_uzunlugu DESC, musteri_adi ASC;