import streamlit as st
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="DQ Monitor", page_icon="shield", layout="wide")
session = get_active_session()

st.title("Data Quality Monitoring Dashboard")
st.caption("Real-time quality metrics for CORP_DWH")

exec_df = session.sql("SELECT * FROM CORP_DWH.DQ.V_DQ_EXECUTIVE_SUMMARY").to_pandas()

if not exec_df.empty:
    col1, col2, col3, col4 = st.columns(4)
    health = float(exec_df["OVERALL_HEALTH_PCT"].iloc[0] or 0)
    total = int(exec_df["TOTAL_CHECKS"].iloc[0] or 0)
    passing = int(exec_df["CHECKS_PASSING"].iloc[0] or 0)
    failing = int(exec_df["CHECKS_FAILING"].iloc[0] or 0)
    col1.metric("Overall Health", f"{health:.0f}%")
    col2.metric("Total Checks", total)
    col3.metric("Passing", passing)
    col4.metric("Failing", failing)
else:
    st.warning("No DQ results available yet.")

st.divider()
tab1, tab2, tab3 = st.tabs(["Scorecard", "Failing Rules", "Rules Catalog"])

with tab1:
    st.subheader("Health by Table")
    scorecard = session.sql("SELECT * FROM CORP_DWH.DQ.V_DQ_SCORECARD").to_pandas()
    if not scorecard.empty:
        for _, row in scorecard.iterrows():
            h = float(row["HEALTH_SCORE_PCT"] or 0)
            st.progress(h / 100, text=f"{row['TABLE_NAME']} -- {h:.0f}%")
    else:
        st.info("No scorecard data.")

with tab2:
    st.subheader("Top Failing Rules")
    fails = session.sql(
        "SELECT METRIC_NAME AS RULE, COLUMN_CHECKED, METRIC_VALUE AS VIOLATIONS, SEVERITY "
        "FROM CORP_DWH.DQ.V_DQ_RESULTS_FLAT WHERE STATUS = 'FAIL' AND METRIC_VALUE > 0 "
        "ORDER BY METRIC_VALUE DESC LIMIT 10"
    ).to_pandas()
    if not fails.empty:
        st.dataframe(fails, use_container_width=True, hide_index=True)
    else:
        st.success("No failures detected!")

with tab3:
    st.subheader("Active Rules Catalog")
    catalog = session.sql(
        "SELECT RULE_NAME, RULE_TYPE, TARGET_TABLE, SEVERITY, OWNER, "
        "CASE WHEN DMF_NAME IS NOT NULL THEN 'Provisioned' ELSE 'Pending' END AS STATUS "
        "FROM CORP_DWH.DQ.RULES_CATALOG WHERE IS_ACTIVE = TRUE ORDER BY SEVERITY DESC"
    ).to_pandas()
    if not catalog.empty:
        st.dataframe(catalog, use_container_width=True, hide_index=True)
