import psycopg2
from dotenv import load_dotenv
import os
from transformers import pipeline
import tiktoken
from openai import OpenAIError
from openai import OpenAI  # or `import openai` if you're using older SDK
# from src.llm_agent.prompts import SUMMARY_PROMPT_TEMPLATE  # adjust import as needed

SUMMARY_PROMPT_TEMPLATE = """
You are an expert data quality analyst.

Given a list of anomalies found in product data, your job is to:
- Summarize key patterns (e.g., duplicates, invalid values)
- Highlight any critical risks or frequent issues
- Suggest steps for improving data quality

Make the summary concise but insightful, in bullet point or paragraph form.

Respond only with the summary.
"""

tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")

def estimate_tokens(text):
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
    return len(enc.encode(text))

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
from collections import defaultdict

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_summary_with_openai(chunk, issue_type):
    prompt = f"""
You are a data quality analyst agent. Summarize the following anomalies found in product data:

{chr(10).join(chunk)}

Include high-level trends and flag any critical patterns you see.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes food product anomalies."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Error summarizing issue type '{issue_type}':", e)
        return ""

def group_by_issue_type(records):
    grouped = defaultdict(list)
    for barcode, issue, val in records:
        grouped[issue].append((barcode, issue, val))
    return grouped

def run_openai_agent(anomalies):
    # Summarize by issue type to reduce token usage
    try:
        summaries = []
        grouped = group_by_issue_type(anomalies)
        for issue_type, group in grouped.items():
            text_rows = [f"- [{barcode}] {issue_type} (Value: {val})" for barcode, _, val in group]

            # Chunk rows to avoid exceeding token limit
            chunks = []
            current_chunk = []
            current_tokens = 0
            for row in text_rows:
                row_tokens = estimate_tokens(row)
                if current_tokens + row_tokens > 3000:
                    chunks.append(current_chunk)
                    current_chunk = [row]
                    current_tokens = row_tokens
                else:
                    current_chunk.append(row)
                    current_tokens += row_tokens
            if current_chunk:
                chunks.append(current_chunk)

            issue_summary_parts = []
            for i, chunk in enumerate(chunks):
                summary = generate_summary_with_openai(chunk, issue_type)
                issue_summary_parts.append(f"🔹 Part {i+1} ({issue_type}):\n{summary}")

            summaries.append("\n\n".join(issue_summary_parts))

        final_summary_prompt = "\n\n".join(summaries)
        final_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes food product anomalies."},
                {"role": "user", "content": f"Summarize the following combined insights:\n\n{final_summary_prompt}"}
            ],
            temperature=0.5
        )
        final_summary = final_response.choices[0].message.content.strip()
        print("[SUMMARY]", final_summary)
        return final_summary
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