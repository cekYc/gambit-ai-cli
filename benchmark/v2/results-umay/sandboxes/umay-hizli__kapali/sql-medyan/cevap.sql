WITH sip_tutar AS (
  SELECT s.id AS siparis_id, m.sehir,
         SUM(sk.adet * sk.birim_fiyat) AS tutar
  FROM siparisler s
  JOIN musteriler m ON m.id = s.musteri_id
  JOIN siparis_kalemleri sk ON sk.siparis_id = s.id
  GROUP BY s.id
),
sirala AS (
  SELECT sehir, tutar,
         ROW_NUMBER() OVER (PARTITION BY sehir ORDER BY tutar) AS rn_asc,
         COUNT(*) OVER (PARTITION BY sehir) AS n
  FROM sip_tutar
),
medyan AS (
  SELECT sehir,
         AVG(tutar) AS medyan,
         MAX(n) AS n
  FROM sirala
  WHERE (n % 2 = 1 AND rn_asc = (n + 1) / 2)
     OR (n % 2 = 0 AND rn_asc IN (n / 2, n / 2 + 1))
  GROUP BY sehir
),
sayi AS (
  SELECT sehir, COUNT(*) AS siparis_sayisi
  FROM sip_tutar
  GROUP BY sehir
)
SELECT m.sehir,
       s.siparis_sayisi,
       ROUND(m.medyan, 2) AS medyan
FROM medyan m
JOIN sayi s ON s.sehir = m.sehir
WHERE m.n >= 2
ORDER BY m.medyan DESC, m.sehir ASC;