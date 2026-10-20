# Your Data Quality Stack Is Six Tools Too Many

*Snowflake already ships Data Metric Functions, Dynamic Tables, Cortex AI, Horizon, native alerts and per-table DQ cost history. I built a 15-notebook lab to see how far you get with just those.*

This story was written with the assistance of an AI writing program (Snowflake Cortex Code). I reviewed it, and I checked every number and code sample against the lab and a test account.

![Cover](diagrams/dq-00-cover.png)
*Cover image generated with Gemini.*

**Reading Time:** 9 minutes
**Difficulty:** Intermediate
**Prerequisites:** A Snowflake account on Enterprise Edition (a free trial works)
**Coffee Required:** A full pot. You're about to question your whole DQ stack.

---

> **What we're building:** a data quality monitoring framework that uses only native Snowflake features. No extra tools, no extra infrastructure. It goes from raw data landing to an executive dashboard in 15 hands-on notebooks.

---

## Six tools to answer one question

A lot of the data quality setups I see look something like this:

- Airflow to schedule the quality checks
- Great Expectations for rule definitions
- A separate metadata catalog (Atlan, DataHub, OpenMetadata)
- dbt tests for the transformation layer
- A custom Slack or email integration for alerts
- A BI tool for the dashboard nobody opens after week two

That's six systems to answer one question: *can I trust this data?*

Each one is a place where things can break. The Airflow DAG fails on a Friday. The expectation suite drifts away from the schema. The catalog shows old lineage. The dbt tests pass and the dashboard still shows bad numbers. And the alert channel gets so noisy that people mute it.

## What Snowflake already ships for data quality

Snowflake has Data Metric Functions (DMFs): SQL functions that measure something about a table, like a null count or a format violation count, and run on a schedule you set. Many teams I talk to have tried ROW_COUNT once and stopped there. That's like buying a sports car and only using the cup holder.

Here's how the pieces map:

| Capability | Typical external tool | Snowflake native |
|-----------|---------------|-----------------|
| Rule definition | Great Expectations suite | `CREATE DATA METRIC FUNCTION` (SQL) |
| Scheduling | Airflow or cron | `TRIGGER_ON_CHANGES` or a cron schedule on the table |
| Pass/fail verdicts | Custom code | Expectations on a DMF (`VALUE = 0`) |
| Metadata | Separate catalog | `INFORMATION_SCHEMA` + Horizon tags |
| Alerting | Custom integration | `CREATE ALERT` + `SYSTEM$SEND_EMAIL` |
| Cost visibility | Usually not built in | `ACCOUNT_USAGE.DATA_QUALITY_MONITORING_USAGE_HISTORY` |
| Lineage | Separate tool | `ACCOUNT_USAGE.OBJECT_DEPENDENCIES` |

The cost row is the one people notice. `DATA_QUALITY_MONITORING_USAGE_HISTORY` shows the credits DQ monitoring used per table, per hour. It doesn't break the cost down per DMF, but per-table cost is already more than most external setups report.

## What the lab builds

The lab starts from an empty Snowflake account and ends with a working DQ framework. It's not a "hello world" with ROW_COUNT. It includes:

- A medallion architecture (RAW, Silver, Gold) fed by 4 source systems
- Dynamic Tables for the Silver layer
- dbt for the Gold layer, deployed with `snow dbt deploy` and run inside Snowflake with `EXECUTE DBT PROJECT`
- 20 custom DMFs plus system DMFs across all three layers
- A rules catalog table that a stored procedure turns into DMFs (for regex, range and allowed-value rules)
- Cortex AI that suggests draft rules for a table
- Z-score anomaly detection on transaction amounts
- A remediation workflow: log, quarantine, resolve
- Tags, classification and lineage with Snowflake Horizon
- Email alerts and an hourly sweep
- Three dashboard options (SQL-only, Python, Streamlit)

The scenario is a fictional diversified holding company with four sources: ERP, CRM, a government portal and a bank feed. There are 115 records with quality issues I seeded on purpose: NULL identifiers, duplicates across sources, stale feeds, invalid National IDs and outlier amounts. The data uses Saudi formats (10-digit National ID, `SA` IBAN, `+966` phones). If you work elsewhere, swap the regex patterns for your country's formats. The framework stays the same.

## Hourly cron runs 12x more checks than a twice-a-day table needs

### The common setup: one schedule for everything

Many teams put the same cron schedule on every table. Every table gets checked every hour, whether it changed or not.

```sql
-- One schedule for everything: 24 evaluations a day
ALTER TABLE STG_TRANSACTIONS
SET DATA_METRIC_SCHEDULE = 'USING CRON 0 * * * * UTC';
```

This works. But if the table only changes twice a day, you run 24 evaluations where 2 would do. That's 12x more checks than the data needs. I'm counting evaluations here, not measured credits. The real cost depends on table size and how many DMFs are attached.

### A better setup: schedule by business impact

```sql
-- TIER 1: mission-critical, check on every change
ALTER TABLE STG_TRANSACTIONS
SET DATA_METRIC_SCHEDULE = 'TRIGGER_ON_CHANGES';

-- TIER 2: important but not urgent, check twice a day
ALTER TABLE STG_CUSTOMERS_CRM
SET DATA_METRIC_SCHEDULE = 'USING CRON 0 6,18 * * * UTC';

-- TIER 3: low priority, check weekly
ALTER TABLE STG_GOV_PORTAL
SET DATA_METRIC_SCHEDULE = 'USING CRON 0 6 * * 1 UTC';
```

The lab stores the tier as a Horizon tag (`SLA_TIER`) and maps each tier to a schedule. Tier 1 tables run on change because a late detection is expensive. Tier 3 tables run weekly because checking hourly costs more than finding the problem a few days late.

