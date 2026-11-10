WITH sehirler AS (
    SELECT DISTINCT sehir FROM musteriler
)
SELECT
    s.sehir AS sehir_adi,
    COUNT(DISTINCT o.musteri_id) AS musteri_sayisi,
    ROUND(COALESCE(SUM(sk.adet * sk.birim_fiyat), 0), 2) AS toplam_ciro
FROM sehirler s
LEFT JOIN musteriler m ON m.sehir = s.sehir
LEFT JOIN siparisler o ON o.musteri_id = m.id
LEFT JOIN siparis_kalemleri sk ON sk.siparis_id = o.id
GROUP BY s.sehir
ORDER BY toplam_ciro DESC, s.sehir ASC;