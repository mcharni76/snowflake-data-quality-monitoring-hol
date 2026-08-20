# Workshop Cards

One-page summary per module. Use as printed handouts, slide deck overview, or quick reference.

---

## Module 0: Environment Setup

| | |
|---|---|
| **Duration** | 20 min |
| **Role** | ACCOUNTADMIN |
| **Domain** | Infrastructure |
| **What you build** | Medallion architecture (RAW/SILVER/GOLD/DQ schemas), 2 roles, 4 source tables with 115 rows of seeded data |
| **Key concept** | Each source system has different quality characteristics -- DQ starts with understanding your sources |
| **Prerequisite** | ACCOUNTADMIN access, Enterprise Edition |
| **Checkpoint** | 4 RAW tables: ERP (30), CRM (25), Gov Portal (10), Bank (50) |

---

## Module 0B: Data Pipeline

| | |
|---|---|
| **Duration** | 90 min |
| **Role** | CORP_DQ_ADMIN |
| **Domain** | Transformation |
| **What you build** | 2 Dynamic Tables (RAW->Silver), real dbt project deployed in Snowflake (Silver->Gold), 3 Gold views |
| **Key concept** | Hybrid pattern: DT for "keep it fresh" (auto-refresh), dbt for "keep it correct" (governed, tested) |
| **Prerequisite** | Module 0 + `snow` CLI installed |
| **Checkpoint** | INT_CUSTOMERS (65 rows), INT_TRANSACTIONS (50 rows), DIM_CUSTOMER (deduplicated), dbt tests pass |

---

## Module 1: Raw Layer DQ

| | |
|---|---|
| **Duration** | 45 min |
| **Role** | CORP_DQ_ADMIN |
| **Domain** | Volume, Freshness, Completeness |
| **What you build** | 8+ system DMFs on RAW tables, expectations with pass/fail, TRIGGER_ON_CHANGES schedules |
| **Key concept** | Shift-left: catch issues at the gate, not after expensive transforms |
| **Prerequisite** | Module 0B (Silver tables must exist for schedule triggers) |
| **Checkpoint** | 3+ DMFs on ERP, 2+ on CRM, expectations firing on STG_TRANSACTIONS |

---

## Module 1B: DMF Costs

| | |
|---|---|
| **Duration** | 20 min |
| **Role** | CORP_DQ_ADMIN |
| **Domain** | Cost Optimization |
| **What you build** | Cost consumption queries, monthly projection view, tiered monitoring strategy |
| **Key concept** | TRIGGER_ON_CHANGES costs 12x more than hourly cron on high-frequency tables. Tier your monitoring. |
| **Prerequisite** | Module 1 (DMFs must have run for Account Usage data) |
| **Checkpoint** | Can query DATA_QUALITY_MONITORING_USAGE_HISTORY (may show 0 if just started) |

---

## Module 2: Silver Custom DMFs

| | |
|---|---|
| **Duration** | 60 min |
| **Role** | CORP_DQ_ADMIN |
| **Domain** | Accuracy, Uniqueness |
| **What you build** | 5 custom DMFs (National ID, IBAN, Phone, Duplicates, Negative Amount) |
| **Key concept** | Business rules encoded as first-class Snowflake objects -- grantable, auditable, versionable |
| **Prerequisite** | Module 0B (INT_CUSTOMERS must exist) |
| **Checkpoint** | 5 DMFs in DQ schema, 3 invalid National IDs detected, 0 invalid IBANs, ≥2 duplicates |

---

## Module 3: Gold Rules Catalog

| | |
|---|---|
| **Duration** | 60 min |
| **Role** | CORP_DQ_ADMIN |
| **Domain** | All (governance infrastructure) |
| **What you build** | RULES_CATALOG table (12 rules), auto-provisioning procedure, multi-column consistency DMFs |
| **Key concept** | Rules as data: self-service, auditable, automatable. Stewards add rules without SQL. |
| **Prerequisite** | Module 2 (DMFs exist for reference) |
| **Checkpoint** | 7+ rules provisioned with DMF_NAME populated, consistency checks attached |

