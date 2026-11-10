WITH CityCustomerCount AS (
    -- Şehirdeki sipariş vermiş farklı müşteri sayısını hesaplar
    SELECT m.sehir, COUNT(DISTINCT s.musteri_id) AS distinct_customers
    FROM musteriler m
    JOIN siparisler s ON m.id = s.musteri_id
    GROUP BY m.sehir
),
CityRevenue AS (
    -- Şehir bazında brüt satış ve iade tutarlarını hesaplar
    SELECT m.sehir, 
           SUM(sk.adet * sk.birim_fiyat) AS gross_sales, 
           SUM(i.adet * sk.birim_fiyat) AS total_returned_value
    FROM musteriler m
    JOIN siparisler s ON m.id = s.musteri_id
    JOIN siparis_kalemleri sk ON s.id = sk.siparis_id
    -- İade kalemlerini bulmak için LEFT JOIN kullanıyoruz, böylece siparişi olmayan şehirler etkilenmez.
    LEFT JOIN iadeler i ON s.id = i.siparis_id AND sk.urun_id = i.urun_id
    GROUP BY m.sehir
)
-- Tüm şehirleri listele (sipariş vermiş olsun veya olmasın)
SELECT
    m.sehir,
    COALESCE(ccc.distinct_customers, 0) AS musteri_sayisi,
    ROUND(COALESCE(cr.gross_sales, 0) - COALESCE(cr.total_returned_value, 0), 2) AS toplam_ciro
FROM
    musteriler m
LEFT JOIN
    CityCustomerCount ccc ON m.sehir = ccc.sehir
LEFT JOIN
    CityRevenue cr ON m.sehir = cr.sehir
ORDER BY
    toplam_ciro DESC,
    m.sehir ASC;