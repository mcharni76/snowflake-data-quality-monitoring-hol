# START HERE - Student Quick Start

> **Welcome!** This is your single entry point. Follow the steps below in order.

---

## Before You Begin

| Requirement | Details |
|-------------|---------|
| **Snowflake Account** | Trial or Enterprise (30-day trial works) |
| **Snowflake CLI** | `brew install snowflake-cli` or `pip install snowflake-cli` |
| **Browser** | Chrome/Edge for Snowsight |
| **Time** | 4-10 hours depending on track (see below) |

---

## Step 1: Clone & Configure (5 min)

```bash
git clone https://github.com/mcharni76/snowflake-data-quality-monitoring-hol.git
cd snowflake-data-quality-monitoring-hol/hol

# Add your Snowflake connection
snow connection add
#   Connection name: dq-lab
#   Account: <your-account-id>  (e.g., ABCDEFG-XY12345)
#   User: <your-username>
#   Password: <your-password>
#   Role: ACCOUNTADMIN
#   Warehouse: DQ_LAB_WH (will be created in Module 0)

snow connection set-default dq-lab
snow connection test
```

---

## Step 2: Upload Notebooks (3 min)

1. Open [Snowsight](https://app.snowflake.com) in your browser
2. Go to **Projects > Notebooks** (left sidebar)
3. Click **Upload .ipynb file** (top-right)
4. Upload ALL `.ipynb` files from the `notebooks/` folder (multi-select)
5. Set database to any (will be overridden by notebook cells)

---

## Step 3: Execute in This Order

```
Module 0   -->  Environment Setup (ACCOUNTADMIN role)
Module 0B  -->  Data Pipeline: Dynamic Tables + dbt
Module 1   -->  Raw Layer DQ: System DMFs
Module 2   -->  Silver Layer DQ: Custom DMFs
Module 3   -->  Gold Layer: Rules Catalog
Module 4   -->  Expectations & Cross-Reference
Module 4B  -->  Record Investigation & Remediation
Module 5   -->  AI/ML-Powered DQ (Cortex AI)
Module 6   -->  Governance (Horizon)
Module 7   -->  Alerts & Monitoring
Module 1B  -->  DMF Cost Analysis (runs last - needs Account Usage lag)
Module 8   -->  Dashboard (choose A, B, or C)
Module 9   -->  Teardown (cleanup)
```

**Important:**
- After Module 0, switch role to **CORP_DQ_ADMIN** for all remaining modules
- Module 0B requires a terminal command (`snow dbt deploy`) - the notebook tells you when
- Module 1B is intentionally placed after Module 7 (requires 1-3h of Account Usage latency)
- Module 8: pick ONE variant (A = SQL charts, B = Python/matplotlib, C = Streamlit)

---

## Step 4: How to Run Each Notebook

1. Open the notebook in Snowsight
2. Set **Role** = `CORP_DQ_ADMIN` (top-left, except Module 0 uses ACCOUNTADMIN)
3. Set **Warehouse** = `DQ_LAB_WH` (top-left)
4. Run cells **top to bottom** (Shift+Enter or Run button)
5. After each code cell, compare your output to the **Expected result** block below it
6. At checkpoints, verify all checks show `[PASS]`

---

## Choose Your Track

| Track | Duration | Modules | Outcome |
|-------|----------|---------|---------|
| **Core** | 4 hours | 0, 0B, 1, 2, 3 | Build a working DQ framework |
| **Standard** | 6 hours | + 4, 4B, 5 | Add expectations + AI |
| **Full** | 8 hours | All modules | Complete enterprise solution |
| **Extended** | 2 days | All + exercises | Deep-dive with discussion |

---

## If Something Goes Wrong

| Problem | Solution |
|---------|----------|
| "Object does not exist" | Did you run Module 0 first? Check role is CORP_DQ_ADMIN |
| DMF results show 0 rows | Wait 1-2 minutes (async). Run the trigger cell, then re-query |
| dbt deploy fails | Run from terminal: `snow dbt deploy --project-dir dbt/corp_dq_gold --connection dq-lab` |
| Permission denied | Check you're using the right role (ACCOUNTADMIN for M0, CORP_DQ_ADMIN after) |
| Account Usage empty | Normal -- 1-3h latency. This is why Module 1B runs last |

---

## Reference Materials

| Document | Purpose |
|----------|---------|
| [PREREQUISITES.md](guide/PREREQUISITES.md) | Trial account signup, CLI install details |
| [STUDENT_GUIDE.md](guide/STUDENT_GUIDE.md) | DQ domains, SQL patterns, glossary |
| [WORKSHOP_CARDS.md](guide/WORKSHOP_CARDS.md) | One-page summary per module |
| [LAB_MAP.md](guide/LAB_MAP.md) | Visual flow diagram |
| [APPENDIX_DBT_DEVELOPMENT.md](guide/APPENDIX_DBT_DEVELOPMENT.md) | How the dbt project was built |

---

## Feedback

After completing the lab, please fill in the feedback form:
**[guide/DQ_HOL_Feedback_Form.xlsx](guide/DQ_HOL_Feedback_Form.xlsx)**

3 sheets:
1. **Module Feedback** -- rate each module (difficulty, clarity, usefulness)
2. **Enhancement Requests** -- bugs, gaps, ideas (free-form)
3. **Cohort Tracker** -- for your facilitator to track group progress

---

> **Questions?** Reach out to your workshop facilitator or open an issue on GitHub.