---

## Module 4: Expectations

| | |
|---|---|
| **Duration** | 45 min |
| **Role** | CORP_DQ_ADMIN |
| **Domain** | Accuracy, Consistency |
| **What you build** | Expectations on Gold/Silver DMFs, cross-reference integrity DMFs (FK orphans, ETL data loss) |
| **Key concept** | From metrics to decisions: VALUE -> threshold -> PASS/FAIL verdict (automated) |
| **Prerequisite** | Modules 2+3 (DMFs attached to tables) |
| **Checkpoint** | MET/NOT_MET results visible, orphan detection working |

---

## Module 4B: Remediation

| | |
|---|---|
| **Duration** | 45 min |
| **Role** | CORP_DQ_ADMIN |
| **Domain** | All (operations) |
| **What you build** | DQ_ISSUES_LOG, idempotent auto-scan procedure, quarantine workflow, resolution procedure, SLA report |
| **Key concept** | Detection without remediation is just noise. Issues need owners, SLAs, and audit trails. |
| **Prerequisite** | Module 4 (expectations configured) |
| **Checkpoint** | Issues logged with lifecycle (OPEN -> QUARANTINED -> ACCEPTED), procedure is idempotent |

---

## Module 5: AI/ML DQ

| | |
|---|---|
| **Duration** | 75 min |
| **Role** | CORP_DQ_ADMIN |
| **Domain** | All (AI-augmented) |
| **What you build** | Z-score anomaly DMF, NL rule parsing (Cortex), bulk AI suggestion procedure with JSON parsing, system DMF recommender |
| **Key concept** | AI suggests -> Human reviews -> Catalog stores -> Procedure provisions |
| **Prerequisite** | Module 3 (catalog exists), cross-region inference enabled |
| **Checkpoint** | Anomaly DMF attached, AI suggestions parsed into catalog, FACT_TRANSACTIONS fully monitored |

---

## Module 6: Governance

| | |
|---|---|
| **Duration** | 45 min |
| **Role** | CORP_DQ_ADMIN |
| **Domain** | Classification, Lineage |
| **What you build** | 4 tag types (SENSITIVITY, DATA_DOMAIN, SLA_TIER, DQ_OWNER), classification scan, lineage query |
| **Key concept** | Quality IS governance: tags + classification + lineage + access history work together |
| **Prerequisite** | Module 4 (Gold tables with data) |
| **Checkpoint** | 7+ tags on DIM_CUSTOMER, 3 PII-tagged columns identified |

---

## Module 7: Alerts

| | |
|---|---|
| **Duration** | 45 min |
| **Role** | CORP_DQ_ADMIN |
| **Domain** | All (automation) |
| **What you build** | Email alert on expectation failures, sweep log table, sweep procedure, hourly scheduled task |
| **Key concept** | Complete lifecycle: 6 automated steps (land -> DMF -> expect -> alert -> email) before human acts |
| **Prerequisite** | Modules 4+6 (expectations + tags configured) |
| **Checkpoint** | Alert RESUMED, Task RESUMED, sweep log has entries from manual run |

---

## Module 8: Dashboard (Choose One Variant)

| | |
|---|---|
| **Duration** | 45 min |
| **Role** | CORP_DQ_ADMIN |
| **Domain** | Reporting |
| **Variants** | 8A: Native SQL tiles + Power BI guide / 8B: Python matplotlib / 8C: Streamlit SiS app |
| **What you build** | 4 DQ reporting views (flat results, scorecard, trend, executive summary) + visualization |
| **Key concept** | Same DQ data, multiple consumption patterns for different personas |
| **Prerequisite** | Module 7 (all DMFs running, expectations evaluated) |
| **Checkpoint** | All 4 views return data |

---

## Module 9: Teardown

| | |
|---|---|
| **Duration** | 5 min |
| **Role** | ACCOUNTADMIN |
| **Domain** | Cleanup |
| **What you do** | Suspend alerts/tasks, DROP database + roles + integration |
| **Checkpoint** | `SHOW DATABASES LIKE 'CORP_DWH'` returns empty |
