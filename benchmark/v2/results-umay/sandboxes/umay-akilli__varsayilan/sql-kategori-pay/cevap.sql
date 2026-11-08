WITH kategori_ciro AS (
    SELECT 
        u.kategori,
        COALESCE(SUM(sk.adet * sk.birim_fiyat), 0) AS ciro
    FROM urunler u
    LEFT JOIN siparis_kalemleri sk ON u.id = sk.urun_id
    LEFT JOIN siparisler s ON sk.siparis_id = s.id AND s.tarih LIKE '2025%'
    GROUP BY u.kategori
),
toplam_ciro AS (
    SELECT SUM(ciro) AS toplam FROM kategori_ciro
)
SELECT 
    kc.kategori,
    ROUND(kc.ciro, 2) AS ciro,
    ROUND(CASE WHEN tc.toplam = 0 THEN 0 ELSE (kc.ciro * 100.0 / tc.toplam) END, 1) AS yuzde,
    DENSE_RANK() OVER (ORDER BY kc.ciro DESC, kc.kategori ASC) AS sira
FROM kategori_ciro kc
CROSS JOIN toplam_ciro tc
ORDER BY kc.ciro DESC, kc.kategori ASC;