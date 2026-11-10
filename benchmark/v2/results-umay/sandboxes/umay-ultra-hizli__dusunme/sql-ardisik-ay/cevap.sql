WITH MonthlyOrders AS (
  -- Her müşteri için sipariş verdiği benzersiz ayları belirle
  SELECT
    s.musteri_id,
    strftime('%Y-%m', s.tarih) AS order_month
  FROM siparisler s
  GROUP BY s.musteri_id, order_month
),
ConsecutiveGroups AS (
  -- Ardışık ayları gruplamak için gap-and-island tekniği
  SELECT
    mo.musteri_id,
    mo.order_month,
    -- Tarihi YYYYMM formatına çevirerek sayısal karşılaştırma yapıyoruz
    CAST(strftime('%Y%m', mo.order_month) AS INTEGER) AS month_int,
    -- Her müşteri içinde ayları sırala ve sıra numarasını ata
    ROW_NUMBER() OVER (PARTITION BY mo.musteri_id ORDER BY mo.order_month) AS rn,
    -- Ardışık ayları aynı gruba atayan hesaplama (month_int - rn sabit kalır)
    (CAST(strftime('%Y%m', mo.order_month) AS INTEGER) - ROW_NUMBER() OVER (PARTITION BY mo.musteri_id ORDER BY mo.order_month)) AS group_id
  FROM MonthlyOrders mo
),
SequenceLengths AS (
  -- Her grubu (seriyi) say ve uzunluğunu hesapla
  SELECT
    cg.musteri_id,
    MIN(cg.order_month) AS start_month,
    COUNT(*) AS sequence_length
  FROM ConsecutiveGroups cg
  GROUP BY cg.musteri_id, cg.group_id
  HAVING COUNT(*) >= 3 -- Sadece en az 3 aylık serileri filtrele
),
RankedSequences AS (
  -- Her müşteri için en uzun seriyi (ve eşitlikte en erken başlayan seriyi) bulmak için sıralama
  SELECT
    sl.musteri_id,
    sl.sequence_length,
    sl.start_month,
    -- En uzun seri uzunluğuna göre azalan, eşitlikte en erken başlangıç ayına göre artan sıralama yap
    RANK() OVER (PARTITION BY sl.musteri_id ORDER BY sl.sequence_length DESC, sl.start_month ASC) AS rank_num
  FROM SequenceLengths sl
)
-- Sonuçları müşteri adı ile birleştir ve istenen sıralamayı uygula
SELECT
  m.ad AS musteri_adi,
  rs.sequence_length AS seri_uzunlugu,
  rs.start_month AS baslangic_ayi
FROM RankedSequences rs
JOIN musteriler m ON rs.musteri_id = m.id
WHERE rs.rank_num = 1 -- Sadece en iyi seriyi (en uzun ve en erken başlayan) al
ORDER BY
  seri_uzunlugu DESC,
  musteri_adi ASC;