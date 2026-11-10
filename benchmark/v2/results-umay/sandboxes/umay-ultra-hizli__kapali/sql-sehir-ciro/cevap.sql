WITH MusteriSehirler AS (
    -- Tüm müşterileri ve şehirlerini listele, sipariş vermiş olsun veya olmasın
    SELECT id, ad, sehir
    FROM musteriler
),
TumSehirler AS (
    -- Tüm şehirleri (sipariş vermiş ve vermemiş) listele
    SELECT DISTINCT sehir FROM musteriler
),
MusteriSiparisSayisi AS (
    -- Her şehirdeki farklı müşteri sayısını hesapla
    SELECT
        ms.sehir,
        COUNT(DISTINCT ms.id) AS musteri_sayisi
    FROM MusteriSehirler ms
    GROUP BY ms.sehir
),
CiroHesaplama AS (
    -- Her sipariş kalemi için brüt ciroyu hesapla
    SELECT
        s.sehir,
        (skl.adet * skl.birim_fiyat) AS kalem_ciro
    FROM siparis_kalemleri skl
    JOIN siparisler s_siparis ON skl.siparis_id = s_siparis.id
    JOIN musteriler s ON s_siparis.musteri_id = s.id
    WHERE s.sehir IS NOT NULL
),
ToplamCiro AS (
    -- Şehirlere göre toplam ciroyu hesapla
    SELECT
        s.sehir,
        SUM(cc.kalem_ciro) AS toplam_ciro
    FROM CiroHesaplama cc
    GROUP BY s.sehir
)
-- Sonuçları birleştirme ve istenen şartlara göre sıralama
SELECT
    ts.sehir,
    COALESCE(mss.musteri_sayisi, 0) AS musteri_sayisi,
    COALESCE(tc.toplam_ciro, 0.00) AS toplam_ciro
FROM TumSehirler ts
LEFT JOIN MusteriSiparisSayisi mss ON ts.sehir = mss.sehir
LEFT JOIN ToplamCiro tc ON ts.sehir = tc.sehir
ORDER BY
    toplam_ciro DESC,
    ts.sehir ASC;