WITH sehirler AS (
    SELECT DISTINCT sehir FROM musteriler
),
siparis_ciro AS (
    SELECT 
        m.sehir,
        COUNT(DISTINCT m.id) AS musteri_sayisi,
        ROUND(SUM(sk.adet * sk.birim_fiyat), 2) AS toplam_ciro
    FROM musteriler m
    JOIN siparisler s ON s.musteri_id = m.id
    JOIN siparis_kalemleri sk ON sk.siparis_id = s.id
    GROUP BY m.sehir
)
SELECT 
    sehirler.sehir,
    COALESCE(siparis_ciro.musteri_sayisi, 0) AS musteri_sayisi,
    COALESCE(siparis_ciro.toplam_ciro, 0) AS toplam_ciro
FROM sehirler
LEFT JOIN siparis_ciro ON siparis_ciro.sehir = sehirler.sehir
ORDER BY toplam_ciro DESC, sehirler.sehir ASC;