WITH 
-- Müşteri bazında sipariş verdiği takvim aylarını çıkar (YYYY-MM)
musteri_aylar AS (
    SELECT 
        m.id AS musteri_id,
        m.ad AS musteri_ad,
        strftime('%Y-%m', REPLACE(s.tarih, '/', '-')) AS siparis_ay
    FROM siparisler s
    JOIN musteriler m ON s.musteri_id = m.id
    GROUP BY m.id, siparis_ay
),
-- Her ayı sıralı bir numaraya çevir (yıl*12 + ay) ve önceki ayla farkı al
ay_sira AS (
    SELECT 
        musteri_id,
        musteri_ad,
        siparis_ay,
        (CAST(substr(siparis_ay, 1, 4) AS INTEGER) * 12 + CAST(substr(siparis_ay, 6, 2) AS INTEGER)) AS ay_no,
        LAG((CAST(substr(siparis_ay, 1, 4) AS INTEGER) * 12 + CAST(substr(siparis_ay, 6, 2) AS INTEGER))) OVER (PARTITION BY musteri_id ORDER BY siparis_ay) AS onceki_ay_no
    FROM musteri_aylar
),
-- Ardışık olmayan geçişlerde gruba başlangıç işareti koy
grup_baslangic AS (
    SELECT 
        musteri_id,
        musteri_ad,
        siparis_ay,
        ay_no,
        CASE WHEN ay_no - COALESCE(onceki_ay_no, ay_no - 2) > 1 THEN 1 ELSE 0 END AS yeni_grup
    FROM ay_sira
),
-- Kümülatif toplamla her ardışık seriye bir grup numarası ver
gruplar AS (
    SELECT 
        musteri_id,
        musteri_ad,
        siparis_ay,
        ay_no,
        SUM(yeni_grup) OVER (PARTITION BY musteri_id ORDER BY siparis_ay ROWS UNBOUNDED PRECEDING) AS grup_no
    FROM grup_baslangic
),
-- Her grup için uzunluk ve başlangıç ayı hesapla
grup_ozet AS (
    SELECT 
        musteri_id,
        musteri_ad,
        MIN(siparis_ay) AS baslangic_ay,
        COUNT(*) AS seri_uzunlugu
    FROM gruplar
    GROUP BY musteri_id, grup_no
),
-- Müşteri başına en uzun seri (eşitlikte en erken başlangıç)
musteri_en_uzun AS (
    SELECT 
        musteri_id,
        musteri_ad,
        seri_uzunlugu,
        baslangic_ay,
        ROW_NUMBER() OVER (PARTITION BY musteri_id ORDER BY seri_uzunlugu DESC, baslangic_ay ASC) AS rn
    FROM grup_ozet
)
SELECT 
    musteri_ad,
    seri_uzunlugu,
    baslangic_ay
FROM musteri_en_uzun
WHERE rn = 1 AND seri_uzunlugu >= 3
ORDER BY seri_uzunlugu DESC, musteri_ad ASC;