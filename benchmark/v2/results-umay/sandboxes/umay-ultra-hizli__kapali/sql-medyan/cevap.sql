WITH MusteriSiparisBilgisi AS (
    -- Her siparişin toplam tutarını hesapla (iadeleri hariç)
    SELECT
        s.id AS siparis_id,
        m.sehir,
        s.tarih,
        SUM(sk.adet * sk.birim_fiyat) AS siparis_tutari
    FROM siparisler s
    JOIN musteriler m ON s.musteri_id = m.id
    JOIN siparis_kalemleri sk ON s.id = sk.siparis_id
    GROUP BY s.id, m.sehir, s.tarih
),
SiralanmisTutarlar AS (
    -- Şehir bazında tutarları alıp sırala
    SELECT
        sehir,
        siparis_tutari,
        COUNT(siparis_id) OVER (PARTITION BY sehir) as total_siparis_sayisi
    FROM MusteriSiparisBilgisi
)
-- Sonuçları oluşturma
SELECT
    sehir,
    total_siparis_sayisi AS siparis_sayisi,
    CASE
        WHEN total_siparis_sayisi < 2 THEN NULL -- En az 2 sipariş şartı
        WHEN total_siparis_sayisi % 2 = 1 THEN -- Tek sayıda sipariş
            (SELECT CAST(siparis_tutari AS REAL) FROM MusteriSiparisBilgisi WHERE sehir = SiralanmisTutarlar.sehir ORDER BY siparis_tutari ASC LIMIT 1 OFFSET (total_siparis_sayisi // 2))
        ELSE -- Çift sayıda sipariş
            (SELECT CAST(siparis_tutari AS REAL) FROM MusteriSiparisBilgisi WHERE sehir = SiralanmisTutarlar.sehir ORDER BY siparis_tutari ASC LIMIT 1 OFFSET (total_siparis_sayisi // 2 - 1)) + 
            (SELECT CAST(siparis_tutari AS REAL) FROM MusteriSiparisBilgisi WHERE sehir = SiralanmisTutarlar.sehir ORDER BY siparis_tutari ASC LIMIT 1 OFFSET (total_siparis_sayisi // 2)) 
            / 2.0
    END AS medyan
FROM SiralanmisTutarlar
WHERE total_siparis_sayisi >= 2
GROUP BY sehir, total_siparis_sayisi
ORDER BY medyan DESC, sehir ASC;