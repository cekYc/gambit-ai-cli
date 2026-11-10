WITH 
tum_sehirler AS (
    SELECT DISTINCT sehir FROM musteriler
),
musteri_ile_siparis AS (
    SELECT m.sehir, m.id AS musteri_id
    FROM musteriler m
    JOIN siparisler s ON m.id = s.musteri_id
),
MusteriSayisi AS (
    SELECT sehir, COUNT(DISTINCT musteri_id) AS unique_customers
    FROM musteri_ile_siparis
    GROUP BY sehir
),
CiroHesapla AS (
    SELECT m.sehir, ROUND(SUM(sk.adet * sk.birim_fiyat), 2) AS ciro
    FROM musteriler m
    JOIN siparisler s ON m.id = s.musteri_id
    JOIN siparis_kalemleri sk ON s.id = sk.siparis_id
    GROUP BY m.sehir
)
SELECT t.sehir,
       COALESCE(ms.unique_customers, 0) AS unique_customers,
       COALESCE(ch.ciro, 0) AS ciro
FROM tum_sehirler t
LEFT JOIN MusteriSayisi ms ON t.sehir = ms.sehir
LEFT JOIN CiroHesapla ch ON t.sehir = ch.sehir
ORDER BY ciro DESC, t.sehir ASC;
