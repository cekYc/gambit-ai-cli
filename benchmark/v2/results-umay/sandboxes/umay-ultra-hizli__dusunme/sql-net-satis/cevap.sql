WITH ProductRevenue AS (
    -- Adet bazlı iade miktarını sipariş bazında hesapla
    SELECT
        sk.urun_id,
        SUM((sk.adet - COALESCE(ir.returned_qty, 0)) * sk.birim_fiyat) AS net_ciro
    FROM siparis_kalemleri sk
    LEFT JOIN (
        -- Her bir (siparis_id, urun_id) çifti için iade edilen toplam adeti bul
        SELECT siparis_id, urun_id, SUM(adet) AS returned_qty
        FROM iadeler
        GROUP BY siparis_id, urun_id
    ) ir ON sk.siparis_id = ir.siparis_id AND sk.urun_id = ir.urun_id
    GROUP BY sk.urun_id
),
ProductMetrics AS (
    -- Ürün bazında toplam satılan ve iade edilen adetleri hesapla
    SELECT
        T1.urun_id,
        SUM(T1.adet) AS total_sold,
        COALESCE((SELECT SUM(adet) FROM iadeler WHERE urun_id = T1.urun_id), 0) AS total_returned,
        SUM(T1.adet) - COALESCE((SELECT SUM(adet) FROM iadeler WHERE urun_id = T1.urun_id), 0) AS net_adet
    FROM siparis_kalemleri T1
    GROUP BY T1.urun_id
)
-- Sonuçları birleştir, sırala ve ilk 5'i getir
SELECT
    U.ad AS urun_adi,
    ROUND(PR.net_ciro, 2) AS net_ciro,
    PM.net_adet
FROM urunler U
JOIN ProductRevenue PR ON U.id = PR.urun_id
JOIN ProductMetrics PM ON U.id = PM.urun_id
ORDER BY
    net_ciro DESC,
    U.ad ASC
LIMIT 5;