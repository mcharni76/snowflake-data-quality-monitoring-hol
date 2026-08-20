# Appendix: How We Built the dbt Project

This appendix walks through how the `dbt/corp_dq_gold/` project was developed from scratch. Use it as a learning reference if you want to understand the "why" behind each file, or as a template for building your own dbt-in-Snowflake projects.

---

## What is dbt in Snowflake?

Traditional dbt runs externally (dbt Cloud, GitHub Actions, local CLI). **dbt in Snowflake** deploys the project as a first-class Snowflake object. No external scheduler, no CI/CD pipeline, no dbt Cloud subscription.

| Traditional dbt | dbt in Snowflake |
|----------------|-----------------|
| `dbt run` from terminal | `EXECUTE DBT PROJECT ... ARGS = 'run'` from SQL |
| Needs `profiles.yml` with password/key | No credentials (Snowflake handles auth) |
| Runs on your machine or CI/CD | Runs on Snowflake serverless compute |
| Deploy = push to Git + run | Deploy = `snow dbt deploy` (one command) |

---

## Step 1: Initialize the Project

We started with the standard dbt init structure:

```bash
mkdir -p dbt/corp_dq_gold/models/{staging,marts}
cd dbt/corp_dq_gold
```

Then created two config files:

### `dbt_project.yml` -- Project definition

```yaml
name: 'corp_dq_gold'
version: '1.0.0'
config-version: 2

profile: 'corp_dq_gold'

model-paths: ["models"]
test-paths: ["tests"]
seed-paths: ["seeds"]

target-path: "target"
clean-targets:
  - "target"

models:
  corp_dq_gold:
    marts:
      +materialized: table      # Gold = physical tables
    staging:
      +materialized: view       # Staging = lightweight views
```

**Key decisions:**
- `marts/` materialized as **table** because Gold data is consumed by BI tools that need predictable performance
- `staging/` materialized as **view** because they're just pass-through references to Silver Dynamic Tables (no need to duplicate data)

### `profiles.yml` -- Connection config

```yaml
corp_dq_gold:
  target: dev
  outputs:
    dev:
      type: snowflake
      database: CORP_DWH
      schema: GOLD
      warehouse: DQ_LAB_WH
      role: CORP_DQ_ADMIN
```

