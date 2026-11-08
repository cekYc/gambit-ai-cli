WITH sehirler AS (
    SELECT DISTINCT sehir FROM musteriler
),
musteri_sayilari AS (
    SELECT m.sehir, COUNT(DISTINCT m.id) AS musteri_sayisi
    FROM musteriler m
    JOIN siparisler s ON s.musteri_id = m.id
    GROUP BY m.sehir
),
ciro_toplamlari AS (
    SELECT m.sehir, SUM(sk.adet * sk.birim_fiyat) AS toplam_ciro
    FROM musteriler m
    JOIN siparisler s ON s.musteri_id = m.id
    JOIN siparis_kalemleri sk ON sk.siparis_id = s.id
    GROUP BY m.sehir
)
SELECT s.sehir,
       COALESCE(ms.musteri_sayisi, 0) AS musteri_sayisi,
       ROUND(COALESCE(ct.toplam_ciro, 0), 2) AS toplam_ciro
FROM sehirler s
LEFT JOIN musteri_sayilari ms ON ms.sehir = s.sehir
LEFT JOIN ciro_toplamlari ct ON ct.sehir = s.sehir
ORDER BY toplam_ciro DESC, s.sehir ASC;