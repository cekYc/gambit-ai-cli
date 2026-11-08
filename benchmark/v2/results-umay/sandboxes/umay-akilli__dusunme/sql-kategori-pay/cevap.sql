WITH kategoriler AS (
    SELECT DISTINCT kategori FROM urunler
),
yil_2025_siparisler AS (
    SELECT id FROM siparisler WHERE tarih LIKE '2025-%'
),
kategori_ciro AS (
    SELECT 
        k.kategori,
        COALESCE(SUM(sk.adet * sk.birim_fiyat), 0) AS ciro
    FROM kategoriler k
    LEFT JOIN urunler u ON u.kategori = k.kategori
    LEFT JOIN siparis_kalemleri sk ON sk.urun_id = u.id
    LEFT JOIN yil_2025_siparisler s ON s.id = sk.siparis_id
    GROUP BY k.kategori
),
toplam_ciro AS (
    SELECT SUM(ciro) AS toplam FROM kategori_ciro
)
SELECT 
    kc.kategori,
    ROUND(kc.ciro, 2) AS ciro,
    ROUND(CASE WHEN t.toplam > 0 THEN (kc.ciro * 100.0 / t.toplam) ELSE 0 END, 1) AS yuzde,
    DENSE_RANK() OVER (ORDER BY kc.ciro DESC, kc.kategori ASC) AS sira
FROM kategori_ciro kc
CROSS JOIN toplam_ciro t
ORDER BY sira, kc.kategori ASC;