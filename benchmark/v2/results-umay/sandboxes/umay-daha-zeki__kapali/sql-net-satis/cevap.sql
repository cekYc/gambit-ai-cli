
WITH SiparisKalemleriCTE AS (
    SELECT 
        sk.urun_id, 
        sk.adet, 
        sk.birim_fiyat, 
        sk.siparis_id
    FROM siparis_kalemleri sk
),
IadelerCTE AS (
    SELECT 
        i.urun_id, 
        i.adet AS iade_adet, 
        i.siparis_id
    FROM iadeler i
),
UrunNetSatis AS (
    SELECT 
        sk.urun_id, 
        SUM(sk.adet) - COALESCE(SUM(i.iade_adet), 0) AS net_adet,
        -- Net ciro hesabı için her kalem bazında net miktarı bulup çarpmak gerekiyor. 
        -- Bu, iade satırlarının hangi sipariş kalemine karşılık geldiğini bilmeyi gerektirir. 
        -- Basitleştirilmiş Yaklaşım: (Toplam Satılan Adet - Toplam İade Edilen Adet) * Ortalama Birim Fiyat
        -- Ancak istenen tanım: her sipariş kaleminin (adet - o sipariş ve ürün için iade edilen adet) * birim_fiyat toplamı
        -- Bu tanım, iadelerin hangi spesifik kalemden geldiğini siparis_kalemleri ve iadeler tabloları arasındaki join ile bulmayı gerektirir.
        SUM(
            (sk.adet - COALESCE(COALESCE(SUM(CASE 
                WHEN i.urun_id = sk.urun_id AND i.siparis_id = sk.siparis_id THEN i.iade_adet ELSE 0 END), 0), 0)) * sk.birim_fiyat
        ) AS net_ciro
    FROM SiparisKalemleriCTE sk
    LEFT JOIN IadelerCTE i ON sk.urun_id = i.urun_id AND sk.siparis_id = i.siparis_id
    GROUP BY sk.urun_id
)
SELECT
    u.ad AS urun_adi, 
    uns.net_adet, 
    ROUND(uns.net_ciro, 2) AS net_ciro
FROM UrunNetSatis uns
JOIN urunler u ON uns.urun_id = u.id
ORDER BY 
    net_ciro DESC, 
    urun_adi ASC
LIMIT 5;
