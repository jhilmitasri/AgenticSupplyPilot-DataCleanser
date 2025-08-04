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
        SELECT log_type, message, created_at
        FROM agent_logs
        WHERE log_type = 'anomaly_summary'
        ORDER BY created_at DESC
        LIMIT 10;
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
    st.success("TODO: LLM Summary refresh triggered! (To be connected to agent runner)")

# Display Anomalies
start_dt = datetime.combine(start_date, datetime.min.time())
end_dt = datetime.combine(end_date, datetime.max.time())

anomaly_df = fetch_anomalies_by_date(start_dt, end_dt)
st.subheader("⚠️ Recent Anomalies")
st.dataframe(anomaly_df, use_container_width=True)

# Agent Logs
st.markdown("###  Agent Insights Log")

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()
cur.execute("""
    SELECT created_at, message
    FROM agent_logs
    WHERE log_type = 'anomaly_summary'
    ORDER BY created_at DESC
""")
logs = cur.fetchall()
cur.close()
conn.close()
# st.write("🔍 Number of summaries fetched:", len(logs))
# st.write("🪵 Raw logs preview:", logs[:1])
if logs:
    for created_at, message in logs:
        with st.expander(f"🧠 Log @ {created_at}"):
            st.text_area("Summary", message or "No content", height=300)
else:
    st.info("No agent logs found.")
st.caption(f"Last updated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
# Optional styling tweak
st.markdown("""
    <style>
    .element-container:has(.stMarkdown) {
        max-height: None;
        # overflow-y: auto;
        # border: 1px solid #DDD;
        # padding: 1rem;
        # border-radius: 8px;
        
    }
    
    </style>
""", unsafe_allow_html=True)