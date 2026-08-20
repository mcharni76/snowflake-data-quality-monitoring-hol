-- models/marts/fact_transactions.sql
-- Valid transactions with derived customer key for referential integrity
-- Business logic: only valid transactions make it to Gold
-- CUSTOMER_ID is a hash of CUSTOMER_REF (independent of dim_customer).
-- In production, this would join on a shared natural key.
-- The DQ lab intentionally demonstrates orphan detection when keys don't match.

SELECT
    ROW_NUMBER() OVER (ORDER BY t.TXN_DATE, t.CUSTOMER_REF) AS TXN_ID,
    ABS(HASH(t.CUSTOMER_REF)) AS CUSTOMER_ID,
    t.CUSTOMER_REF,
    t.TXN_DATE,
    t.AMOUNT,
    t.CURRENCY,
    t.TXN_TYPE,
    t.SOURCE_SYSTEM,
    t.LOADED_AT
FROM {{ ref('stg_silver_transactions') }} t
WHERE t.IS_VALID = TRUE
