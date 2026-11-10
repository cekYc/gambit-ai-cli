WITH sehirler AS (
    SELECT DISTINCT sehir FROM musteriler
),
musteri_siparis AS (
    SELECT m.sehir, m.id AS musteri_id
    FROM musteriler m
    JOIN siparisler s ON s.musteri_id = m.id
),
musteri_sayilari AS (
    SELECT sehir, COUNT(DISTINCT musteri_id) AS musteri_sayisi
    FROM musteri_siparis
    GROUP BY sehir
),
ciro_hesap AS (
    SELECT m.sehir, ROUND(SUM(sk.adet * sk.birim_fiyat), 2) AS toplam_ciro
    FROM musteriler m
    JOIN siparisler s ON s.musteri_id = m.id
    JOIN siparis_kalemleri sk ON sk.siparis_id = s.id
    GROUP BY m.sehir
)
SELECT 
    sl.sehir,
    COALESCE(ms.musteri_sayisi, 0) AS musteri_sayisi,
    COALESCE(ch.toplam_ciro, 0) AS toplam_ciro
FROM sehirler sl
LEFT JOIN musteri_sayilari ms ON ms.sehir = sl.sehir
LEFT JOIN ciro_hesap ch ON ch.sehir = sl.sehir
ORDER BY toplam_ciro DESC, sl.sehir ASC;