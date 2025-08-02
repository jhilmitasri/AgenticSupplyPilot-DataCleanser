import psycopg2
from dotenv import load_dotenv
import os
from transformers import pipeline

load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

def fetch_anomalies():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT barcode, issue, original_value FROM anomalies ORDER BY flagged_at DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def build_prompt(anomalies):
    issues = "\n".join([f"- [{barcode}] {issue} (Value: {val})" for barcode, issue, val in anomalies])
    return f"""
You are a data quality analyst agent. Summarize the following anomalies found in product data:

{issues}

Include high-level trends and flag any critical patterns you see.
"""

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_openai_agent(anomalies):
    input_text = build_prompt(anomalies)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # cheap, fast, still very good
            messages=[
                {"role": "system", "content": "You are a data quality summarization agent."},
                {"role": "user", "content": input_text}
            ],
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("❌ Error during OpenAI summary:", e)
        return ""

def run_llm_agent(anomalies):
    summarizer = pipeline("text2text-generation", model="google/flan-t5-base", max_new_tokens=200)
    input_text = build_prompt(anomalies)

    try:
        result = summarizer(input_text)
        summary_text = result[0]['generated_text'].strip()
        return summary_text
    except Exception as e:
        print("❌ Error during LLM summary generation:", e)
        return ""

def save_log(message):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("INSERT INTO agent_logs (log_type, message) VALUES (%s, %s)", ("anomaly_summary", message))
    conn.commit()
    cur.close()
    conn.close()
    print("🧠 Logged LLM summary to agent_logs.")

def main():
    print("🚀 explain_agent.py started...")
    anomalies = fetch_anomalies()
    if not anomalies:
        print("✅ No anomalies to summarize.")
        return
    summary = run_openai_agent(anomalies)
    if summary:
        print("🧠 Summary:\n", summary)
        save_log(summary)
    else:
        print("⚠️ No summary returned by LLM.")

if __name__ == "__main__":
    main()