WITH AllCategories AS (
    SELECT DISTINCT kategori FROM urunler
),
CategorySales AS (
    SELECT u.kategori,
           SUM(sk.adet * sk.birim_fiyat) AS ciro_2025
    FROM urunler u
    JOIN siparis_kalemleri sk ON u.id = sk.urun_id
    JOIN siparisler s ON sk.siparis_id = s.id
    WHERE s.tarih LIKE '2025%'
    GROUP BY u.kategori
),
RankedSales AS (
    SELECT ac.kategori,
           COALESCE(cs.ciro_2025, 0.00) AS ciro,
           SUM(COALESCE(cs.ciro_2025, 0.00)) OVER () AS total_ciro_2025,
           DENSE_RANK() OVER (ORDER BY COALESCE(cs.ciro_2025, 0.00) DESC, ac.kategori ASC) as sira
    FROM AllCategories ac
    LEFT JOIN CategorySales cs ON ac.kategori = cs.kategori
)
SELECT 
    kategori,
    ROUND(ciro, 2) AS ciro,
    ROUND((ciro * 100.0 / NULLIF(total_ciro_2025, 0)), 1) AS yüzde,
    sira
FROM RankedSales
ORDER BY sira, kategori;