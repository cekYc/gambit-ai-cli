WITH veriler AS (
    SELECT
        u.kategori AS kategori,
        COALESCE(SUM(sk.adet * sk.birim_fiyat) - COALESCE(SUM(i.adet * u.fiyat), 0), 0) AS ciro
    FROM urunler u
    LEFT JOIN siparis_kalemleri sk
        ON sk.urun_id = u.id
    LEFT JOIN siparisler s
        ON s.id = sk.siparis_id AND s.tarih GLOB '2025-*'
    LEFT JOIN iadeler i
        ON i.siparis_id = sk.siparis_id AND i.urun_id = sk.urun_id
    GROUP BY u.kategori
),
birlesik AS (
    SELECT
        kategori,
        ROUND(ciro, 2) AS ciro,
        ROUND(100.0 * ciro / SUM(ciro) OVER (), 1) AS yuzde,
        DENSE_RANK() OVER (ORDER BY ciro DESC) AS sira
    FROM veriler
)
SELECT
    kategori,
    ciro,
    yuzde,
    sira
FROM birlesik
ORDER BY sira ASC, kategori ASC;