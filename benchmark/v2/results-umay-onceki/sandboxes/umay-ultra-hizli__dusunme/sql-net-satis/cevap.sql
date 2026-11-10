WITH order_returns AS (
    SELECT siparis_id, urun_id, SUM(adet) as iade_adet
    FROM iadeler
    GROUP BY siparis_id, urun_id
),
base AS (
    SELECT sk.urun_id, sk.adet, sk.birim_fiyat, COALESCE(or_.iade_adet, 0) as iade_adet
    FROM siparis_kalemleri sk
    LEFT JOIN order_returns or_ ON sk.siparis_id = or_.siparis_id AND sk.urun_id = or_.urun_id
),
product_stats AS (
    SELECT u.ad as urun_adi,
           ROUND(SUM(b.adet - b.iade_adet), 2) as net_adet,
           ROUND(SUM((b.adet - b.iade_adet) * b.birim_fiyat), 2) as net_ciro
    FROM base b
    JOIN urunler u ON b.urun_id = u.id
    GROUP BY u.ad
)
SELECT urun_adi, net_adet, net_ciro
FROM product_stats
ORDER BY net_ciro DESC, urun_adi ASC
LIMIT 5