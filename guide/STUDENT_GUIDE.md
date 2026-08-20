# Data Quality Monitoring with Snowflake

**Hands-On Workshop | 4-8 hours (track-dependent) | Snowflake Enterprise Edition**

---

## Prerequisites (Complete Before Workshop Day)

1. **Snowflake Trial Account** -- Sign up at [signup.snowflake.com](https://signup.snowflake.com/). Choose **Enterprise Edition**. Any cloud/region works (for KSA: GCP Dammam if available).
2. **Snowflake CLI (`snow`)** -- Install: `brew install snowflake-cli` (macOS) or `pip install snowflake-cli` (all platforms). Verify: `snow --version`
3. **CLI Connection** -- Run `snow connection add`, name it `dq-lab`, enter your trial account details (account ID, username, password, role: ACCOUNTADMIN). Set default: `snow connection set-default dq-lab`. Test: `snow connection test`
4. **Notebook Workspace** -- In Snowsight, go to **Workspaces** (left sidebar), create a folder (e.g., `DQ_Lab`), then click **+ > Upload File** and upload all 15 `.ipynb` notebooks from the `notebooks/` folder.
5. **Warehouse** -- Create one if needed: `CREATE WAREHOUSE COMPUTE_WH WAREHOUSE_SIZE='XSMALL';`

> Detailed step-by-step instructions: see `guide/PREREQUISITES.md` in the lab repository.

---

## Architecture Overview

```
+------------------+     +-------------------+     +------------------+     +------------------+
|   RAW (Bronze)   |     |      SILVER       |     |       GOLD       |     |   DQ (Quality)   |
|                  | --> |                   | --> |                  |     |                  |
| STG_CUSTOMERS_   |     | INT_CUSTOMERS(65) |     | DIM_CUSTOMER     |     | RULES_CATALOG    |
|   ERP (30)       |     | INT_TRANSACTIONS  |     | FACT_TRANSACTIONS|     | Custom DMFs      |
| STG_CUSTOMERS_   |     |   (50)            |     | Views (3)        |     | Procedures       |
|   CRM (25)       |     |                   |     |                  |     | Alerts & Tasks   |
| STG_GOV_PORTAL   |     |                   |     |                  |     |                  |
|   (10)           |     |                   |     |                  |     |                  |
| STG_TRANSACTIONS |     |                   |     |                  |     |                  |
|   (50)           |     |                   |     |                  |     |                  |
+------------------+     +-------------------+     +------------------+     +------------------+
                                                                                    |
                          - - - - - - DMFs monitor all layers - - - - - - - - - - - +
```

---

## DQ Monitoring Lifecycle

```
 Data Lands    -->   DMFs Execute   -->   Expectations  -->   Alerts Fire   -->   Team Acts
 (auto/batch)        (serverless)         (PASS/FAIL)        (email/task)        (remediate)

 RAW tables          System + Custom      VALUE = 0?         SYSTEM$SEND         Fix source
 loaded              DMFs + Catalog       MET / NOT_MET      _EMAIL()            Update rules

 |<------------- Fully Automated (no human intervention) ------------>|    Human Action
```

---

## The 7 Data Quality Domains

Every DQ check in this lab maps to one of 7 domains. Understanding these domains helps you design comprehensive monitoring -- if you only check accuracy but ignore freshness, you'll serve correct-but-outdated data.

| Domain | Question It Answers | Concrete Example (from this lab) | What Happens If You Ignore It | Lab Module |
|--------|-------------------|----------------------------------|------------------------------|-----------|
| **Accuracy** | Is the data in the correct format and free of errors? | National ID `98765` is only 5 digits. Saudi IDs must be exactly 10 digits starting with 1 or 2. This ID was truncated by OCR during PDF extraction from the government portal. | A customer with an invalid National ID cannot complete digital onboarding (Absher, GOSI). They're stuck in manual processing costing SAR 200+ per case. | M2, M3 |
| **Completeness** | Are all required fields actually populated? | 10 out of 25 CRM customers have `NULL` National ID. In Salesforce, this field isn't mandatory -- sales reps skip it because they don't need it to close deals. | KYC compliance fails. The regulator asks "show me all customer identities" and you can only produce 50%. Potential fine: SAR 100K per audit finding. | M1, M3 |
| **Uniqueness** | Are there duplicate records that shouldn't exist? | Abdullah Al-Rashid appears in BOTH ERP (corporate email) and CRM (personal Gmail). Same National ID `1087654321`, two records. He'll get double-billed or double-counted in revenue reports. | Customer receives 2 invoices for the same service. Revenue dashboard shows SAR 15M but actual is SAR 12M. CFO makes decisions on inflated numbers. | M2, M4 |
| **Freshness** | Is the data up-to-date within our SLA? | Transaction row 4 was loaded 3 days ago but the SLA is 2 hours. The bank feed SFTP job failed silently on Friday, and nobody noticed until Monday's reconciliation. | Daily revenue reports show stale numbers. Treasury team thinks SAR 3M is missing. They raise an incident, waste 4 hours investigating, and discover it's just a delayed feed. | M1, M7 |
| **Validity** | Does the data fall within acceptable values or ranges? | Transaction type code must be one of: P (Payment), I (Invoice), T (Transfer), R (Refund). A value of "X" means the bank changed their codes without telling us -- our ETL will misclassify it. | Revenue breakdown report shows "UNKNOWN" category growing. Finance can't reconcile because they don't know if "X" is a payment or a refund. Month-end close is delayed 2 days. | M3, M5 |
| **Volume** | Did the expected amount of data arrive? | ERP normally sends 30 customer records per batch. If `ROW_COUNT` suddenly returns 0, the SFTP job failed. If it returns 3000, someone accidentally loaded a full extract instead of a delta. | A "zero rows" scenario means the Gold layer serves yesterday's data as if it's current. A "3000 rows" scenario means duplicates flood downstream, breaking uniqueness constraints. | M1 |
| **Consistency** | Do related fields agree with each other? | If `SOURCE_SYSTEM = 'ERP'`, then `IBAN` must NOT be NULL (ERP requires IBAN for payments). If `LAST_UPDATED` is before `CREATED_DATE`, someone backdated a record -- that's a data integrity violation. | An ERP customer without IBAN means their salary payment bounces. A backdated record means audit trail is compromised -- regulators see this as potential fraud concealment. | M3, M4 |

> **How to remember all 7:** Think of a SAR bank transfer arriving in your system. Is the amount **accurate** (correct format)? Is the sender name **complete** (not missing)? Is it **unique** (not a duplicate transfer)? Is it **fresh** (arrived today, not last week)? Is the type **valid** (PAYMENT, not GARBAGE)? Did the full batch arrive (**volume**)? Does the currency match the country (**consistency**)?

---

## Table of Contents

| # | Module | Duration |
|---|--------|----------|
| 0 | Environment Setup | 20 min |
| 0B | Data Pipeline: Dynamic Tables + dbt in Snowflake | 90 min |
| 1 | Raw Layer DQ - System DMFs | 45 min |
| 1B | DMF Costs & Optimization | 20 min |
| 2 | Silver Layer DQ - Custom DMFs | 60 min |
| 3 | Gold Layer DQ - Business Rules Catalog | 60 min |
| 4 | Expectations + Cross-Reference Integrity | 45 min |
| 4B | Record Investigation + Remediation | 45 min |
| 5 | AI/ML-Powered Data Quality | 75 min |
| 6 | Governance Integration | 45 min |
| 7 | Alerts - Close the Loop | 45 min |
| 8 | Dashboard (choose 1 of 3 variants: Native/Python/Streamlit) | 45 min |
| 9 | Teardown (cleanup all objects) | 5 min |

---

## Module 0: Environment Setup

**Duration:** 20 min

### What You Will Build

- Database `CORP_DWH` with Medallion schemas (RAW, SILVER, GOLD, DQ)
- Roles: `CORP_DQ_ADMIN` (lab exercises) and `CORP_DQ_STEWARD` (production pattern)
- Sample data with intentional DQ issues seeded across all layers
- Notification integration for email alerts

### Steps

1. Open the `0_SETUP` notebook in Snowflake Notebooks
2. Ensure you are using the `ACCOUNTADMIN` role
3. Run all cells sequentially (top to bottom)
4. Verify the row count output at the end matches expectations

### Expected Output (Verification Cell)

```
TABLE_NAME                  | ROW_COUNT
----------------------------|----------
RAW.STG_CUSTOMERS_ERP       | 30
RAW.STG_CUSTOMERS_CRM       | 25
RAW.STG_GOV_PORTAL          | 10
RAW.STG_TRANSACTIONS        | 50
```

### Intentional DQ Issues

| Issue | Location | Why It Matters |
|-------|----------|---------------|
| NULL National IDs | CRM feed (10 records) | Field not mandatory in Salesforce |
| Invalid National IDs | Gov Portal / GOSI (3 records) | OCR errors: too short, too long, contains letters |
| Blank CUSTOMER_REF | Transactions row 5 | Empty string -- NULL_COUNT won't catch it! |
| Duplicate customers | CRM + ERP overlap | Same person, different source emails |
| Stale record | Transaction row 4 | Loaded 3 days ago, SLA is 2 hours |
| Negative amount | Transaction row 6 | Incorrectly coded refund |
| Outlier amounts | Transactions rows 48-50 | SAR 87K-92K vs normal SAR 1K-22K |

> **Tip:** After setup, switch to `CORP_DQ_ADMIN` role for all remaining modules. You should NOT need ACCOUNTADMIN again.

---

## Module 1: Raw Layer DQ - System DMFs

**Duration:** 45 min

### Key Concept: Shift-Left Data Quality

Don't wait until Gold to find problems. Attach checks at the gate (RAW layer) so issues are detected the moment data lands.

### System DMFs You Will Use

| DMF | Level | Returns |
|-----|-------|---------|
| `SNOWFLAKE.CORE.ROW_COUNT` | Table | Total row count |
| `SNOWFLAKE.CORE.FRESHNESS` | Column (TIMESTAMP) | Seconds since last DML |
| `SNOWFLAKE.CORE.NULL_COUNT` | Column | Number of NULL values |
| `SNOWFLAKE.CORE.BLANK_COUNT` | Column | Number of empty strings |

### What You Will Do

1. Attach `ROW_COUNT` to ERP table (volume check)
2. Attach `FRESHNESS` to timestamp columns (SLA compliance)
3. Attach `NULL_COUNT` to CRM National ID and Email (completeness)
4. Attach `BLANK_COUNT` to Transaction CUSTOMER_REF (the tricky one!)
5. Set `TRIGGER_ON_CHANGES` schedule on all raw tables
6. Add expectations for automated pass/fail
7. Query results via `DATA_QUALITY_MONITORING_RESULTS`

> **Important:** `BLANK_COUNT` catches empty strings (`''`) that `NULL_COUNT` misses. Always use both for string columns where completeness matters.

### Key SQL Pattern

```sql
-- Attach a system DMF
ALTER TABLE schema.table
    ADD DATA METRIC FUNCTION SNOWFLAKE.CORE.NULL_COUNT ON (column_name);

-- Set automatic schedule
ALTER TABLE schema.table SET DATA_METRIC_SCHEDULE = 'TRIGGER_ON_CHANGES';

-- Add expectation
ALTER TABLE schema.table
    MODIFY DATA METRIC FUNCTION SNOWFLAKE.CORE.NULL_COUNT ON (column_name)
    ADD EXPECTATION my_expectation_name (VALUE = 0);

-- Query results
SELECT * FROM TABLE(SNOWFLAKE.LOCAL.DATA_QUALITY_MONITORING_RESULTS(
    REF_ENTITY_NAME => 'DB.SCHEMA.TABLE',
    REF_ENTITY_DOMAIN => 'TABLE'
));
```

> **Tip:** Results may take 1-2 minutes to appear after attaching DMFs. If you see empty results, wait and re-run the query cell.

---

## Module 2: Silver Layer DQ - Custom DMFs

**Duration:** 60 min

### Key Concept: Domain-Specific Validation

System DMFs catch generic issues. Custom DMFs encode YOUR business rules as first-class Snowflake objects.

### Custom DMFs You Will Build

| DMF Name | Validates | Regex/Logic |
|----------|-----------|-------------|
| `CHECK_NATIONAL_ID_FORMAT` | Saudi ID format | `^[12][0-9]{9}$` |
| `CHECK_IBAN_FORMAT` | Saudi IBAN format | `^SA[0-9A-Za-z]{22}$` |
| `CHECK_PHONE_FORMAT` | Saudi phone format | `^(\+966\|05\|00966)[0-9]{8,9}$` |
| `CHECK_DUPLICATES` | Uniqueness | `COUNT(*) - COUNT(DISTINCT col)` |
| `CHECK_AMOUNT_NOT_NEGATIVE` | No negative amounts | `WHERE col < 0` |

### DMF Signature Pattern

```sql
CREATE OR REPLACE DATA METRIC FUNCTION schema.dmf_name(
    ARG_T TABLE(ARG_C datatype)  -- table argument with typed column
)
RETURNS NUMBER                    -- must return a number
AS
$$
    SELECT COUNT(*)               -- count violations
    FROM ARG_T
    WHERE condition               -- your validation logic
$$;
```

### Expected Findings

- **3 invalid National IDs** (Gov Portal records: 98765, 30876543210, ABC1234567)
- **0 invalid IBANs** (all ERP IBANs are valid; CRM/Gov have NULL)
- **~9 duplicate National IDs** (IDs shared across ERP, CRM, and Gov sources)

---

## Module 3: Gold Layer DQ - Business Rules Catalog

**Duration:** 60 min

### Key Concept: Rules as Data

Instead of hard-coding checks, store rules in a catalog table. This enables self-service, auditability, and automation.

### Rules Catalog Schema

| Column | Purpose |
|--------|---------|
| RULE_NAME | Human-readable name |
| RULE_TYPE | REGEX, RANGE, ENUM, COMPLETENESS, UNIQUENESS, FRESHNESS |
| TARGET_SCHEMA/TABLE/COLUMN | Where to apply |
| REGEX_PATTERN / MIN_VALUE / MAX_VALUE / ENUM_VALUES | Rule parameters |
| SEVERITY | LOW, MEDIUM, HIGH, CRITICAL |
| OWNER | Responsible team |
| DMF_NAME | Auto-populated by provisioning procedure |

### The Auto-Provisioning Pattern

```
1. Steward adds rule to RULES_CATALOG
2. CALL PROVISION_DMFS_FROM_CATALOG()
3. Procedure reads catalog, generates DMF SQL
4. DMF is created and attached to target table
5. DMF_NAME column updated in catalog
```

> **Tip:** The provisioning procedure handles REGEX, RANGE, and ENUM rules automatically. COMPLETENESS and UNIQUENESS require manual DMF creation (or extend the procedure as a challenge).

---

## Module 4: Expectations - Automated Pass/Fail

**Duration:** 45 min

### Key Concept: Metrics to Decisions

A metric says "3 invalid IBANs." An expectation says "this table FAILS." Expectations transform monitoring into actionable gates.

### Expectation Syntax

```sql
ALTER TABLE db.schema.table
    MODIFY DATA METRIC FUNCTION dmf_name ON (column)
    ADD EXPECTATION expectation_name (VALUE operator threshold);

-- Examples:
-- Zero violations:       VALUE = 0
-- Freshness under 2hr:   VALUE <= 7200
-- At least 100 rows:     VALUE >= 100
```

### Reading Results

| EXPECTATION_RESULT | Meaning | Action |
|--------------------|---------|--------|
| `MET` | Value satisfies condition | No action needed |
| `NOT_MET` | Value violates condition | Investigate and remediate |

### DQ Scorecard (Python Cell)

Module 4 includes a Python cell that queries all expectation results and generates a summary scorecard showing pass/fail counts. This demonstrates how to build monitoring dashboards programmatically.

---

## Module 5: AI/ML-Powered Data Quality

**Duration:** 75 min

### Key Concept: AI-Augmented Quality

Traditional DQ relies on humans defining every rule. AI helps discover rules humans haven't thought of yet.

### Techniques Covered

| Technique | Use Case | Implementation |
|-----------|----------|---------------|
| Z-Score Anomaly Detection | Find statistical outliers in amounts | SQL with CTEs |
| Cortex AI Rule Suggestions | Let AI propose DQ rules from metadata | `SNOWFLAKE.CORTEX.COMPLETE()` |
| Anomaly DMF | Ongoing monitoring of distribution shifts | Custom DMF with z-score logic |

### Cortex AI Pattern

```sql
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'claude-haiku-4-5', -- model name (or use 'auto' for Snowflake-selected model)
    'Your prompt here'  -- natural language instruction
) AS AI_RESPONSE;
```

> **Note:** Cortex AI requires cross-region inference in some regions (e.g., ME-CENTRAL2). This was enabled in Module 0. If you get errors, verify with: `SHOW PARAMETERS LIKE 'CORTEX_ENABLED_CROSS_REGION' IN ACCOUNT;`

---

## Module 6: Governance Integration

**Duration:** 45 min

### Key Concept: DQ is Part of Horizon

Data Quality doesn't exist in isolation. It connects to tags, classification, lineage, and access history.

### Governance Features Used

| Feature | DQ Connection |
|---------|--------------|
| Object Tags | Classify sensitivity (PII), ownership, SLA tiers |
| Data Classification | Auto-detect columns that need DQ checks |
| Object Dependencies | Impact analysis when upstream quality degrades |
| Access History | Who consumed data that failed DQ checks? |

### Tags Created

- `SENSITIVITY` -- PII, SENSITIVE, INTERNAL, PUBLIC
- `DATA_DOMAIN` -- CUSTOMER, TRANSACTION, FINANCE, HR
- `SLA_TIER` -- TIER_1 (1hr), TIER_2 (4hr), TIER_3 (24hr)
- `DQ_OWNER` -- Responsible team

---

## Module 7: Alerts - Close the Loop

**Duration:** 45 min

### Key Concept: Monitoring Without Alerting is Just Reporting

The final piece: automated notifications when quality degrades.

### Components Built

| Object | Purpose |
|--------|---------|
| `ALERT_DQ_FAILURES` | Fires when expectations fail (every 5 min check) |
| `TASK_HOURLY_DQ_SWEEP` | Scheduled comprehensive DQ sweep |
| `DQ_SWEEP_LOG` | Historical record of sweep results |
| `RUN_DQ_SWEEP()` | Procedure that collects and logs DQ status |

### Alert Pattern

```sql
CREATE OR REPLACE ALERT alert_name
    WAREHOUSE = wh_name
    SCHEDULE = '5 MINUTES'
IF (EXISTS (
    SELECT 1 FROM ... WHERE condition
))
THEN
    CALL SYSTEM$SEND_EMAIL(integration, recipient, subject, body);
```

> **Remember:** Alerts are created SUSPENDED. You must `ALTER ALERT ... RESUME` to activate. Don't forget to SUSPEND them after the lab to avoid ongoing email noise.

---

## Module 4B: Record Investigation & Remediation

**Duration:** 45 min

### Key Concept: Detection Without Remediation is Noise

Module 4 detects issues. Module 4B completes the lifecycle: investigate, log, remediate, verify.

### What You Will Build

| Object | Purpose |
|--------|---------|
| `DQ_ISSUES_LOG` | Central issue registry with status lifecycle |
| `RESOLVE_ISSUE()` | Procedure to update issue status with audit trail |
| Investigation queries | Drill-down patterns to identify root causes |

### Remediation Lifecycle

```
DETECT → LOG → INVESTIGATE → REMEDIATE → VERIFY → CLOSE
```

Each issue progresses through states: `OPEN` → `INVESTIGATING` → `RESOLVED`. The stored procedure enforces valid transitions and logs resolution notes.

> **Tip:** The `NOT EXISTS` anti-duplicate guard in the logging INSERT prevents the same issue from being logged twice — a critical pattern for scheduled DQ sweeps.

---

## Module 8: Dashboard (Choose One Variant)

**Duration:** 45 min (pick 8A, 8B, or 8C)

### Key Concept: Make Quality Visible

All three variants share the same 4 dashboard views built on DMF results. The choice is about rendering technology:

| Variant | Technology | Best For |
|---------|-----------|----------|
| **8A** | SQL + native Snowsight charts | Quick setup, no dependencies |
| **8B** | Python + matplotlib | Custom visualizations, offline export |
| **8C** | Streamlit in Snowflake | Interactive app, shareable URL |

### Shared Views

| View | Shows |
|------|-------|
| `V_DQ_RESULTS_FLAT` | All DMF results with metadata |
| `V_DQ_SCORECARD` | Pass/fail rates per table |
| `V_DQ_TREND` | Quality metrics over time |
| `V_DQ_EXECUTIVE_SUMMARY` | High-level health score |

> **Recommendation:** Try 8A first (fastest). If you want to impress stakeholders, 8C produces a shareable app with a URL.

---

## Module 9: Teardown

**Duration:** 5 min

### What Gets Cleaned Up

| Object | Command |
|--------|---------|
| Database `CORP_DWH` | `DROP DATABASE` (removes all schemas, tables, views, Dynamic Tables, dbt objects) |
| Role `CORP_DQ_ADMIN` | `DROP ROLE` |
| Integration `CORP_DQ_ALERTS` | `DROP INTEGRATION` |

> **Warning:** This is irreversible. Only run when you're completely finished with the lab. The verification cell confirms all objects are gone.

---

## Glossary

| Term | Definition |
|------|-----------|
| **DMF (Data Metric Function)** | A Snowflake function that measures a quality aspect of a table or column. Returns a number. |
| **System DMF** | Built-in DMFs provided by Snowflake (ROW_COUNT, FRESHNESS, NULL_COUNT, BLANK_COUNT, etc.) |
| **Custom DMF** | User-defined DMFs for business-specific validation (regex checks, range checks, etc.) |
| **Expectation** | A condition applied to a DMF result that produces a PASS (MET) or FAIL (NOT_MET) verdict. |
| **Rules Catalog** | A table storing business rules as data, enabling self-service and auto-provisioning. |
| **TRIGGER_ON_CHANGES** | Schedule mode where DMFs run automatically whenever the underlying table receives DML. |
| **DATA_QUALITY_MONITORING_RESULTS** | Table function that returns all DMF measurement results for a given table. |
| **Snowflake Horizon** | Snowflake's governance framework including tags, classification, lineage, and access policies. |
| **Cortex AI** | Snowflake's built-in LLM capabilities, accessed via SNOWFLAKE.CORTEX.COMPLETE(). |

---

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Empty DQ results | DMFs haven't run yet | Wait 1-2 min, or manually trigger with INSERT/UPDATE on the table |
| "Insufficient privileges" | Wrong role | `USE ROLE CORP_DQ_ADMIN;` |
| "Data metric function not found" | DMF not created yet | Run Module 2 before Module 3/4 |
| Cortex AI error | Cross-region not enabled | `ALTER ACCOUNT SET CORTEX_ENABLED_CROSS_REGION = 'ANY_REGION';` |
| Alert not firing | Alert is suspended | `ALTER ALERT alert_name RESUME;` |
| "Cannot add DMF" error | Missing EXECUTE DATA METRIC FUNCTION grant | Re-run Module 0 role grants |

---

## Next Steps

1. **Deploy a Streamlit App** -- Build a self-service UI for the Rules Catalog
2. **Production Patterns** -- Set up RBAC with DQ_STEWARD role for data teams
3. **Extend the Catalog** -- Add your own business rules and run provisioning
4. **Dashboard Integration** -- Connect DQ_SWEEP_LOG to your BI tool
5. **Advanced AI** -- Use Cortex for anomaly explanations and root cause analysis
