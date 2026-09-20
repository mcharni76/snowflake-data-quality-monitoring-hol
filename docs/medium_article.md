# Stop Building Data Quality Frameworks from Scratch

*You don't need Great Expectations, Airflow, and a separate metadata catalog. You need 15 Snowflake notebooks and an afternoon.*

![Cover](diagrams/dq-00-cover.png)

**Reading Time:** 12 minutes
**Difficulty:** Intermediate
**Prerequisites:** A Snowflake account (Enterprise edition or trial)
**Coffee Required:** A full pot. You're about to rethink your entire DQ stack.

---

> **What we're building:** A production-ready data quality monitoring framework using only native Snowflake capabilities. No external tools, no additional infrastructure, no ongoing maintenance. From raw data landing to executive dashboard in 15 hands-on modules.

---

## The Tool Sprawl Problem

Every enterprise data team I work with has the same architecture diagram on their wall. It looks something like this:

- Airflow for scheduling quality checks
- Great Expectations for rule definitions
- A separate metadata catalog (Atlan, DataHub, OpenMetadata)
- dbt tests for transformation-layer validation
- A custom Slack/email integration for alerting
- A BI tool for the dashboard nobody looks at

That's six systems to answer one question: *can I trust this data?*

And here's what actually happens. The Airflow DAG breaks on a Friday. The Great Expectations suite drifts out of sync with the schema. The metadata catalog shows lineage from three months ago. The dbt tests pass but the dashboard still shows garbage. And the Slack channel has so many alerts that everyone muted it in week two.

I've seen this pattern across dozens of enterprise deployments in the Middle East, from Saudi banks to government agencies to holding companies. The tools are different, the outcome is the same: DQ monitoring that works in the demo but fails in production.

## What If the Platform Already Had Everything?

Snowflake shipped Data Metric Functions (DMFs) as a native feature. Most teams I talk to either haven't heard of them or used ROW_COUNT once and moved on. That's like buying a sports car and only using the cup holder.

Here's what DMFs actually give you, out of the box:

| Capability | External Tool | Snowflake Native |
|-----------|---------------|-----------------|
| Rule definition | Great Expectations YAML | SQL function (CREATE DATA METRIC FUNCTION) |
| Scheduling | Airflow/cron | TRIGGER_ON_CHANGES or cron, built-in |
| Metadata | Separate catalog | INFORMATION_SCHEMA + Horizon tags |
| Alerting | Custom integration | Native ALERT + SYSTEM$SEND_EMAIL |
| Cost visibility | You don't have this | ACCOUNT_USAGE.DATA_QUALITY_MONITORING_USAGE_HISTORY |
| Lineage | Separate tool | OBJECT_DEPENDENCIES (automatic) |

That last row is the one that usually gets people. With DMFs, you don't just get quality checks. You get cost visibility per table, per DMF, per day. Try getting that from Great Expectations.

## The Lab: 10 Hours, Zero External Dependencies

I built a hands-on lab that takes you from an empty Snowflake account to a complete DQ monitoring framework. Not a toy. Not a "hello world" with ROW_COUNT. A real framework with:

- A medallion architecture (RAW, Silver, Gold) processing data from 4 source systems
- Dynamic Tables for the Silver layer (auto-refreshing, declarative)
- dbt in Snowflake for the Gold layer (deployed as a native object, not a CLI tool)
- 20+ Data Metric Functions across all three layers
- A self-service rules catalog that auto-provisions DMFs from business-readable definitions
- Cortex AI that reads your table and suggests quality rules in plain English
- Z-score anomaly detection that flags statistical outliers
- A full remediation workflow (detect, log, quarantine, resolve)
- Tags, classification, and lineage via Snowflake Horizon
- Email alerts and a scheduled sweep that runs hourly
- Three dashboard options (SQL-only, Python/plotly, Streamlit)

