WITH CustomerMonths AS (
  SELECT DISTINCT musteri_id, strftime('%Y-%m', tarih) AS order_month
  FROM siparisler
  WHERE tarih IS NOT NULL
),
RankedMonths AS (
  SELECT
    musteri_id,
    order_month,
    -- YYYY-MM stringini YYYYMM integer formatına çevirerek gruplama yapıyoruz
    CAST(SUBSTR(order_month, 1, 4) AS INTEGER) * 100 + CAST(SUBSTR(order_month, 6, 2) AS INTEGER) AS month_int,
    ROW_NUMBER() OVER (PARTITION BY musteri_id ORDER BY order_month) AS rn
  FROM CustomerMonths
),
Sequences AS (
  SELECT
    musteri_id,
    order_month,
    -- Ardışık grupları bulma hilesi: (month_int - rn) sabit kalırsa ardışıktır
    CAST(month_int - rn AS INTEGER) AS group_id
  FROM RankedMonths
),
SeriesInfo AS (
  SELECT
    musteri_id,
    group_id,
    MIN(order_month) AS start_month,
    COUNT(order_month) AS series_length
  FROM Sequences
  GROUP BY musteri_id, group_id
),
MaxSeriesPerCustomer AS (
  SELECT
    musteri_id,
    MAX(series_length) AS max_length
  FROM SeriesInfo
  GROUP BY musteri_id
)
SELECT
  T1.ad AS musteri_adi,
  T2.series_length,
  T2.start_month
FROM musteriler AS T1
JOIN SeriesInfo AS T2 ON T1.id = T2.musteri_id
JOIN MaxSeriesPerCustomer AS T3 ON T1.id = T3.musteri_id
WHERE T2.series_length = T3.max_length AND T2.series_length >= 3
ORDER BY T2.series_length DESC, T1.ad ASC;