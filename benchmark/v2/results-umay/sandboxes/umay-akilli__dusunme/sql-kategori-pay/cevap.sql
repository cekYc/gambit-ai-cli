WITH
-- 2025 sipariş ID'leri
siparisler_2025 AS (
    SELECT id FROM siparisler WHERE tarih LIKE '2025-%'
),
-- Tüm kategoriler
kategoriler AS (
    SELECT DISTINCT kategori FROM urunler
),
-- 2025 satışları (sipariş kalemleri)
satislar AS (
    SELECT
        u.kategori,
        SUM(sk.adet * sk.birim_fiyat) AS toplam_satis
    FROM siparis_kalemleri sk
    JOIN siparisler_2025 s2025 ON sk.siparis_id = s2025.id
    JOIN urunler u ON sk.urun_id = u.id
    GROUP BY u.kategori
),
-- 2025 iadeleri
iadeler_2025 AS (
    SELECT
        u.kategori,
        SUM(i.adet * sk.birim_fiyat) AS toplam_iade
    FROM iadeler i
    JOIN siparisler_2025 s2025 ON i.siparis_id = s2025.id
    JOIN urunler u ON i.urun_id = u.id
    JOIN siparis_kalemleri sk ON sk.siparis_id = i.siparis_id AND sk.urun_id = i.urun_id
    GROUP BY u.kategori
),
-- Kategori başına net ciro (satış - iade)
kategori_ciro AS (
    SELECT
        k.kategori,
        COALESCE(s.toplam_satis, 0) - COALESCE(i.toplam_iade, 0) AS ciro
    FROM kategoriler k
    LEFT JOIN satislar s ON k.kategori = s.kategori
    LEFT JOIN iadeler_2025 i ON k.kategori = i.kategori
),
-- Toplam ciro ve yüzdeler
ciro_hesapla AS (
    SELECT
        kategori,
        ROUND(ciro, 2) AS ciro,
        CASE
            WHEN (SELECT SUM(ciro) FROM kategori_ciro) = 0 THEN 0.0
            ELSE ROUND(ciro * 100.0 / (SELECT SUM(ciro) FROM kategori_ciro), 1)
        END AS yuzde
    FROM kategori_ciro
)
SELECT
    kategori,
    ciro,
    yuzde,
    DENSE_RANK() OVER (ORDER BY ciro DESC, kategori ASC) AS sira
FROM ciro_hesapla
ORDER BY sira, kategori;