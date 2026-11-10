WITH tum_kategoriler AS (
    SELECT DISTINCT kategori FROM urunler
),
siparisler_2025 AS (
    SELECT id FROM siparisler WHERE substr(tarih, 1, 4) = '2025'
),
kategori_cirolari AS (
    SELECT
        k.kategori,
        COALESCE(SUM(sk.adet * sk.birim_fiyat), 0.0) AS ciro
    FROM tum_kategoriler k
    LEFT JOIN urunler u ON u.kategori = k.kategori
    LEFT JOIN siparis_kalemleri sk ON sk.urun_id = u.id
    LEFT JOIN siparisler_2025 s ON s.id = sk.siparis_id
    GROUP BY k.kategori
),
toplam_ciro AS (
    SELECT SUM(ciro) AS toplam FROM kategori_cirolari
)
SELECT
    kc.kategori AS kategori,
    ROUND(kc.ciro, 2) AS ciro,
    COALESCE(ROUND(kc.ciro * 100.0 / NULLIF(tc.toplam, 0), 1), 0.0) AS yuzde,
    DENSE_RANK() OVER (ORDER BY kc.ciro DESC) AS sira
FROM kategori_cirolari kc
CROSS JOIN toplam_ciro tc
ORDER BY kc.ciro DESC, kc.kategori ASC;