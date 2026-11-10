
WITH MusteriAylar AS (
    -- Müşterinin sipariş verdiği benzersiz ayları 'YYYY-MM' formatında alır
    SELECT
        m.id AS musteri_id,
        m.ad AS musteri_adi,
        strftime('%Y-%m', s.tarih) AS siparis_ayi
    FROM musteriler m
    JOIN siparisler s ON m.id = s.musteri_id
),
ArdışıkSeriler AS (
    -- Ayları sıralar ve ardışık seri gruplarını tanımlar
    SELECT
        musteri_id,
        musteri_adi,
        siparis_ayi,
        -- Ayın sayısal temsilini alır (YYYYMM)
        CAST(strftime('%Y', siparis_ayi) AS INTEGER) * 100 + CAST(strftime('%m', siparis_ayi) AS INTEGER) AS ay_sayisi,
        -- Bir müşterinin ilk sipariş ayına göre ay farkı (Seri başlangıcı)
        (CAST(strftime('%Y', siparis_ayi) AS INTEGER) * 100 + CAST(strftime('%m', siparis_ayi) AS INTEGER)) - MIN(CAST(strftime('%Y', siparis_ayi) AS INTEGER) * 100 + CAST(strftime('%m', siparis_ayi) AS INTEGER)) OVER (PARTITION BY musteri_id) AS seri_baslangic_offset
    FROM MusteriAylar
),
SeriGrup AS (
    -- Ardışık ayları gruplar (seri_baslangic_offset aynı olanlar aynı seridir)
    SELECT
        musteri_id,
        musteri_adi,
        siparis_ayi,
        seri_baslangic_offset,
        COUNT(siparis_ayi) OVER (PARTITION BY musteri_id, seri_baslangic_offset) AS seri_uzunlugu,
        MIN(siparis_ayi) OVER (PARTITION BY musteri_id, seri_baslangic_offset) AS seri_baslangic_ayi
    FROM ArdışıkSeriler
)
-- Nihai Sonuç Seti: En az 3 ay olan ve en uzun seriyi/en erken başlayanı seçme
SELECT
    musteri_adi,
    seri_uzunlugu AS seri_uzunlugu_ay,
    seri_baslangic_ayi
FROM (
    SELECT
        musteri_adi,
        seri_uzunlugu,
        seri_baslangic_ayi,
        ROW_NUMBER() OVER (PARTITION BY musteri_id, seri_uzunlugu ORDER BY seri_baslangic_ayi ASC) AS rn_en_erken,
        RANK() OVER (PARTITION BY musteri_id ORDER BY seri_uzunlugu DESC, seri_baslangic_ayi ASC) AS rk_en_uzun
    FROM SeriGrup
) AS RankedSeriler
WHERE
    seri_uzunlugu >= 3 AND rk_en_uzun = 1
ORDER BY
    seri_uzunlugu DESC,
    musteri_adi ASC;
