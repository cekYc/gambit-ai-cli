WITH sehirler AS (
    SELECT DISTINCT sehir FROM musteriler
),
siparis_ciro AS (
    SELECT 
        m.sehir,
        COUNT(DISTINCT s.musteri_id) AS musteri_sayisi,
        COALESCE(ROUND(SUM(sk.adet * sk.birim_fiyat), 2), 0) AS toplam_ciro
    FROM musteriler m
    LEFT JOIN siparisler s ON m.id = s.musteri_id
    LEFT JOIN siparis_kalemleri sk ON s.id = sk.siparis_id
    GROUP BY m.sehir
)
SELECT 
    s.sehir,
    COALESCE(sc.musteri_sayisi, 0) AS musteri_sayisi,
    COALESCE(sc.toplam_ciro, 0) AS toplam_ciro
FROM sehirler s
LEFT JOIN siparis_ciro sc ON s.sehir = sc.sehir
ORDER BY toplam_ciro DESC, s.sehir ASC;