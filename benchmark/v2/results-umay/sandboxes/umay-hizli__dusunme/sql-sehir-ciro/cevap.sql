WITH tum_sehirler AS (
    SELECT DISTINCT sehir
    FROM musteriler
),
sehir_musteri_sayisi AS (
    SELECT m.sehir, COUNT(DISTINCT m.id) AS musteri_sayisi
    FROM musteriler m
    JOIN siparisler s ON m.id = s.musteri_id
    GROUP BY m.sehir
),
sehir_ciro AS (
    SELECT m.sehir, ROUND(SUM(sk.adet * sk.birim_fiyat), 2) AS toplam_ciro
    FROM musteriler m
    JOIN siparisler s ON m.id = s.musteri_id
    JOIN siparis_kalemleri sk ON s.id = sk.siparis_id
    GROUP BY m.sehir
)
SELECT 
    ts.sehir,
    COALESCE(sms.musteri_sayisi, 0) AS musteri_sayisi,
    COALESCE(sc.toplam_ciro, 0) AS toplam_ciro
FROM tum_sehirler ts
LEFT JOIN sehir_musteri_sayisi sms ON ts.sehir = sms.sehir
LEFT JOIN sehir_ciro sc ON ts.sehir = sc.sehir
ORDER BY toplam_ciro DESC, ts.sehir ASC;