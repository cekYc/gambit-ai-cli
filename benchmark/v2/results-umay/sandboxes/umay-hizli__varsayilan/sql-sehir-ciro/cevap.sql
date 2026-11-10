WITH musteri_sehir AS (
  SELECT id AS musteri_id, sehir
  FROM musteriler
),
sip_musteri AS (
  SELECT DISTINCT s.id AS siparis_id, ms.sehir, ms.musteri_id
  FROM siparisler s
  JOIN musteri_sehir ms ON ms.musteri_id = s.musteri_id
),
kalem AS (
  SELECT sm.sehir,
         sm.siparis_id,
         sm.musteri_id,
         sk.urun_id,
         sk.adet * sk.birim_fiyat AS tutor
  FROM sip_musteri sm
  JOIN siparis_kalemleri sk ON sk.siparis_id = sm.siparis_id
),
iade_brut AS (
  SELECT k.sehir,
         k.siparis_id,
         k.urun_id,
         SUM(i.adet) AS iade_adet
  FROM kalem k
  JOIN iadeler i ON i.siparis_id = k.siparis_id AND i.urun_id = k.urun_id
  GROUP BY k.sehir, k.siparis_id, k.urun_id
),
iade_dusulecek AS (
  SELECT ib.sehir,
         ib.siparis_id,
         SUM(ib.iade_adet * sk.birim_fiyat) AS iade_tutar
  FROM iade_brut ib
  JOIN siparis_kalemleri sk
    ON sk.siparis_id = ib.siparis_id AND sk.urun_id = ib.urun_id
  GROUP BY ib.sehir, ib.siparis_id
),
net AS (
  SELECT k.sehir,
         SUM(k.tutor) - COALESCE(d.iade_tutar, 0) AS ciro
  FROM kalem k
  LEFT JOIN iade_dusulecek d
    ON d.sehir = k.sehir AND d.siparis_id = k.siparis_id
  GROUP BY k.sehir
),
musteri_say AS (
  SELECT sehir, COUNT(DISTINCT musteri_id) AS musteri_sayisi
  FROM sip_musteri
  GROUP BY sehir
)
SELECT m.sehir AS sehir_adi,
       COALESCE(ms.musteri_sayisi, 0) AS musteri_sayisi,
       ROUND(COALESCE(n.ciro, 0), 2) AS toplam_ciro
FROM (SELECT DISTINCT sehir FROM musteriler) m
LEFT JOIN musteri_say ms ON ms.sehir = m.sehir
LEFT JOIN net n ON n.sehir = m.sehir
ORDER BY toplam_ciro DESC, sehir_adi ASC;