WITH MusteriSehir AS (
    -- Tüm müşterileri ve şehirlerini listeler
    SELECT id, sehir FROM musteriler
),
CiroHesaplama AS (
    -- Sipariş kalemlerinden sadece ciroyu (adet * birim_fiyat) hesaplar
    SELECT 
        s.musteri_id, 
        (sk.adet * sk.birim_fiyat) AS kalem_ciro
    FROM siparisler s
    JOIN siparis_kalemleri sk ON s.id = sk.siparis_id
)
SELECT
    ms.sehir,
    COUNT(DISTINCT CASE WHEN ch.musteri_id IS NOT NULL THEN ms.id END) AS musteri_sayisi,
    COALESCE(SUM(ch.kalem_ciro), 0.00) AS toplam_ciro
FROM MusteriSehir ms
LEFT JOIN CiroHesaplama ch ON ms.id = ch.musteri_id
GROUP BY ms.sehir
ORDER BY toplam_ciro DESC, ms.sehir ASC;