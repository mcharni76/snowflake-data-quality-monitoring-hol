-- models/staging/stg_silver_customers.sql
-- Staging view referencing the Silver Dynamic Table directly

SELECT
    CUSTOMER_NAME,
    CUSTOMER_NAME_AR,
    NATIONAL_ID,
    IBAN,
    EMAIL,
    PHONE,
    CITY,
    SOURCE_SYSTEM,
    DQ_SCORE,
    IS_DUPLICATE,
    LOADED_AT
FROM {{ source('silver', 'INT_CUSTOMERS') }}
