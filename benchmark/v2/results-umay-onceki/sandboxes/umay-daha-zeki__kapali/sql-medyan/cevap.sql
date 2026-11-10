
WITH SiparisTutarlari AS (
    SELECT 
        s.id AS siparis_id, 
        m.sehir, 
        SUM(skl.adet * skl.birim_fiyat) AS toplam_tutar 
    FROM siparisler s 
    JOIN musteriler m ON s.musteri_id = m.id 
    JOIN siparis_kalemleri skl ON s.id = skl.siparis_id 
    GROUP BY s.id, m.sehir
),

SehirOzellikleri AS (
    SELECT 
        sehir, 
        COUNT(siparis_id) AS siparis_sayisi, 
        GROUP_CONCAT(total_tutar ORDER BY total_tutar ASC) AS tutarlar_listesi 
    FROM SiparisTutarlari 
    GROUP BY sehir 
    HAVING COUNT(siparis_id) >= 2 
)

SELECT 
    sehir, 
    siparis_sayisi, 
    CASE 
        WHEN LENGTH(tutarlar_listesi) % 2 != 0 THEN CAST(SUBSTR(tutarlar_listesi, (LENGTH(tutarlar_listesi) + 1) / 2, 1000) AS REAL)
        ELSE (CAST(SUBSTR(tutarlar_listesi, LENGTH(tutarlar_listesi) / 2 + 1, 1000) AS REAL) + CAST(SUBSTR(tutarlar_listesi, LENGTH(tutarlar_listesi) / 2, 1000) AS REAL)) / 2.0
    END AS medyan_tutar
FROM 
    SehirOzellikleri
ORDER BY 
    medyan_tutar DESC, 
    sehir ASC;
