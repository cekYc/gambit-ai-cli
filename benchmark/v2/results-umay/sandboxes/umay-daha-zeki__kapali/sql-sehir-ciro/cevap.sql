WITH SehirMusteriSayisi AS (
    -- Her şehrin toplam farklı müşteri sayısını hesapla (sipariş verip vermemiş olanlar dahil)
    SELECT
        m.sehir,
        COUNT(DISTINCT m.id) AS farklı_musteri_sayisi
    FROM musteriler m
    GROUP BY m.sehir
),
SehirCiro AS (
    -- Her şehrin toplam cirosunu hesapla
    SELECT
        m.sehir,
        ROUND(SUM(sk.adet * sk.birim_fiyat), 2) AS toplam_ciro
    FROM musteriler m
    JOIN siparisler s ON m.id = s.musteri_id
    JOIN siparis_kalemleri sk ON s.id = sk.siparis_id
    GROUP BY m.sehir
)
-- Nihai birleştirme ve sıralama
SELECT
    sms.sehir,
    sms.farkli_musteri_sayisi,
    COALESCE(sc.toplam_ciro, 0.00) AS toplam_ciro
FROM SehirMusteriSayisi sms
LEFT JOIN SehirCiro sc ON sms.sehir = sc.sehir
ORDER BY
    toplam_ciro DESC,
    sms.sehir ASC;