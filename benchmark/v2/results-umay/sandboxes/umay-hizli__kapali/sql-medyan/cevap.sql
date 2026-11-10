-- SQLite 3.50 + CTE ve pencere fonksiyonları ile şehir bazlı sipariş sayısı ve medyan sipariş tutarı
-- Iadeler dikkate alınmaz; sipariş tutarı = kalem adet × birim_fiyat toplamı
WITH siparis_tutar AS (
    SELECT
        s.id AS siparis_id,
        m.sehir,
        COALESCE(SUM(sk.adet * sk.birim_fiyat), 0) AS toplam_tutar
    FROM siparisler s
    JOIN musteriler m ON m.id = s.musteri_id
    LEFT JOIN siparis_kalemleri sk ON sk.siparis_id = s.id
    GROUP BY s.id, m.sehir
),
sirali AS (
    SELECT
        sehir,
        toplam_tutar,
        ROW_NUMBER() OVER (PARTITION BY sehir ORDER BY toplam_tutar) AS sira,
        COUNT(*) OVER (PARTITION BY sehir) AS adet
    FROM siparis_tutar
)
SELECT
    sehir AS sehir,
    adet AS siparis_sayisi,
    ROUND(
        CASE
            WHEN adet % 2 = 1 THEN
                MAX(CASE WHEN sira = (adet + 1) / 2 THEN toplam_tutar END)
            ELSE
                0.5 * (
                    MAX(CASE WHEN sira = adet / 2 THEN toplam_tutar END) +
                    MAX(CASE WHEN sira = adet / 2 + 1 THEN toplam_tutar END)
                )
        END,
        2
    ) AS medyan
FROM sirali
GROUP BY sehir, adet
HAVING adet >= 2
ORDER BY medyan DESC, sehir ASC;