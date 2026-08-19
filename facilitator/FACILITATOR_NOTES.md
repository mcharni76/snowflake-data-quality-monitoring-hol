# Facilitator Notes - Data Quality Monitoring with Snowflake

## Overview

**Duration:** Full day (~11 hours with all modules + breaks; see "Short on Time" below)
**Format:** Instructor-led, hands-on workshop
**Participants:** 4-12 (optimal: 6-8)
**Repository:** github.com/mcharni76/snowflake-data-quality-monitoring-hol
**Database:** CORP_DWH | **Roles:** CORP_DQ_ADMIN, CORP_DQ_STEWARD

---

## Pre-Workshop Setup (Send to Students 1 Week Before)

Share `guide/PREREQUISITES.md` with students. They need to complete:
1. Snowflake trial account (Enterprise Edition)
2. Import notebooks into Snowflake Notebooks workspace
3. Install `snow` CLI and configure connection
4. Test with `snow connection test`

**Facilitator pre-check:** Run `scripts/setup_only.sql` on a test account to confirm everything works. Deploy dbt project to validate.

---

## Timing Breakdown

| Module | Duration | Cumulative | Notes |
|--------|----------|-----------|-------|
| 0: Setup | 20 min | 0:20 | RAW data only, source system explanations |
| 0B: Data Pipeline | 90 min | 1:50 | Dynamic Tables (RAW->Silver) + dbt (Silver->Gold) |
| **Break** | 15 min | 2:05 | |
| 1: Raw Layer DQ | 45 min | 2:50 | System DMFs, first "aha" moment |
| 1B: DMF Costs | 20 min | 3:10 | Cost visibility, scheduling trade-offs |
| 2: Silver Custom DMFs | 60 min | 3:50 | Most hands-on coding |
| **Lunch** | 45 min | 4:35 | |
| 3: Gold Rules Catalog | 60 min | 5:35 | Consistency checks + auto-provisioning |
| 4: Expectations | 45 min | 6:20 | Cross-reference integrity |
| 4B: Remediation | 45 min | 7:05 | Issues log, quarantine, resolve |
| **Break** | 15 min | 7:20 | |
| 5: AI/ML | 75 min | 8:35 | NL parsing, bulk suggest, recommender |
| 6: Governance | 45 min | 9:20 | Tags, classification, lineage |
| 7: Alerts | 45 min | 10:05 | Full lifecycle closed |
| 8 (choose one): Dashboard | 45 min | 10:50 | Native/Python/Streamlit variant |
| 9: Teardown | 5 min | 10:55 | Optional cleanup |

---

## If You're Short on Time

**Half day (4h):** Modules 0, 0B, 1, 2, 3 (core pipeline + DQ)
**6 hours:** Add 4, 4B, 5 (expectations + AI)
**8 hours (realistic full day):** All modules, demo-only for 5+6, pick one M8 variant
**11 hours (all hands-on):** Every module fully hands-on -- requires 2 days or fast group
**Module 6 (Governance)** can be demo-only if pressed
**Module 5 (AI)** can be shortened to 45 min by skipping the capstone (5f)

---

## Source Systems (teach before Module 0)

| Source | System | Feed | Owner | Quality | Key Issue |
|--------|--------|------|-------|---------|-----------|
| ERP | SAP S/4HANA | Nightly CSV | Finance | High | Minor: spaces in IDs, varied phone formats |
| CRM | Salesforce | API sync/2h | Sales | Low | 50% NULL National IDs, duplicates with ERP |
| Gov Portal | GOSI/Absher | Monthly Excel | Compliance | Very Low | ALL National IDs invalid (OCR errors) |
| Bank | Core Banking | Daily SFTP | Treasury | Medium | String dates, amounts with commas/prefix |

---

## Key Talking Points

### Module 0B: Data Pipeline
- **Dynamic Tables:** "Set it and forget it -- auto-refreshes when source changes"
- **dbt in Snowflake:** "Real project deployed as a Snowflake object -- no external infra"
- **Prerequisite:** Students need `snow` CLI installed. Have them run `snow dbt deploy` BEFORE opening the notebook
- **Hybrid pattern:** "DT for Silver (fresh), dbt for Gold (governed) -- use BOTH"
- **dbt tests vs DMFs:** Build-time gate (dbt) vs continuous monitoring (DMFs) -- both have value

### Module 1: Raw Layer DQ
- "Don't wait until Gold to find problems -- catch them at the gate"
- BLANK_COUNT vs NULL_COUNT is the key insight

### Module 1B: DMF Costs
- "The cheapest DMF is the one you don't need"
- Cost formula: executions/day x 30 x credits/execution x $3
- TRIGGER_ON_CHANGES on high-frequency tables = bill shock (show 12x difference)
- Tiered monitoring pattern maps directly to SLA_TIER tags (Module 6)

### Module 2: Custom DMFs
- Saudi-specific validations resonate well with KSA partners
- Emphasize: DMFs are first-class Snowflake objects (grantable, auditable)

### Module 3: Rules Catalog
- "Stewards self-serve. No ticket to engineering needed."
- Consistency checks are the advanced "wow" moment

### Module 4B: Remediation
- "Detection without remediation is just noise"
- Quarantine pattern: flag, don't delete
- Issues have owners, SLAs, and audit trails

### Module 5: AI
- NL parsing: "Describe in English, AI extracts parameters"
- Bulk analysis + approve/reject = governance workflow
- System DMF recommender = zero tables go unmonitored

---

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Empty DQ results | DMFs haven't fired yet | Wait 1-2 min or touch table with UPDATE |
| "Insufficient privileges" | Wrong role | `USE ROLE CORP_DQ_ADMIN;` |
| Cortex AI error | Cross-region not enabled | Module 0 Step 3 |
| Dynamic Table not refreshing | Initial lag period | Wait up to TARGET_LAG duration |
| Dashboard view won't create | No DMF results yet | Run modules 1-4 first, then create views |
| dbt project not found | Student didn't deploy | Run: `snow dbt deploy CORP_DQ_GOLD --source dbt/corp_dq_gold --database CORP_DWH --schema GOLD` |
| "snow: command not found" | CLI not installed | Install: `pip install snowflake-cli` or `brew install snowflake-cli` |

---

## Post-Lab Discussion

1. "Where would you apply Raw Layer DQ first in your current platform?"
2. "DT or dbt for your Silver layer? What drives that decision?"
3. "What business rules exist as tribal knowledge that should go in a catalog?"
4. "How would you structure DQ ownership across teams?"
5. "What SLAs would you set for your critical data feeds?"

---

## Cleanup

```sql
USE ROLE ACCOUNTADMIN;
DROP DATABASE IF EXISTS CORP_DWH;
DROP ROLE IF EXISTS CORP_DQ_ADMIN;
DROP ROLE IF EXISTS CORP_DQ_STEWARD;
DROP INTEGRATION IF EXISTS CORP_DQ_ALERTS;
```