The scenario is a Saudi diversified holding company. Four source systems (ERP, CRM, Government Portal, Bank Feed), 115 records with intentionally seeded quality issues, and a CFO who wants a single scorecard. It's fictional, but the problems are real: NULL identifiers, cross-source duplicates, stale feeds, invalid National IDs, and transaction outliers.

## The "Wrong Way, Then Right Way" Pattern

### Wrong: One-size-fits-all scheduling

Most teams slap a cron schedule on every quality check. Every table gets checked every hour, whether it changed or not.

```sql
-- The expensive way: check every hour regardless
ALTER TABLE STG_TRANSACTIONS
SET DATA_METRIC_SCHEDULE = 'USING CRON 0 * * * * UTC';
```

This works. It's also 12x more expensive than it needs to be for tables that only change twice a day.

### Right: Tiered monitoring based on business impact

```sql
-- TIER 1: Mission-critical, check on every change
ALTER TABLE STG_TRANSACTIONS
SET DATA_METRIC_SCHEDULE = 'TRIGGER_ON_CHANGES';

-- TIER 2: Important but not urgent, check twice daily  
ALTER TABLE STG_CUSTOMERS_CRM
SET DATA_METRIC_SCHEDULE = 'USING CRON 0 6,18 * * * UTC';

-- TIER 3: Low-priority, check weekly
ALTER TABLE STG_GOV_PORTAL
SET DATA_METRIC_SCHEDULE = 'USING CRON 0 6 * * 1 UTC';
```

Map your SLA tier (which you define with Horizon tags) to a monitoring schedule. Tier 1 tables get `TRIGGER_ON_CHANGES` because you need to know immediately. Tier 3 tables get a weekly check because the cost of checking hourly exceeds the cost of a late detection.

The lab walks through this cost analysis in Module 1B, with actual credit consumption numbers from `ACCOUNT_USAGE.DATA_QUALITY_MONITORING_USAGE_HISTORY`.

## The Modules

The lab is structured as 15 notebooks that build on each other:

| # | Module | What You Build | Key Insight |
|---|--------|---------------|-------------|
| 0 | Setup | Medallion architecture, 4 source tables, 115 seeded records | The quality issues are intentional. Don't fix the data. Fix the monitoring. |
| 0B | Pipeline | Dynamic Tables (Silver) + dbt in Snowflake (Gold) | DTs are declarative pipelines. No DAG. No scheduling. Just SQL and a target lag. |
| 1 | Raw Layer DQ | System DMFs: ROW_COUNT, FRESHNESS, NULL_COUNT, BLANK_COUNT | NULL and blank are different. Most source systems use empty strings, not NULL. |
| 1B | Cost Analysis | DMF credit consumption, tiered scheduling, cost projection | The cheapest DMF is the one you don't need. Start daily, promote to trigger. |
| 2 | Silver Layer DQ | Custom DMFs: National ID, IBAN, phone format, duplicates | Saudi-specific regex: `^[12][0-9]{9}$` for National ID, `^SA[0-9A-Za-z]{22}$` for IBAN. |
| 3 | Gold Rules Catalog | Self-service rule definitions, auto-provisioning procedure | Business users define rules in a table. A stored procedure generates DMFs automatically. |
| 4 | Expectations | Pass/fail verdicts, cross-reference integrity, data loss detection | Expectations turn metrics into decisions. A NULL_COUNT of 10 is a number. "10 > 0 = FAIL" is a verdict. |
| 4B | Remediation | Issue logging, quarantine, resolution workflow | Detection without remediation is just expensive observation. |
| 5 | AI/ML DQ | Cortex AI rule suggestions, z-score anomaly detection | Tell the AI: "analyze this table and suggest quality rules." It reads the schema, samples data, and proposes rules with SQL. |
| 6 | Governance | Tags, classification, lineage via Horizon | Tag a column as PII. Classify it automatically. See lineage from RAW to Gold. One platform. |
| 7 | Alerts | Email notifications, scheduled sweep, sweep log | Alerts fire on expectation failures. The sweep runs hourly and logs everything. |
| 8 | Dashboard | Three options: SQL-only, Python/plotly, Streamlit | Pick the one your team will actually maintain. |
| 9 | Teardown | Clean removal of all lab objects | One notebook, 30 seconds, zero residue. |

