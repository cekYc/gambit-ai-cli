SELECT
    m.sehir,
    COUNT(DISTINCT s.musteri_id) AS musteri_sayisi,
    ROUND(SUM(sk.adet * sk.birim_fiyat), 2) AS toplam_ciro
FROM
    musteriler m
LEFT JOIN
    siparisler s ON m.id = s.musteri_id
LEFT JOIN
    siparis_kalemleri sk ON s.id = sk.siparis_id
GROUP BY
    m.sehir
ORDER BY
    toplam_ciro DESC,
    m.sehir ASC;