**Key decisions:**
- No `account`, `user`, or `password` fields -- when deployed to Snowflake, auth is handled by the deploying user's session
- `role: CORP_DQ_ADMIN` ensures the dbt project runs with lab permissions, not ACCOUNTADMIN
- Single `dev` target (in production you'd add `staging` and `prod`)

---

## Step 2: Define Sources (What does dbt read from?)

Sources tell dbt where upstream data lives. We point at the Silver Dynamic Tables:

### `models/schema.yml` -- Sources section

```yaml
version: 2

sources:
  - name: silver
    database: CORP_DWH
    schema: SILVER
    description: "Silver layer Dynamic Tables (auto-refreshing from RAW)"
    tables:
      - name: INT_CUSTOMERS
        description: "Unified customer table from 3 source systems"
      - name: INT_TRANSACTIONS
        description: "Parsed and typed transactions from bank feed"
```

**Why declare sources?**
- dbt tracks lineage: it knows Gold depends on Silver
- `{{ source('silver', 'INT_CUSTOMERS') }}` generates fully-qualified `CORP_DWH.SILVER.INT_CUSTOMERS`
- If the table moves or renames, you change one line here, not every model

---

## Step 3: Build Staging Models (Thin layer over sources)

Staging models are the entry point into the dbt DAG. They reference sources and apply minimal logic.

### `models/staging/stg_silver_customers.sql`

```sql
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
    SOURCE_PRIORITY,
    DQ_SCORE,
    IS_DUPLICATE,
    LOADED_AT
FROM {{ source('silver', 'INT_CUSTOMERS') }}
```

### `models/staging/stg_silver_transactions.sql`

```sql
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
```

**Why have staging at all if it's just a SELECT *?**

1. **Decoupling** -- if we rename columns, add filters, or change types, we change staging only. Marts don't care.
2. **Lineage** -- dbt draws the DAG: `source → staging → marts`. Without staging, sources connect directly to marts, which gets messy at scale.
3. **Testing** -- we can add tests at the staging layer (e.g., "never more than 100 rows") without modifying the mart.

---

## Step 4: Build Mart Models (Business logic)

Marts contain the real transformation logic. These become Gold tables.

### `models/marts/dim_customer.sql`

```sql
-- Deduplicated customer dimension from Silver layer
-- Business logic: keep only non-duplicate records (primary source wins)
-- Surrogate key uses stable hash to ensure consistent IDs across refreshes

SELECT
    ABS(HASH(COALESCE(NATIONAL_ID, '') || '|' || SOURCE_SYSTEM || '|' || COALESCE(EMAIL, ''))) AS CUSTOMER_ID,
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
```

**Design decisions:**
- `WHERE IS_DUPLICATE = FALSE` -- Silver already flagged duplicates (via ROW_NUMBER over NATIONAL_ID). Gold only keeps the "winner" (highest SOURCE_PRIORITY).
- `ABS(HASH(...)) AS CUSTOMER_ID` -- deterministic surrogate key using a hash of NATIONAL_ID + SOURCE_SYSTEM + EMAIL. Unlike ROW_NUMBER(), this is stable across full refreshes.
- `IS_ACTIVE = TRUE` -- all records start active. A future SCD pattern would set this to FALSE when a customer is deactivated.

### `models/marts/fact_transactions.sql`

```sql
-- Valid transactions with derived customer key for referential integrity
-- Business logic: only valid transactions make it to Gold
-- CUSTOMER_ID is a hash of CUSTOMER_REF (independent of dim_customer).
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
```

**Design decisions:**
- `WHERE t.IS_VALID = TRUE` -- Silver flags invalid records (blank ref, negative amount, parse failures). Only clean rows reach Gold.
- `ABS(HASH(t.CUSTOMER_REF)) AS CUSTOMER_ID` -- derived numeric key enables DMF attachment and referential integrity checks. Because it hashes a different input than dim_customer's key, orphans are always detected (intentional DQ demonstration).
- `CUSTOMER_REF` kept as-is -- the original bank feed reference, useful for traceability.
- `ROW_NUMBER() ... AS TXN_ID` -- surrogate key for the fact table, ordered deterministically by date + ref.

---

## Step 5: Add Tests (schema.yml)

dbt tests validate data after materialization. They're defined declaratively in YAML:

### `models/schema.yml` -- Models + tests section

```yaml
models:
  - name: dim_customer
    description: "Deduplicated customer dimension - one row per unique customer"
    columns:
      - name: CUSTOMER_ID
        tests:
          - unique          # No two rows share the same ID
          - not_null        # Every row must have an ID
      - name: NATIONAL_ID
        tests:
          - unique:
              where: "NATIONAL_ID IS NOT NULL"  # Unique AMONG non-nulls
      - name: EMAIL
        tests:
          - not_null
      - name: SOURCE_SYSTEM
        tests:
          - accepted_values:
              values: ['ERP', 'CRM', 'GOV_PORTAL']

  - name: fact_transactions
    description: "Valid financial transactions - only records passing validation reach Gold"
    columns:
      - name: TXN_ID
        tests:
          - unique
          - not_null
      - name: CUSTOMER_ID
        description: "Derived numeric key (hash of CUSTOMER_REF)"
        tests:
          - not_null
      - name: CUSTOMER_REF
        description: "Customer reference from bank feed"
        tests:
          - not_null
      - name: AMOUNT
        tests:
          - not_null
      - name: TXN_TYPE
        tests:
          - accepted_values:
              values: ['PAYMENT', 'INVOICE', 'TRANSFER', 'REFUND']
```

**Test types used:**
| Test | What it checks | Fails when... |
|------|---------------|---------------|
| `unique` | No duplicate values | Two rows have the same value |
| `not_null` | No NULL values | Any row has NULL |
| `accepted_values` | Value in allowed list | A row has 'UNKNOWN' or unexpected value |
| `relationships` | FK exists in parent | A value in child doesn't exist in parent (not used here -- see Module 4 for DMF-based FK checks) |

---

## Step 6: Deploy to Snowflake

With the project developed, deploy it as a Snowflake-native object:

```bash
cd dbt/corp_dq_gold

# Deploy (uploads project as a Snowflake object)
snow dbt deploy CORP_DQ_GOLD --connection dq-lab --source . --database CORP_DWH --schema GOLD

# Verify it exists
snow dbt list --in schema GOLD --database CORP_DWH
```

Once deployed, you can run it from SQL (no CLI needed):

```sql
-- Build all models (creates/refreshes Gold tables)
EXECUTE DBT PROJECT CORP_DWH.GOLD.CORP_DQ_GOLD ARGS = 'run';

-- Run all tests
EXECUTE DBT PROJECT CORP_DWH.GOLD.CORP_DQ_GOLD ARGS = 'test';

-- Run a specific model
EXECUTE DBT PROJECT CORP_DWH.GOLD.CORP_DQ_GOLD ARGS = 'run --select dim_customer';
```

---

## The Complete DAG

```
sources:                staging:                marts:
                        (views)                 (tables)

INT_CUSTOMERS  ──────>  stg_silver_customers  ──────>  dim_customer
(Dynamic Table)

INT_TRANSACTIONS ────>  stg_silver_transactions ─────>  fact_transactions
(Dynamic Table)
```

**Data flow:**
1. Source systems feed RAW tables (Module 0)
2. Dynamic Tables auto-refresh Silver from RAW (Module 0B Part A)
3. dbt reads Silver, deduplicates, and materializes Gold (Module 0B Part B)
4. DMFs monitor ALL layers continuously (Modules 1-7)

---

## dbt Tests vs DMFs: Complementary, Not Competing

| Aspect | dbt Tests | Snowflake DMFs |
|--------|-----------|---------------|
| **Run when** | On demand (`dbt test` / `EXECUTE ... 'test'`) | Continuously (TRIGGER_ON_CHANGES) |
| **Scope** | Gold layer only (whatever dbt builds) | Any table/view in any schema |
| **Failure mode** | Blocks pipeline (test fails = don't deploy) | Fires alert (data already landed) |
| **Best for** | Build-time gates before promoting to Gold | Runtime monitoring after data arrives |
| **Who writes** | Analytics engineers (YAML) | Data engineers + stewards (SQL/catalog) |

**The hybrid pattern used in this lab:**
- dbt tests catch bugs **before** data reaches Gold (build-time gate)
- DMFs catch drift **after** data arrives in any layer (runtime monitor)
- Together: nothing bad gets in (dbt) AND nothing bad goes unnoticed (DMFs)

---

## Building Your Own dbt-in-Snowflake Project

If you want to create a new project from scratch:

```bash
# 1. Create project structure
mkdir -p my_project/models/{staging,marts}
cd my_project

# 2. Create dbt_project.yml (copy from above, change name)
# 3. Create profiles.yml (set your database/schema/warehouse/role)
# 4. Define sources in models/schema.yml
# 5. Write staging models (one per source table)
# 6. Write mart models (business logic + joins)
# 7. Add tests in schema.yml
# 8. Deploy:
snow dbt deploy MY_PROJECT --connection dq-lab --source . --database MY_DB --schema MY_SCHEMA

# 9. Execute:
snow dbt execute -c default --database MY_DB --schema MY_SCHEMA MY_PROJECT run
```

**Tips:**
- Start small: 1 source, 1 staging, 1 mart. Add complexity after it works.
- Use `+materialized: view` for staging, `+materialized: table` for marts.
- No passwords in `profiles.yml` -- Snowflake handles auth at deploy time.
- Run tests after every model change: `EXECUTE DBT PROJECT ... ARGS = 'test'`
