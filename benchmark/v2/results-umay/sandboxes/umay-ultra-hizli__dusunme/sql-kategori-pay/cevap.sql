WITH CategoryNetCiro AS (
    SELECT
        u.kategori,
        -- Gross Ciro (2025)
        COALESCE(SUM(CASE WHEN s.tarih LIKE '2025-%' THEN sk.adet * sk.birim_fiyat ELSE 0 END), 0) AS GrossCiro,
        -- Total Returns (2025) - Assuming return value is based on urunler.fiyat
        COALESCE(SUM(CASE WHEN s_return.tarih LIKE '2025-%' THEN i.adet * u.fiyat ELSE 0 END), 0) AS TotalReturns
    FROM urunler u
    LEFT JOIN siparis_kalemleri sk ON u.id = sk.urun_id
    LEFT JOIN siparisler s ON sk.siparis_id = s.id
    LEFT JOIN iadeler i ON u.id = i.urun_id
    LEFT JOIN siparisler s_return ON i.siparis_id = s_return.id
    GROUP BY u.kategori
)
SELECT
    kategori,
    (GrossCiro - TotalReturns) AS Ciro,
    -- Calculate percentage: (Category Ciro / Total 2025 Ciro) * 100 (1 ondalığa yuvarlanmış)
    ROUND(
        (GrossCiro - TotalReturns) * 100.0 / SUM(GrossCiro - TotalReturns) OVER (),
        1
    ) AS Yuzde,
    -- Rank based on Ciro (DESC), then Kategori (ASC)
    DENSE_RANK() OVER (ORDER BY (GrossCiro - TotalReturns) DESC, kategori ASC) AS Sıra
FROM CategoryNetCiro
ORDER BY Sıra, kategori;