Module 1B walks through this with the credit numbers from `DATA_QUALITY_MONITORING_USAGE_HISTORY`. Note that this view lags by a few hours, so run 1B near the end of the lab.

## Four phases, 15 notebooks

The 15 notebooks fall into four phases. Each phase builds on the one before.

**Phase 1: Foundation (Modules 0, 0B).** Build the medallion architecture. Load four source tables with 115 messy records. Dynamic Tables refresh the Silver layer, and dbt builds the Gold layer. Don't fix the data. Fix the monitoring.

**Phase 2: Detection (Modules 1, 1B, 2, 3).** Attach system DMFs (ROW_COUNT, FRESHNESS, NULL_COUNT, BLANK_COUNT) to the RAW tables. Then write custom DMFs for business rules at Silver and Gold: National ID format, IBAN format, phone format and duplicates. Module 3 adds a rules catalog. You describe a rule as a row in a table, and a stored procedure creates and attaches the DMF. Module 1B looks at what all of this costs.

**Phase 3: Action (Modules 4, 4B, 5).** Turn metrics into decisions with expectations: `VALUE = 0` passes, anything else fails. Log every failure, quarantine the critical ones and resolve them with a reason. Then ask Cortex AI to draft rules, and flag outlier amounts with a z-score DMF.

**Phase 4: Operations (Modules 6, 7, 8, 9).** Tag PII columns with Horizon and run classification. Set up an email alert that fires when a check fails. Schedule an hourly sweep. Build a dashboard in SQL, Python or Streamlit. Then remove everything with one teardown script.

## Cortex AI writes the first draft of your rules

Module 5 is where the lab goes past detection. Instead of writing every rule by hand, you ask Cortex AI for suggestions:

```sql
CALL CORP_DWH.DQ.AI_SUGGEST_RULES('GOLD.FACT_TRANSACTIONS');
```

The procedure:

1. Reads the table's column names and data types from `INFORMATION_SCHEMA.COLUMNS`
2. Sends them to `claude-haiku-4-5` with a prompt asking for exactly 3 rules as JSON
3. Inserts each suggestion into `RULES_CATALOG` with `IS_ACTIVE = FALSE`
4. Inserts a placeholder row if the JSON doesn't parse, so the call never fails silently

The AI doesn't replace your data steward. It gives them a starting point. Every suggestion lands inactive, and a person approves or rejects it.

There's a trade-off to know about. The procedure sends only column names and types, not sample values. That keeps customer data out of the prompt, but it also means the AI can't see the actual patterns in the data. Its suggestions come from what the column names suggest. The output also changes between runs, so treat it as a draft every time.

## Detection is step 1 of 10

Most DQ workshops stop at detection. Run a check, see a failure, done.

This lab covers the full loop:

1. **Detect** with DMFs on every layer
2. **Decide** with expectations (pass or fail)
3. **Log** to `DQ_ISSUES_LOG` with severity and owner
4. **Alert** by email, checked every 5 minutes
5. **Investigate** with drill-down queries
6. **Remediate** by quarantining and resolving
7. **Report** on an executive dashboard
8. **Govern** with tags, classification and lineage
9. **Optimize** with cost analysis and tiered schedules
10. **Automate** with AI-drafted rules and catalog-driven DMFs

Detection without remediation is just expensive observation.

## When this lab is worth your time, and when it isn't

I built it for SI partners who implement data quality on Snowflake for enterprise customers. It's also useful if you:

- Are deciding between native DQ in Snowflake and an external tool
- Want to use DMFs beyond ROW_COUNT
- Need a reference design for DQ monitoring in production
- Want to see Dynamic Tables, dbt in Snowflake, Cortex AI and Horizon working in one project

It's less useful if most of your data lives outside Snowflake. DMFs only check Snowflake tables. If you already run a tool like Great Expectations across several platforms and it works, adding native DMFs means running two systems instead of one.

On cost: my full test runs used about 1.4 credits on an X-Small warehouse, plus well under 0.01 credits of DMF serverless compute. Cortex AI calls are billed separately. A student working at their own pace will idle more, but the lab warehouse auto-suspends after 60 seconds.

I tested the lab end to end on an Enterprise account and, separately, on a trial account with Enterprise Edition. Both work.

## Run Module 0 in ten minutes

The lab is open source (Apache 2.0). The first ten minutes look like this:

```bash
# 1. Get the lab
git clone https://github.com/mcharni76/snowflake-data-quality-monitoring-hol.git
cd snowflake-data-quality-monitoring-hol

# 2. Connect the Snowflake CLI
snow connection add   # name: dq-lab, role: ACCOUNTADMIN
snow connection test

# 3. Upload the notebooks to Snowsight Workspaces and run Module 0
```

After Module 0 you have a database with 115 records across 4 source tables, two roles and a warehouse. After Module 3, about 20 DMFs run automatically. After Module 7, a failing check sends you an email. Each notebook has checkpoints that tell you if you're on track.

**Repository:** [github.com/mcharni76/snowflake-data-quality-monitoring-hol](https://github.com/mcharni76/snowflake-data-quality-monitoring-hol)

---

*About the Author: [Marawen Charni](https://www.linkedin.com/in/mcharni) is a Senior Partner Solutions Engineer at Snowflake, based in the Middle East. He believes the best data quality framework is the one your team doesn't need a separate vendor to maintain.*

*Follow on Medium: [@marawen.cherni](https://medium.com/@marawen.cherni)*

---

### A Note on How This Article Came to Be

> **Figures:** Generated with **Gemini** in hand-drawn sketch style.
> **Content:** Drafted with **Snowflake Cortex Code** and reviewed by me.
> **Testing:** I ran every notebook end to end on a Snowflake Enterprise account and on a trial account before publishing.
