
WITH SiparisTutarlari AS (
    -- 1. Her siparişin toplam tutarını hesapla (iadeyi dikkate alma)
    SELECT
        s.id AS siparis_id,
        m.sehir,
        SUM(sk.adet * sk.birim_fiyat) AS siparis_tutari
    FROM siparisler s
    JOIN musteriler m ON s.musteri_id = m.id
    JOIN siparis_kalemleri sk ON s.id = sk.siparis_id
    GROUP BY s.id, m.sehir
),
SiraliTutarlar AS (
    -- 2. Şehir bazında sipariş tutarlarını sırala ve sıra numarasını ata
    SELECT
        sehir,
        siparis_tutari,
        ROW_NUMBER() OVER (PARTITION BY sehir ORDER BY siparis_tutari ASC) as rn,
        COUNT(*) OVER (PARTITION BY sehir) as siparis_sayisi
    FROM SiparisTutarlari
)
-- 3. Medyanı hesapla ve filtrele
SELECT
    sehir,
    siparis_sayisi,
    CASE
        -- Tek sayı ise tam ortadaki değer (rn = (N+1)/2)
        WHEN siparis_sayisi % 2 = 1 THEN siparis_tutari
        -- Çift sayı ise ortadaki iki değerin ortalaması (rn = N/2 ve rn = N/2 + 1)
        ELSE (siparis_tutari + (SELECT siparis_tutari FROM SiraliTutarlar WHERE sehir = SiraliTutarlar.sehir AND rn = siparis_sayisi / 2 + 1)) / 2.0
    END AS medyan
FROM SiraliTutarlar
WHERE siparis_sayisi >= 2 
AND rn = (siparis_sayisi + 1) / 2 -- Sadece medyan konumundaki satırı seçmek için
ORDER BY medyan DESC, sehir ASC;
