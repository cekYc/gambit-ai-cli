WITH TumKategoriler AS (SELECT DISTINCT kategori FROM urunler),
KategoriCiro AS (
    SELECT 
        T.kategori,
        COALESCE(SUM(CASE WHEN S.tarih LIKE '2025-%' THEN SK.adet * SK.birim_fiyat ELSE 0 END), 0.0) AS ciro
    FROM TumKategoriler AS T
    LEFT JOIN urunler AS U ON T.kategori = U.kategori
    LEFT JOIN siparis_kalemleri AS SK ON U.id = SK.urun_id
    LEFT JOIN siparisler AS S ON SK.siparis_id = S.id
    GROUP BY T.kategori
)
SELECT
    kategori,
    ROUND(ciro, 2) AS ciro,
    ROUND(CIRO_TOPLAM * 100.0 / COALESCE(SUM(ciro), 0.0), 1) AS yuzde,
    DENSE_RANK() OVER (ORDER BY ciro DESC, kategori ASC) AS sira
FROM KategoriCiro
CROSS JOIN (SELECT COALESCE(SUM(ciro), 0.0) AS CIRO_TOPLAM FROM KategoriCiro)
ORDER BY sira ASC, kategori ASC;