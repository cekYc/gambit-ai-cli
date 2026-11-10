WITH OrderReturns AS (
    SELECT
        siparis_id,
        urun_id,
        SUM(adet) AS total_returned_qty
    FROM iadeler
    GROUP BY siparis_id, urun_id
),
NetOrderItems AS (
    SELECT
        SK.urun_id,
        SK.adet - COALESCE(OR.total_returned_qty, 0) AS net_adet_item,
        (SK.adet - COALESCE(OR.total_returned_qty, 0)) * SK.birim_fiyat AS net_ciro_item
    FROM
        siparis_kalemleri SK
    LEFT JOIN
        OrderReturns OR ON SK.siparis_id = OR.siparis_id AND SK.urun_id = OR.urun_id
)
SELECT
    U.ad AS urun_adi,
    SUM(NOI.net_adet_item) AS net_adet,
    CAST(SUM(NOI.net_ciro_item) AS REAL) AS net_ciro
FROM
    urunler U
JOIN
    NetOrderItems NOI ON U.id = NOI.urun_id
GROUP BY
    U.id, U.ad
ORDER BY
    net_ciro DESC,
    urun_adi ASC
LIMIT 5;