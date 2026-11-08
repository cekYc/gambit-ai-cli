WITH tum_kategoriler AS (
    SELECT DISTINCT kategori FROM urunler
),
satis AS (
    SELECT u.kategori AS kategori,
           SUM(sk.adet * sk.birim_fiyat) AS bruto
    FROM siparisler s
    JOIN siparis_kalemleri sk ON sk.siparis_id = s.id
    JOIN urunler u ON u.id = sk.urun_id
    WHERE s.tarih LIKE '2025-%'
    GROUP BY u.kategori
),
iade AS (
    SELECT u.kategori AS kategori,
           SUM(i.adet * sk.birim_fiyat) AS iade_miktari
    FROM iadeler i
    JOIN siparisler s ON s.id = i.siparis_id
    JOIN siparis_kalemleri sk ON sk.siparis_id = i.siparis_id AND sk.urun_id = i.urun_id
    JOIN urunler u ON u.id = i.urun_id
    WHERE s.tarih LIKE '2025-%'
    GROUP BY u.kategori
),
net AS (
    SELECT tk.kategori AS kategori,
           COALESCE(s.bruto,0) - COALESCE(i.iade_miktari,0) AS ciro
    FROM tum_kategoriler tk
    LEFT JOIN satis s ON s.kategori = tk.kategori
    LEFT JOIN iade i ON i.kategori = tk.kategori
),
toplam AS (
    SELECT SUM(ciro) AS toplam_ciro FROM net
)
SELECT n.kategori AS kategori,
       printf('%.2f', n.ciro) AS ciro,
       printf('%.1f', CASE WHEN t.toplam_ciro = 0 THEN 0.0 ELSE ROUND(100.0 * n.ciro / t.toplam_ciro, 1) END) AS yuzde,
       DENSE_RANK() OVER (ORDER BY n.ciro DESC, n.kategori ASC) AS sira
FROM net n, toplam t
ORDER BY sira, n.kategori ASC;
