WITH m AS (
    SELECT musteri_id, strftime('%Y-%m', tarih) AS ym
    FROM siparisler
    GROUP BY musteri_id, ym
),
numbered AS (
    SELECT musteri_id, ym,
           CAST(strftime('%Y', ym) AS INTEGER) * 12
           + CAST(strftime('%m', ym) AS INTEGER) AS mon_idx
    FROM m
),
grp AS (
    SELECT musteri_id, ym, mon_idx,
           mon_idx - ROW_NUMBER() OVER (
               PARTITION BY musteri_id
               ORDER BY ym
           ) AS grp
    FROM numbered
),
agg AS (
    SELECT musteri_id, grp,
           COUNT(*) AS len,
           MIN(ym) AS start_ym
    FROM grp
    GROUP BY musteri_id, grp
),
best AS (
    SELECT musteri_id, len, start_ym,
           ROW_NUMBER() OVER (
               PARTITION BY musteri_id
               ORDER BY len DESC, start_ym ASC
           ) AS rn
    FROM agg
)
SELECT m.ad AS musteri_adi,
       b.len AS seri_uzunlugu,
       b.start_ym AS baslangic_ayi
FROM best b
JOIN musteriler m ON m.id = b.musteri_id
WHERE b.rn = 1
  AND b.len >= 3
ORDER BY b.len DESC, m.ad ASC;