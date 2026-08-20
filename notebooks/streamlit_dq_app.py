import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="DQ Monitor", page_icon="\U0001F6E1", layout="wide")
session = get_active_session()

st.title("\U0001F6E1 Data Quality Monitoring Dashboard")
st.caption("Real-time quality metrics for CORP_DWH | Powered by Snowflake DMFs")

# --- KPI Header ---
exec_df = session.sql("SELECT * FROM CORP_DWH.DQ.V_DQ_EXECUTIVE_SUMMARY").to_pandas()

if not exec_df.empty:
    health = float(exec_df["OVERALL_HEALTH_PCT"].iloc[0] or 0)
    total = int(exec_df["TOTAL_CHECKS"].iloc[0] or 0)
    passing = int(exec_df["CHECKS_PASSING"].iloc[0] or 0)
    failing = int(exec_df["CHECKS_FAILING"].iloc[0] or 0)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Overall Health", f"{health:.0f}%",
                delta="Healthy" if health >= 90 else "Degraded" if health >= 70 else "Critical",
                delta_color="normal" if health >= 90 else "off" if health >= 70 else "inverse")
    col2.metric("Total Checks", total)
    col3.metric("Passing", passing, delta=f"{passing}/{total}")
    col4.metric("Failing", failing, delta=f"-{failing}" if failing > 0 else "0",
                delta_color="inverse" if failing > 0 else "normal")
else:
    st.warning("No DQ results available yet. Run some DMF checks first (Modules 1-4).")
    st.stop()

st.divider()

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "\U0001F4CA Overview", "\U0001F4C8 Trend", "\U0001F6A8 Failures", "\U0001F4DD Rules Catalog", "\U0001F50D Drill-Down"
])

