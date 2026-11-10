SELECT
    M.sehir,
    COUNT(DISTINCT CASE WHEN S.id IS NOT NULL THEN M.id END) AS siparis_verenin_musteri_sayisi,
    ROUND(COALESCE(SUM(SK.adet * SK.birim_fiyat), 0), 2) AS toplam_ciro
FROM
    musteriler M
LEFT JOIN
    siparisler S ON M.id = S.musteri_id
LEFT JOIN
    siparis_kalemleri SK ON S.id = SK.siparis_id
GROUP BY
    M.sehir
ORDER BY
    toplam_ciro DESC, M.sehir ASC;