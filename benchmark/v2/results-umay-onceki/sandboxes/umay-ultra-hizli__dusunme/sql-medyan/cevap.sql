WITH order_totals AS (
   SELECT m.sehir,
          s.id AS order_id,
          SUM(k.adet * k.birim_fiyat) AS total
   FROM siparis s
   JOIN musteriler m ON s.musteri_id = m.id
   JOIN siparis_kalemleri k ON s.id = k.siparis_id
   WHERE s.id NOT IN (SELECT siparis_id FROM iadeler)
   GROUP BY s.id, m.sehir
),
city_counts AS (
   SELECT sehir, COUNT(order_id) AS siparis_sayisi
   FROM order_totals
   GROUP BY sehir
   HAVING COUNT(order_id) >= 2
),
ordered_totals AS (
   SELECT ot.sehir,
          ot.total,
          ROW_NUMBER() OVER (PARTITION BY ot.sehir ORDER BY ot.total) AS rn,
          cc.siparis_sayisi AS cnt
   FROM order_totals ot
   JOIN city_counts cc ON ot.sehir = cc.sehir
),
median_vals AS (
   SELECT sehir,
          CASE WHEN cnt % 2 = 1 THEN
               MAX(CASE WHEN rn = (cnt+1)/2 THEN total END)
          ELSE
               (MAX(CASE WHEN rn = cnt/2 THEN total END) + MAX(CASE WHEN rn = cnt/2 + 1 THEN total END))/2.0
          END AS medyan
   FROM ordered_totals
   GROUP BY sehir
)
SELECT sehir,
       siparis_sayisi,
       ROUND(medyan, 2) AS medyan
FROM median_vals
JOIN city_counts USING (sehir)
ORDER BY medyan DESC, sehir ASC;