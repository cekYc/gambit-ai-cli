WITH sehirler AS (
    SELECT DISTINCT sehir FROM musteriler
),
ciro_hesapla AS (
    SELECT m.sehir AS sehir,
           COUNT(DISTINCT s.musteri_id) AS musteri_sayisi,
           ROUND(COALESCE(SUM(sk.adet * sk.birim_fiyat), 0), 2) AS toplam_ciro
    FROM sehirler sh
    LEFT JOIN musteriler m ON m.sehir = sh.sehir
    LEFT JOIN siparisler s ON s.musteri_id = m.id
    LEFT JOIN siparis_kalemleri sk ON sk.siparis_id = s.id
    GROUP BY sh.sehir
)
SELECT sehir, musteri_sayisi, toplam_ciro
FROM ciro_hesapla
ORDER BY toplam_ciro DESC, sehir ASC;