WITH MusteriAylari AS (
    SELECT 
        m.ad AS musteri_adi,
        strftime('%Y-%m', s.tarih) AS siparis_ay,
        CAST(strftime('%Y', s.tarih) AS INTEGER) * 100 + CAST(strftime('%m', s.tarih) AS INTEGER) AS ay_tamsayi
    FROM musteriler m
    JOIN siparisler s ON m.id = s.musteri_id
),
SeriGrup AS (
    -- Ardışık serileri aynı 'gruba' yerleştirir: (Ay Tamsayısı - Sıra Numarası) sabittir.
    SELECT 
        musteri_adi,
        siparis_ay,
        ay_tamsayi,
        ROW_NUMBER() OVER (PARTITION BY musteri_adi ORDER BY ay_tamsayi) AS rn,
        ay_tamsayi - ROW_NUMBER() OVER (PARTITION BY musteri_adi ORDER BY ay_tamsayi) AS seri_grubu
    FROM MusteriAylari
)
-- Sonuçları filtrele ve sırala
SELECT 
    musteri_adi, 
    COUNT(siparis_ay) AS seri_uzunlugu, 
    MIN(siparis_ay) AS baslangic_ay
FROM SeriGrup
WHERE seri_grubu IN (
    -- En uzun seriyi bulmak için maksimum seri uzunluğunu buluruz
    SELECT 
        MAX(COUNT(siparis_ay)) 
    FROM (
        SELECT COUNT(siparis_ay) AS seri_uzunlugu 
        FROM SeriGrup
        GROUP BY seri_grubu
    )
) AND COUNT(siparis_ay) >= 3
GROUP BY seri_grubu, musteri_adi
ORDER BY 
    seri_uzunlugu DESC, 
    musteri_adi ASC;