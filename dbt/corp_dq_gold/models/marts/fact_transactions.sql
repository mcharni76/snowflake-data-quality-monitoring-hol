-- models/marts/fact_transactions.sql
-- Valid transactions joined to customer dimension
-- Business logic: only valid transactions make it to Gold

SELECT
    ROW_NUMBER() OVER (ORDER BY t.TXN_DATE) AS TXN_ID,
    c.CUSTOMER_ID,
    t.TXN_DATE,
    t.AMOUNT,
    t.CURRENCY,
    t.TXN_TYPE,
    t.SOURCE_SYSTEM,
    t.LOADED_AT
FROM {{ ref('stg_silver_transactions') }} t
LEFT JOIN {{ ref('dim_customer') }} c
    ON t.CUSTOMER_REF = 'CUST-' || LPAD(c.CUSTOMER_ID::STRING, 3, '0')
WHERE t.IS_VALID = TRUE
