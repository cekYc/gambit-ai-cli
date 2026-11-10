
WITH TumKategoriler AS (
    SELECT DISTINCT kategori FROM urunler
),
KategoriCirosu AS (
    SELECT
        u.kategori,
        COALESCE(SUM(sk.adet * sk.birim_fiyat), 0.0) AS ciro
    FROM urunler u
    LEFT JOIN siparis_kalemleri sk ON u.id = sk.urun_id
    JOIN siparisler s ON sk.siparis_id = s.id
    WHERE s.tarih LIKE '2025-%' AND u.kategori IN (SELECT kategori FROM TumKategoriler)
    GROUP BY u.kategori
)
SELECT
    tk.kategori,
    ROUND(kc.ciro, 2) AS ciro,
    ROUND(kc.ciro * 100.0 / (SELECT SUM(kc_total.ciro) FROM KategoriCirosu kc_total), 1) AS yuzde,
    DENSE_RANK() OVER (ORDER BY kc.ciro DESC, tk.kategori ASC) AS sira
FROM TumKategoriler tk
LEFT JOIN KategoriCirosu kc ON tk.kategori = kc.kategori
ORDER BY 
    kc.ciro DESC, 
    tk.kategori ASC;
