WITH MusteriAylar AS (
    SELECT
        m.ad AS musteri_adi,
        strftime('%Y-%m', s.tarih) AS siparis_ay
    FROM musteriler m
    JOIN siparisler s ON m.id = s.musteri_id
),
AySiralama AS (
    SELECT
        musteri_adi,
        siparis_ay,
        -- Ayın sayısal temsilini (YYYYMM) almak için
        CAST(strftime('%Y', siparis_ay) AS INTEGER) * 100 + CAST(strftime('%m', siparis_ay) AS INTEGER) AS ay_sayi,
        -- Her müşteri için ayları sırala
        ROW_NUMBER() OVER (PARTITION BY musteri_adi ORDER BY siparis_ay ASC) as rn
    FROM MusteriAylar
    GROUP BY musteri_adi, siparis_ay
),
ArdIsikSeri AS (
    SELECT
        musteri_adi,
        ay_sayi,
        -- Bir önceki ayın sayısal değerini bul
        LAG(ay_sayi, 1, ay_sayi - 1) OVER (PARTITION BY musteri_adi ORDER BY ay_sayi) AS onceki_ay_sayi,
        -- Ardışık devam edip etmediğini kontrol et (fark 1 olmalı)
        CASE WHEN ay_sayi - LAG(ay_sayi, 1, ay_sayi - 1) OVER (PARTITION BY musteri_adi ORDER BY ay_sayi) = 1 THEN 1 ELSE 0 END AS ard_disik_devam
    FROM AySiralama
),
SeriGrup AS (
    SELECT
        musteri_adi,
        ay_sayi,
        -- Serinin başlangıcını bul: ardışık devam etmeyen ilk ay veya ilk ay
        SUM(CASE WHEN ard_disik_devam = 0 THEN 1 ELSE 0 END) OVER (PARTITION BY musteri_adi ORDER BY ay_sayi) AS seri_grup_id,
        -- Seri uzunluğunu hesapla
        COUNT(ay_sayi) OVER (PARTITION BY musteri_adi, SUM(CASE WHEN ard_disik_devam = 0 THEN 1 ELSE 0 END) OVER (PARTITION BY musteri_adi ORDER BY ay_sayi)) AS seri_uzunlugu,
        -- Serinin başlangıç ayını bul (grup içindeki ilk ay)
        MIN(ay_sayi) OVER (PARTITION BY musteri_adi, SUM(CASE WHEN ard_disik_devam = 0 THEN 1 ELSE 0 END) OVER (PARTITION BY musteri_adi ORDER BY ay_sayi)) AS seri_baslangic_ay_sayi
    FROM ArdIsikSeri
)
SELECT
    musteri_adi,
    seri_uzunlugu AS seri_uzunlugu_ay,
    strftime('%Y-%m', seri_baslangic_ay_sayi / 100, '%Y-%m') AS baslangic_ayi
FROM SeriGrup
WHERE
    seri_uzunlugu >= 3
ORDER BY
    seri_uzunlugu DESC,
    musteri_adi ASC;