## The Part Nobody Talks About: AI-Powered Rule Discovery

Module 5 is where this lab diverges from every other DQ workshop I've seen.

Instead of manually writing rules for each column, you point Cortex AI at a table and ask it to suggest quality rules:

```sql
CALL DQ.AI_SUGGEST_RULES('CORP_DWH.GOLD.DIM_CUSTOMER');
```

The procedure:
1. Reads the table schema (column names, types)
2. Samples 50 rows of actual data
3. Sends both to Cortex AI with a prompt that asks for quality rules
4. Parses the JSON response into RULES_CATALOG rows
5. Handles parsing failures gracefully (no crash, just a log entry)

The AI doesn't replace your data steward. It gives your data steward a starting point. Instead of staring at a 40-column table and deciding where to begin, they review 10-15 AI-suggested rules and approve, reject, or modify each one.

In the lab, the AI correctly identifies that National IDs should be 10 digits starting with 1 or 2, that IBANs should follow the SA + 22 character pattern, and that transaction amounts should be positive. It also suggests rules you might not think of, like checking that email domains are valid or that phone numbers follow the +966 format.

## Who Should Run This Lab

I built this for SI partners who implement data quality for enterprise customers on Snowflake. But it's useful for anyone who:

- Is evaluating whether to build DQ monitoring natively in Snowflake or bolt on external tools
- Wants to understand DMFs beyond ROW_COUNT
- Needs a reference architecture for production DQ monitoring
- Wants to see how Dynamic Tables, dbt in Snowflake, Cortex AI, and Horizon work together in a single project

The lab runs on a trial account. Total compute cost is under $5 for the full 10-hour run.

## What's Different About This Workshop

Most DQ workshops teach you detection. Run a check. See a failure. Done.

This lab teaches the full lifecycle:

1. **Detect** it (DMFs on every layer)
2. **Decide** on it (Expectations: pass or fail?)
3. **Log** it (DQ_ISSUES_LOG with severity, owner, SLA)
4. **Alert** on it (email notification within minutes)
5. **Investigate** it (drill-down queries and root cause analysis)
6. **Remediate** it (quarantine, resolve, close the loop)
7. **Report** on it (executive dashboard with DQ scores)
8. **Govern** it (tags, classification, lineage)
9. **Optimize** it (cost analysis, tiered scheduling)
10. **Automate** it (AI suggests rules, procedures provision DMFs)

That's not a demo. That's a framework.

## Getting Started

The lab is open-source (Apache 2.0) and available on GitHub:

1. Clone or download the repository
2. Create a Snowflake trial account (or use an existing Enterprise account)
3. Upload the 15 notebooks to Snowflake Workspaces
4. Start with Module 0 and follow the numbered sequence

Each notebook is self-contained with explanations, code cells, verification checkpoints, quizzes, and a challenge section. You don't need to read documentation. Just run the cells and read the markdown.

**Repository:** [github.com/mcharni76/snowflake-data-quality-monitoring-hol](https://github.com/mcharni76/snowflake-data-quality-monitoring-hol)

---

*About the Author: [Marawen Charni](https://www.linkedin.com/in/mcharni) is a Solutions Engineer at Snowflake, based in the Middle East. He believes the best data quality framework is the one your team doesn't need a separate vendor to maintain.*

*Follow on Medium: [@marawen.cherni](https://medium.com/@marawen.cherni)*

---

### A Note on How This Article Came to Be

> **Figures:** Generated with **Gemini** in infographic style.
> **Content:** Assisted by **Snowflake Cortex Code**.
> **Experience:** Based on real enterprise DQ implementations across the Middle East (genericized and anonymized).
