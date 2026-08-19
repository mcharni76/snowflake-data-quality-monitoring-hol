-- models/marts/dim_customer.sql
-- Deduplicated customer dimension from Silver layer
-- Business logic: keep only non-duplicate records (primary source wins)

SELECT
    ROW_NUMBER() OVER (ORDER BY SOURCE_SYSTEM, CUSTOMER_NAME) AS CUSTOMER_ID,
    CUSTOMER_NAME,
    NATIONAL_ID,
    IBAN,
    EMAIL,
    PHONE,
    CITY,
    SOURCE_SYSTEM,
    DQ_SCORE,
    LOADED_AT AS CREATED_DATE,
    CURRENT_TIMESTAMP() AS LAST_UPDATED,
    TRUE AS IS_ACTIVE
FROM {{ ref('stg_silver_customers') }}
WHERE IS_DUPLICATE = FALSE
