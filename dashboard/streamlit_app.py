import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime, timedelta
import os

# DB config
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

def fetch_anomalies_by_date(start_date, end_date):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT barcode, issue, original_value, flagged_at
        FROM anomalies
        WHERE flagged_at BETWEEN %s AND %s
        ORDER BY flagged_at DESC
        """, (start_date, end_date)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return pd.DataFrame(rows, columns=["barcode", "issue", "original_value", "flagged_at"])

def fetch_agent_logs():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT created_at, message
        FROM agent_logs
        WHERE log_type = 'anomaly_summary'
        ORDER BY created_at DESC
        LIMIT 10
        """
    )
    logs = cur.fetchall()
    cur.close()
    conn.close()
    return logs

# Streamlit App
st.set_page_config(page_title="AgenticSupplyPilot", layout="wide")
st.title("🧠 AgenticSupplyPilot Dashboard")

# Date Range Filter
st.subheader("📅 Filter Anomalies by Date")
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", datetime.today() - timedelta(days=7))
with col2:
    end_date = st.date_input("End Date", datetime.today())

# Refresh Button
if st.button("🔁 Refresh LLM Summary"):
    st.success("LLM Summary refresh triggered! (To be connected to agent runner)")

# Display Anomalies
start_dt = datetime.combine(start_date, datetime.min.time())
end_dt = datetime.combine(end_date, datetime.max.time())

anomaly_df = fetch_anomalies_by_date(start_dt, end_dt)
st.subheader("⚠️ Recent Anomalies")
st.dataframe(anomaly_df, use_container_width=True)

# Display Agent Logs
st.subheader("🧠 Agent Summaries")
logs = fetch_agent_logs()
for timestamp, message in logs:
    with st.expander(f"{timestamp}"):
        st.markdown(message)