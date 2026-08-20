# Prerequisites Guide

Step-by-step instructions to get ready for the Data Quality Monitoring Hands-On Lab.

Complete these steps **before** the workshop day.

---

## Step 0: Get the Lab Materials

Clone the repository to your local machine:

```bash
git clone https://github.com/mcharni76/snowflake-data-quality-monitoring-hol.git
cd snowflake-data-quality-monitoring-hol
```

> **No git?** Download the ZIP from [GitHub](https://github.com/mcharni76/snowflake-data-quality-monitoring-hol/archive/refs/heads/main.zip) and extract it.

You will need the `notebooks/` folder (15 `.ipynb` files to upload) and `dbt/corp_dq_gold/` (for Module 0B).

---

## Appendix A: Create a Snowflake Trial Account

1. Go to [signup.snowflake.com](https://signup.snowflake.com/)
2. Fill in your name, email, and company
3. Choose these options:
   - **Edition:** Enterprise (required for Data Metric Functions)
   - **Cloud Provider:** Any (AWS, Azure, or GCP)
   - **Region:** Choose one close to you. For KSA workshops, select **GCP - Middle East (Dammam)** if available, or any region (Cortex AI uses cross-region inference)
4. Click **Start Free Trial**
5. Check your email for the activation link and set your password
6. Log in at your account URL (e.g., `https://abc12345.snowflakecomputing.com`)

Your trial includes:
- 30 days free
- $400 in credits
- Enterprise Edition features (DMFs, Dynamic Tables, Cortex AI)
- ACCOUNTADMIN role (full access)

> **Important:** Note your **account identifier** (e.g., `abc12345`) and **account URL**. You will need these for the Snowflake CLI connection.

---

## Appendix B: Set Up a Snowflake Notebook Workspace

Snowflake Notebooks run inside **Workspaces** in Snowsight (the Snowflake web UI). No local Jupyter installation needed.

> **What is a Workspace?** A Workspace is a file-based development environment in Snowsight where you can organize notebooks, SQL files, and Python files into folders. Each user gets a personal "My Workspace" automatically.

### Import Lab Notebooks into Your Workspace

1. Log into Snowsight at your account URL
2. Select **Workspaces** from the left sidebar (or navigate to it from the top navigation)
3. In your default workspace ("My Workspace"), create a folder for the lab:
   - Click the **+** button in the file explorer (left panel) and select **New Folder**
   - Name it `DQ_Lab`
4. Upload all 15 notebooks into the folder:
   - Click the **+** button again and select **Upload File**
   - Select all `.ipynb` files from the `notebooks/` folder (you can multi-select)
   - The files appear in your workspace file explorer
5. Open `0_SETUP.ipynb` by clicking on it — it opens as a notebook tab in the editor
6. Set the execution context using the **role and warehouse picker** (top-left of the notebook editor):
   - **Role:** ACCOUNTADMIN (for Module 0 only)
   - **Warehouse:** COMPUTE_WH (or create one: `CREATE WAREHOUSE COMPUTE_WH WAREHOUSE_SIZE = 'XSMALL'`)

### Tips

- Upload all 15 notebooks at the start so you can switch between them using the file explorer
- After Module 0, switch the notebook role to `CORP_DQ_ADMIN` (top-left role picker)
- Each notebook is independent — you can close and reopen without losing state (objects persist in Snowflake)
- The notebook kernel stays active even if you navigate away or close your browser
- Use the **minimap** (right side) for quick navigation between cells within a notebook

---

## Appendix C: Install the Snowflake CLI (`snow`)

The Snowflake CLI is required for deploying the dbt project in Module 0B. Install it on your local machine.

### macOS

```bash
# Option 1: Homebrew (recommended)
brew install snowflake-cli

# Option 2: pip
pip install snowflake-cli
```

### Windows

```bash
# Option 1: pip (requires Python 3.8+)
pip install snowflake-cli

# Option 2: Download installer from Snowflake docs
# https://docs.snowflake.com/en/developer-guide/snowflake-cli/installation
```

### Linux

```bash
pip install snowflake-cli
```

### Verify Installation

```bash
snow --version
# Expected: Snowflake CLI X.X.X
```

---

## Appendix D: Configure CLI Connection to Your Trial Account

The CLI needs a connection profile to authenticate with your Snowflake trial.

### Step 1: Create the connection

```bash
snow connection add
```

Follow the prompts:

| Prompt | Value |
|--------|-------|
| Connection name | `default` |
| Account identifier | Your account ID (e.g., `abc12345` or `orgname-accountname`) |
| User | Your username (the email you signed up with) |
| Password | Your password |
| Role | `ACCOUNTADMIN` |
| Warehouse | `COMPUTE_WH` |
| Database | `CORP_DWH` |
| Schema | `GOLD` |

### Step 2: Set as default connection

```bash
snow connection set-default default
```

### Step 3: Test the connection

```bash
snow connection test
```

Expected output:
```
Connection test successful.
Role:      ACCOUNTADMIN
Warehouse: COMPUTE_WH
Database:  CORP_DWH
```

### Step 4: Verify dbt commands are available

```bash
# Confirm the dbt subcommand is available
snow dbt --help
```

> **Note:** You will deploy the dbt project during the workshop (Module 0B). Do NOT run `snow dbt deploy` yet -- the database must be created first by Module 0.

### Troubleshooting

| Issue | Fix |
|-------|-----|
| `snow: command not found` | Restart terminal, or check `pip show snowflake-cli` |
| `Authentication failed` | Check account ID format. Try `orgname-accountname` format. |
| `Database CORP_DWH does not exist` | Run Module 0 (0_SETUP.ipynb) first to create the database |
| `Permission denied on GOLD schema` | Ensure you ran Module 0 setup which grants privileges |
| `Connection timeout` | Check your network/VPN. Snowflake needs outbound HTTPS (443). |

---

## Checklist (Complete Before Workshop Day)

- [ ] Snowflake trial account created (Enterprise Edition)
- [ ] Can log into Snowsight web UI
- [ ] COMPUTE_WH warehouse exists (or will be created in Module 0)
- [ ] Snowflake CLI installed (`snow --version` works)
- [ ] CLI connection configured and tested (`snow connection test` passes)
- [ ] Lab notebooks downloaded from the repository
- [ ] At least `0_SETUP.ipynb` imported into Snowflake Notebooks

**Estimated time:** 15-20 minutes to complete all prerequisites.
