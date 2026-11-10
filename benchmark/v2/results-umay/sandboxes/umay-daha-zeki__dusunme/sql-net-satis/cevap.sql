WITH Sales AS (
    -- Her ürün için toplam satılan adet ve toplam satış cirosu
    SELECT
        u.ad AS urun_adi,
        SUM(sk.adet) AS toplam_satilan_adet,
        SUM(sk.adet * sk.birim_fiyat) AS toplam_satis_cirosu
    FROM siparis_kalemleri sk
    JOIN urunler u ON sk.urun_id = u.id
    GROUP BY u.ad
),
Returns AS (
    -- Her ürün için toplam iade edilen adet ve iade cirosu
    SELECT
        u.ad AS urun_adi,
        SUM(i.adet) AS toplam_iade_adet,
        -- İade cirosu, ürünün güncel birim fiyatı üzerinden hesaplanır
        SUM(i.adet * u.fiyat) AS toplam_iade_cirosu
    FROM iadeler i
    JOIN urunler u ON i.urun_id = u.id
    GROUP BY u.ad
)
SELECT
    s.urun_adi,
    (COALESCE(s.toplam_satilan_adet, 0) - COALESCE(r.toplam_iade_adet, 0)) AS net_adet,
    (COALESCE(s.toplam_satis_cirosu, 0) - COALESCE(r.toplam_iade_cirosu, 0)) AS net_ciro
FROM Sales s
LEFT JOIN Returns r ON s.urun_adi = r.urun_adi
ORDER BY
    net_ciro DESC,
    urun_adi ASC
LIMIT 5;