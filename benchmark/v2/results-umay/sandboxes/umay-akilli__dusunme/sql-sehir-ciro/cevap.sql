WITH
sehirler AS (
    SELECT DISTINCT sehir FROM musteriler
),
siparis_detay AS (
    SELECT 
        m.sehir,
        m.id AS musteri_id,
        s.id AS siparis_id,
        sk.adet,
        sk.birim_fiyat
    FROM musteriler m
    LEFT JOIN siparisler s ON m.id = s.musteri_id
    LEFT JOIN siparis_kalemleri sk ON s.id = sk.siparis_id
)
SELECT 
    s.sehir,
    COUNT(DISTINCT CASE WHEN sd.siparis_id IS NOT NULL THEN sd.musteri_id END) AS musteri_sayisi,
    ROUND(COALESCE(SUM(CASE WHEN sd.siparis_id IS NOT NULL THEN sd.adet * sd.birim_fiyat END), 0), 2) AS ciro
FROM sehirler s
LEFT JOIN siparis_detay sd ON s.sehir = sd.sehir
GROUP BY s.sehir
ORDER BY ciro DESC, s.sehir ASC;