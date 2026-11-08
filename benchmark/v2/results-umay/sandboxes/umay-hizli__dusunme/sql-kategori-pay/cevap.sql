-- 2025 yili bazinda kategori cirolari, yuzde payi ve DENSE_RANK sirasi
-- TUM kategoriler listelenir; 2025'de satis olmayanlar 0 ciro ve 0.0 pay ile.
WITH sales_2025 AS (
    SELECT
        u.kategori AS kategori,
        SUM(sk.adet * sk.birim_fiyat) AS ciro
    FROM urunler u
    JOIN siparis_kalemleri sk ON sk.urun_id = u.id
    JOIN siparisler s ON s.id = sk.siparis_id
    WHERE substr(s.tarih, 1, 4) = '2025'
    GROUP BY u.kategori
),
kategoriler AS (
    SELECT DISTINCT kategori FROM urunler
),
agg AS (
    SELECT
        k.kategori,
        COALESCE(s.ciro, 0.0) AS ciro
    FROM kategoriler k
    LEFT JOIN sales_2025 s ON s.kategori = k.kategori
),
toplam AS (
    SELECT SUM(ciro) AS toplam_ciro FROM agg
)
SELECT
    kategori,
    round(ciro, 2) AS ciro,
    CASE
        WHEN t.toplam_ciro = 0 THEN 0.0
        ELSE round(ciro * 100.0 / t.toplam_ciro, 1)
    END AS yuzde,
    DENSE_RANK() OVER (ORDER BY ciro DESC) AS sira
FROM agg, toplam t
ORDER BY sira ASC, kategori ASC;