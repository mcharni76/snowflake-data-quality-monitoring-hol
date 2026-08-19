-- models/staging/stg_silver_transactions.sql
-- Staging view referencing the Silver Dynamic Table directly

SELECT
    CUSTOMER_REF,
    TXN_DATE,
    AMOUNT,
    CURRENCY,
    TXN_TYPE,
    SOURCE_SYSTEM,
    IS_VALID,
    LOADED_AT
FROM {{ source('silver', 'INT_TRANSACTIONS') }}