# === TAB 1: Overview (Charts) ===
with tab1:
    results_df = session.sql(
        "SELECT METRIC_NAME, COLUMN_CHECKED, METRIC_VALUE, STATUS, SEVERITY, RULE_TYPE "
        "FROM CORP_DWH.DQ.V_DQ_RESULTS_FLAT WHERE STATUS IN ('PASS', 'FAIL')"
    ).to_pandas()

    if results_df.empty:
        st.info("No results to visualize.")
    else:
        chart_col1, chart_col2 = st.columns(2)

        # Pass/Fail distribution (pie-like bar)
        with chart_col1:
            st.subheader("Pass/Fail Distribution")
            status_counts = results_df["STATUS"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            st.bar_chart(status_counts.set_index("Status"), color=["#29B5E8"])

        # Failures by severity
        with chart_col2:
            st.subheader("Failures by Severity")
            fails_sev = results_df[results_df["STATUS"] == "FAIL"]["SEVERITY"].value_counts().reset_index()
            fails_sev.columns = ["Severity", "Count"]
            if not fails_sev.empty:
                st.bar_chart(fails_sev.set_index("Severity"), color=["#FF6B6B"])
            else:
                st.success("No failures!")

        # Top violations
        st.subheader("Top Violations (by value)")
        top_violations = (
            results_df[results_df["METRIC_VALUE"] > 0]
            .nlargest(10, "METRIC_VALUE")[["METRIC_NAME", "COLUMN_CHECKED", "METRIC_VALUE", "SEVERITY"]]
        )
        if not top_violations.empty:
            st.bar_chart(
                top_violations.set_index("METRIC_NAME")["METRIC_VALUE"],
                color="#FF9800"
            )
        else:
            st.info("All metrics at zero.")

        # Health by table (progress bars)
        st.subheader("Health by Table")
        scorecard = session.sql("SELECT * FROM CORP_DWH.DQ.V_DQ_SCORECARD").to_pandas()
        if not scorecard.empty:
            for _, row in scorecard.iterrows():
                h = float(row["HEALTH_SCORE_PCT"] or 0)
                color = "normal" if h >= 90 else "off" if h >= 70 else "inverse"
                st.progress(h / 100, text=f"{row['TABLE_NAME']} — {h:.0f}% ({row['PASSED']}/{row['TOTAL_EXPECTATIONS']} passing)")
        else:
            st.info("No scorecard data.")

# === TAB 2: Trend (Line Chart) ===
with tab2:
    st.subheader("Quality Trend Over Time")
    trend_df = session.sql("""
        SELECT MEASUREMENT_HOUR,
            COUNT(CASE WHEN EXPECTATION_RESULT = 'MET' THEN 1 END) AS PASSING,
            COUNT(CASE WHEN EXPECTATION_RESULT = 'NOT_MET' THEN 1 END) AS FAILING
        FROM CORP_DWH.DQ.V_DQ_TREND
        GROUP BY MEASUREMENT_HOUR
        ORDER BY MEASUREMENT_HOUR
    """).to_pandas()

    if not trend_df.empty:
        trend_df = trend_df.set_index("MEASUREMENT_HOUR")
        st.line_chart(trend_df, color=["#4CAF50", "#f44336"])
        st.caption("Green = passing checks, Red = failing checks per measurement hour")
    else:
        st.info("Not enough historical data yet. Trend appears after multiple DMF evaluation cycles.")

    # Per-metric trend
    st.subheader("Individual Metric History")
    metric_trend = session.sql("""
        SELECT MEASUREMENT_TIME, METRIC_NAME, METRIC_VALUE
        FROM CORP_DWH.DQ.V_DQ_TREND
        ORDER BY MEASUREMENT_TIME
    """).to_pandas()

    if not metric_trend.empty:
        metrics = sorted(metric_trend["METRIC_NAME"].unique())
        selected = st.multiselect("Select metrics to plot", metrics, default=metrics[:3])
        if selected:
            filtered = metric_trend[metric_trend["METRIC_NAME"].isin(selected)]
            pivot = filtered.pivot_table(index="MEASUREMENT_TIME", columns="METRIC_NAME", values="METRIC_VALUE")
            st.line_chart(pivot)
    else:
        st.info("No metric history available.")

# === TAB 3: Failures Detail ===
with tab3:
    st.subheader("Failing Rules")
    fails = session.sql(
        "SELECT METRIC_NAME AS RULE, COLUMN_CHECKED, METRIC_VALUE AS VIOLATIONS, "
        "SEVERITY, RULE_OWNER AS OWNER, MEASUREMENT_TIME AS LAST_CHECKED "
        "FROM CORP_DWH.DQ.V_DQ_RESULTS_FLAT WHERE STATUS = 'FAIL' AND METRIC_VALUE > 0 "
        "ORDER BY METRIC_VALUE DESC"
    ).to_pandas()

    if not fails.empty:
        # Severity filter
        severities = ["All"] + sorted(fails["SEVERITY"].unique().tolist())
        selected_sev = st.selectbox("Filter by severity", severities)
        if selected_sev != "All":
            fails = fails[fails["SEVERITY"] == selected_sev]

        st.dataframe(fails, use_container_width=True, hide_index=True)
        st.caption(f"Showing {len(fails)} failing rule(s)")
    else:
        st.success("\u2705 No failures detected! All expectations are passing.")

# === TAB 4: Rules Catalog ===
with tab4:
    st.subheader("Active Rules Catalog")
    catalog = session.sql(
        "SELECT RULE_NAME, RULE_TYPE, TARGET_TABLE, TARGET_COLUMN, SEVERITY, OWNER, "
        "CASE WHEN DMF_NAME IS NOT NULL THEN '\u2705 Provisioned' ELSE '\u23F3 Pending' END AS STATUS "
        "FROM CORP_DWH.DQ.RULES_CATALOG WHERE IS_ACTIVE = TRUE ORDER BY SEVERITY DESC"
    ).to_pandas()

    if not catalog.empty:
        # Summary metrics
        prov = len(catalog[catalog["STATUS"].str.contains("Provisioned")])
        pend = len(catalog) - prov
        mcol1, mcol2, mcol3 = st.columns(3)
        mcol1.metric("Total Rules", len(catalog))
        mcol2.metric("Provisioned", prov)
        mcol3.metric("Pending", pend)

        st.dataframe(catalog, use_container_width=True, hide_index=True)
    else:
        st.info("No rules in catalog. Run Module 3 first.")

# === TAB 5: Drill-Down ===
with tab5:
    st.subheader("Investigate Specific Issues")
    st.markdown("""
    Use these queries to drill into specific DQ failures. Select a category below.
    """)

    drill = st.selectbox("Investigation type", [
        "NULL National IDs (CRM)",
        "Duplicate Customers",
        "Orphan Transactions",
        "Stale Data (Freshness)"
    ])

    if drill == "NULL National IDs (CRM)":
        df = session.sql("""
            SELECT CUSTOMER_NAME, EMAIL, CITY, SOURCE_SYSTEM
            FROM CORP_DWH.SILVER.INT_CUSTOMERS
            WHERE NATIONAL_ID IS NULL
            ORDER BY CUSTOMER_NAME
        """).to_pandas()
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"{len(df)} customers with NULL National ID")

    elif drill == "Duplicate Customers":
        df = session.sql("""
            SELECT CUSTOMER_NAME, NATIONAL_ID, SOURCE_SYSTEM, EMAIL, IS_DUPLICATE
            FROM CORP_DWH.SILVER.INT_CUSTOMERS
            WHERE IS_DUPLICATE = TRUE
            ORDER BY NATIONAL_ID
        """).to_pandas()
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"{len(df)} duplicate records flagged")

    elif drill == "Orphan Transactions":
        df = session.sql("""
            SELECT TXN_ID, CUSTOMER_ID, CUSTOMER_REF, AMOUNT, TXN_TYPE, TXN_DATE
            FROM CORP_DWH.GOLD.FACT_TRANSACTIONS
            WHERE CUSTOMER_ID NOT IN (SELECT CUSTOMER_ID FROM CORP_DWH.GOLD.DIM_CUSTOMER)
            ORDER BY AMOUNT DESC LIMIT 20
        """).to_pandas()
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"{len(df)} orphan transactions (CUSTOMER_ID not in DIM_CUSTOMER)")

    elif drill == "Stale Data (Freshness)":
        df = session.sql("""
            SELECT 'STG_TRANSACTIONS' AS TABLE_NAME,
                MAX(LOADED_AT) AS LAST_LOAD,
                DATEDIFF('HOUR', MAX(LOADED_AT), CURRENT_TIMESTAMP()) AS HOURS_SINCE_LOAD,
                CASE WHEN DATEDIFF('HOUR', MAX(LOADED_AT), CURRENT_TIMESTAMP()) > 2
                     THEN 'STALE' ELSE 'FRESH' END AS STATUS
            FROM CORP_DWH.RAW.STG_TRANSACTIONS
        """).to_pandas()
        st.dataframe(df, use_container_width=True, hide_index=True)
