WITH ciro_2025 AS (
    SELECT
        u.kategori,
        COALESCE(SUM(sk.adet * sk.birim_fiyat), 0) AS ciro
    FROM urunler u
    LEFT JOIN siparis_kalemleri sk
        ON sk.urun_id = u.id
        AND sk.siparis_id IN (
            SELECT id FROM siparisler WHERE tarih LIKE '2025-%'
        )
    GROUP BY u.kategori
),
toplam_ciro AS (
    SELECT SUM(ciro) AS toplam FROM ciro_2025
)
SELECT
    c.kategori,
    ROUND(c.ciro, 2) AS ciro,
    CASE WHEN t.toplam = 0 THEN 0.0 ELSE ROUND(100.0 * c.ciro / t.toplam, 1) END AS yuzde,
    DENSE_RANK() OVER (ORDER BY c.ciro DESC) AS sira
FROM ciro_2025 c
CROSS JOIN toplam_ciro t
ORDER BY sira ASC, c.kategori ASC;