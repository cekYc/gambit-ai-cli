WITH all_categories AS (
    SELECT DISTINCT kategori FROM urunler
),
category_sales AS (
    SELECT u.kategori, SUM(sl.adet * sl.birim_fiyat) AS ciro
    FROM urunler u
    JOIN siparis_kalemleri sl ON sl.urun_id = u.id
    JOIN siparisler s ON s.id = sl.siparis_id
    WHERE s.tarih LIKE '2025%'
    GROUP BY u.kategori
),
total_revenue AS (
    SELECT COALESCE(SUM(sl.adet * sl.birim_fiyat), 0) AS toplam
    FROM siparis_kalemleri sl
    JOIN siparisler s ON s.id = sl.siparis_id
    WHERE s.tarih LIKE '2025%'
)
SELECT
    ac.kategori,
    ROUND(COALESCE(cs.ciro, 0), 2) AS ciro,
    ROUND(CASE WHEN tr.toplam = 0 THEN 0.0 ELSE (COALESCE(cs.ciro, 0) / tr.toplam) * 100 END, 1) AS yüzde,
    DENSE_RANK() OVER (ORDER BY COALESCE(cs.ciro, 0) DESC, ac.kategori ASC) AS sıra
FROM all_categories ac
LEFT JOIN category_sales cs ON ac.kategori = cs.kategori
CROSS JOIN total_revenue tr
ORDER BY sıra, ac.kategori;