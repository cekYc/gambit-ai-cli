WITH CategorySales AS (
    SELECT
        T1.kategori,
        COALESCE(SUM(T3.adet * T3.birim_fiyat), 0.0) AS ciro_2025
    FROM
        urunler AS T1
    LEFT JOIN
        siparis_kalemleri AS T3 ON T1.id = T3.urun_id
    LEFT JOIN
        siparisler AS T2 ON T3.siparis_id = T2.id AND T2.tarih LIKE '2025%'
    GROUP BY
        T1.kategori
),
RankedSales AS (
    SELECT
        kategori,
        ciro_2025 AS ciro,
        SUM(ciro_2025) OVER () AS total_ciro,
        DENSE_RANK() OVER (ORDER BY ciro_2025 DESC, kategori ASC) AS sira
    FROM
        CategorySales
)
SELECT
    kategori,
    ROUND(ciro, 2) AS ciro,
    ROUND(100.0 * ciro / total_ciro, 1) AS yüzde,
    sira
FROM
    RankedSales
ORDER BY
    sira ASC, kategori ASC;