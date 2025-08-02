# 🧠 AgenticSupplyPilot

A modular, intelligent data quality monitoring platform powered by agents. Built with a PostgreSQL backend, rule-based anomaly detection, and LLM-powered summarization, this project automates anomaly detection and insight generation across tabular data streams.

---

## 📦 Features

- ✅ **Automated Ingestion** from OpenFoodFacts (or other data streams)
- 🧹 **Data Cleaning** using custom rules
- ⚠️ **Anomaly Detection** (missing values, duplicates)
- 🤖 **LLM Agent Summarization** using OpenAI (GPT-3.5) or HuggingFace
- 📊 **Interactive Dashboard** with Streamlit
- 🐳 Dockerized and production-ready

---

## 🏗️ Architecture

```
            +----------------+
            |  PostgreSQL DB |
            +--------+-------+
                     ^
                     |
       +-------------+-------------+
       |                           |
+--------------+         +----------------+
| Ingestion    |         | Anomaly Agent  |
| (open_food)  |         | (rule-based)   |
+--------------+         +----------------+
       |                           |
       +-------------+-------------+
                     |
        +------------v------------+
        |     explain_agent.py    |  <-- LLM Summary
        +------------+------------+
                     |
            +--------v--------+
            |   Streamlit UI  |
            +----------------+
```

---

## 🚀 Getting Started

### 📁 Project Structure

```
AgenticSupplyPilot-DataCleanser/
├── docker-compose.yml
├── requirements.txt
├── dashboard/               ← Streamlit UI
├── src/
│   ├── db/                  ← schema.sql
│   ├── ingestion/           ← open_food_facts.py
│   ├── cleaning/            ← data_cleaner.py
│   ├── anomalies/           ← anomaly_detector.py
│   ├── llm_agent/           ← explain_agent.py
│   └── dockerfile
```

---

## 🐳 Run the App (Docker)

### 1. 🔧 Prerequisites

- Docker + Docker Compose
- `.env` file at root:

```env
OPENAI_API_KEY=sk-...
DB_HOST=postgres
DB_PORT=5432
DB_USER=aspuser
DB_PASSWORD=asppassword
DB_NAME=aspdb
```

### 2. 🏗️ Build and Run

```bash
docker compose up --build
```

Streamlit UI will be available at: [http://localhost:8501](http://localhost:8501)

---

## 🧪 Run Manually (Local Dev)

```bash
python src/ingestion/open_food_facts.py
python src/cleaning/data_cleaner.py
python src/anomalies/anomaly_detector.py
python src/llm_agent/explain_agent.py
streamlit run dashboard/Streamlitapp.py
```

---

## 📊 Dashboard Features

- Filter anomalies by date
- View the 10 most recent LLM summaries
- Interactive exploration of the anomalies table

---

## 📌 How It Works

### 🔍 Anomaly Detection Rules

- Missing product fields (e.g. barcode, name)
- Duplicate barcodes
- Invalid numeric formats

### 🤖 LLM Agent (Summarizer)

- Uses `gpt-3.5-turbo` or `flan-t5-base`
- Generates human-like summaries with trends and flags
- Summaries stored in `agent_logs` table

---

## 🛣️ Future Roadmap

-

---

## 🧪 Testing

Test DB connection:

```bash
psql -U aspuser -d aspdb -h localhost -p 5543
```

Test agent:

```bash
python src/llm_agent/explain_agent.py
```

---

## 📄 License

MIT License © 2025 AgenticSupplyPilot Team

---

## 🙋‍♂️ Maintainer

**Jhilmit Asri**\
[LinkedIn](https://www.linkedin.com/in/jhilmitasri/)\
[GitHub](https://github.com/Jhilmit)

