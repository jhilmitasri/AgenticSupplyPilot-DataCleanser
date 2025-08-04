#!/bin/bash

echo "🔁 ENTRYPOINT: RUN_MODE=$RUN_MODE"

if [ "$RUN_MODE" = "prod" ]; then
  echo "🚀 Running full agent pipeline..."
  python ingestion/open_food_facts.py &&
  python cleaning/data_cleaner.py &&
  python anomalies/anomaly_detector.py &&
  python llm_agent/explain_agent.py
else
  echo "💤 Dev mode: keeping container alive..."
  tail -f /dev/null
fi