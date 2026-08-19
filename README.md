# Data Quality Monitoring with Snowflake

![Snowflake](https://img.shields.io/badge/Snowflake-Enterprise-29B5E8?logo=snowflake&logoColor=white)
![dbt](https://img.shields.io/badge/dbt-in_Snowflake-FF694B?logo=dbt&logoColor=white)
![Cortex AI](https://img.shields.io/badge/Cortex_AI-Powered-9B59B6)
![License](https://img.shields.io/badge/License-Apache_2.0-green)
![Modules](https://img.shields.io/badge/Modules-15-blue)

Build a **production-ready data quality monitoring framework** using only native Snowflake capabilities. No external tools, no additional infrastructure, no ongoing maintenance -- just Snowflake.

## What You Will Build

A complete DQ lifecycle from raw data landing to executive dashboard:

- **Data Metric Functions (DMFs)** -- system and custom checks on every layer
- **Dynamic Tables** -- auto-refreshing Silver layer (RAW to Silver)
- **dbt in Snowflake** -- governed Gold layer with tests (Silver to Gold)
- **Rules Catalog** -- self-service rule management with auto-provisioning
- **Expectations** -- automated pass/fail verdicts and cross-reference integrity
- **Cortex AI** -- natural language rule parsing, bulk table analysis, anomaly detection
- **Horizon Governance** -- tags, classification, lineage integration
- **Alerts & Dashboards** -- email notifications, sweep logs, BI-ready views

## Workshop Duration

| Track | Duration | Modules | Best For |
|-------|----------|---------|----------|
| **Half Day** | 4 hours | 0, 0B, 1, 1B, 2, 3 | Quick enablement -- core DQ framework |
| **Standard** | 6 hours | + 4, 4B, 5 | Full detection + remediation + AI |
| **Full Day** | 8 hours | All (demo 5+6) | Complete enterprise framework |
| **Extended** | 2 days | All hands-on | Deep-dive with exercises + discussion |

**Detailed timing (all hands-on, no shortcuts):**

| Module | Topic | Duration | Cumulative |
|--------|-------|----------|-----------|
| 0 | Environment Setup | 20 min | 0:20 |
| 0B | Dynamic Tables + dbt in Snowflake | 90 min | 1:50 |
| 1 | Raw Layer DQ (System DMFs) | 45 min | 2:35 |
| 1B | DMF Cost Management | 20 min | 2:55 |
| 2 | Silver Layer DQ (Custom DMFs) | 60 min | 3:55 |
| 3 | Gold Rules Catalog + Consistency | 60 min | 4:55 |
| 4 | Expectations + Cross-Reference Integrity | 45 min | 5:40 |
| 4B | Record Investigation + Remediation | 45 min | 6:25 |
| 5 | AI/ML-Powered DQ (Cortex AI) | 75 min | 7:40 |
| 6 | Governance (Horizon Integration) | 45 min | 8:25 |
| 7 | Alerts + Scheduled Monitoring | 45 min | 9:10 |
| 8 | Dashboard (choose 1 of 3 variants) | 45 min | 9:55 |
| 9 | Teardown | 5 min | 10:00 |
| | **Total instruction time** | **10 hours** | |
| | + Breaks (3x15 min) + Lunch (45 min) | +1:30 | **11:30** |

## Architecture

```
Source Systems          Bronze              Silver                 Gold                  DQ Layer
+-----------+       +----------+       +----------------+     +---------------+     +----------------+
| SAP ERP   |------>| STG_ERP  |       |                |     |               |     | RULES_CATALOG  |
| Salesforce|------>| STG_CRM  |--DT-->| INT_CUSTOMERS  |--+  | DIM_CUSTOMER  |     | DQ_ISSUES_LOG  |
| Gov Portal|------>| STG_GOV  |       | INT_TRANS      |  |  | FACT_TRANS    |     | DQ_SWEEP_LOG   |
| Bank Feed |------>| STG_TXN  |       +----------------+  |  +---------------+     +----------------+
+-----------+       +----------+        (auto-refresh)     |         ^                      |
                         |                                 |    snow dbt deploy         DMFs + Expectations
                    System DMFs                       Custom DMFs     |                       |
                    (Module 1)                        (Module 2)      +--- dbt tests ---------+
                                                                          (build-time)    (continuous)
```

## Quick Start

```bash
# 1. Clone
git clone https://github.com/mcharni/snowflake-data-quality-monitoring-hol.git
cd snowflake-data-quality-monitoring-hol

# 2. Setup Snowflake (requires ACCOUNTADMIN)
# Upload notebooks/0_SETUP.ipynb to Snowflake Notebooks and execute
# OR: snow sql -f scripts/setup_only.sql

# 3. Deploy dbt project
cd dbt/corp_dq_gold
snow dbt deploy CORP_DQ_GOLD --source . --database CORP_DWH --schema GOLD

# 4. Upload all notebooks to Snowflake Notebooks workspace

# 5. Execute in order: 0 -> 0B -> 1 -> 1B -> 2 -> 3 -> 4 -> 4B -> 5 -> 6 -> 7 -> 8 -> 9
```

> **First time?** See [guide/PREREQUISITES.md](guide/PREREQUISITES.md) for detailed setup: trial account, CLI install, connection config, notebook import.

## What Makes This Workshop Unique

| Feature | This Workshop | Typical DQ Workshops |
|---------|--------------|---------------------|
| Tools required | Snowflake only | Great Expectations + Airflow + dbt Cloud + ... |
| Infrastructure | Zero (serverless DMFs) | Kubernetes, schedulers, external DBs |
| AI-powered | Cortex AI for rule discovery | Manual rule writing only |
| Governance | Native Horizon integration | Separate catalog tool |
| Cost visibility | Built-in (Module 1B) | Rarely addressed |
| Remediation workflow | Full lifecycle (detect -> log -> quarantine -> resolve) | Usually just detection |
| Real dbt | Deployed in Snowflake (`EXECUTE DBT PROJECT`) | External dbt CLI |

## Who Is This For

- **SI Partners** implementing DQ for enterprise customers
- **Snowflake SEs** running customer workshops and demos
- **Data Engineers** building quality frameworks on Snowflake
- **Data Stewards** learning self-service rule management
- **Analytics Engineers** combining dbt tests with continuous DMF monitoring

## DQ Domains Covered

| Domain | Question | Lab Example |
|--------|----------|-------------|
| Accuracy | Correct format? | National ID `98765` too short (need 10 digits) |
| Completeness | Fields filled? | 3 CRM records with NULL National ID |
| Uniqueness | Duplicates? | Abdullah in both ERP and CRM |
| Freshness | Up to date? | Transaction 3 days stale (SLA: 2 hours) |
| Validity | Allowed values? | City not in reference list |
| Volume | Enough data? | ERP feed drops from 1000 to 5 rows |
| Consistency | Fields agree? | ERP customer missing mandatory IBAN |

## Repository Structure

```
├── notebooks/              # 15 Snowflake Notebooks (.ipynb)
├── dbt/corp_dq_gold/       # Real dbt project (deploy via snow CLI)
├── guide/
│   ├── STUDENT_GUIDE.html  # Self-contained visual guide
│   ├── PREREQUISITES.md    # Setup instructions (trial, CLI, workspace)
│   ├── WORKSHOP_CARDS.md   # One-page summary per module
│   └── LAB_MAP.md          # Flow diagram + learning paths
├── facilitator/
│   └── FACILITATOR_NOTES.md
├── scripts/
│   ├── setup_only.sql      # Quick setup (no notebook needed)
│   ├── teardown.sql        # Quick cleanup
│   └── validate_notebooks.py
├── .github/workflows/validate.yml
├── .gitignore
├── LICENSE (Apache 2.0)
└── README.md
```

## Publishing & Contributing

**Repository:** [github.com/mcharni/snowflake-data-quality-monitoring-hol](https://github.com/mcharni/snowflake-data-quality-monitoring-hol)

Contributions welcome. To contribute:
1. Fork the repo
2. Create a feature branch
3. Submit a PR with description of changes

## Keywords

`snowflake` `data-quality` `data-metric-functions` `dmf` `dbt` `dynamic-tables` `cortex-ai` `data-governance` `horizon` `hands-on-lab` `workshop` `enterprise` `monitoring` `expectations` `alerts`

## License

Apache 2.0. See [LICENSE](LICENSE).
