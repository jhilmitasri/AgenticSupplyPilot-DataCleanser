-- Raw ingested data from Open Food Facts API
CREATE TABLE IF NOT EXISTS raw_data (
    id SERIAL PRIMARY KEY,
    product_name TEXT,
    brand TEXT,
    categories TEXT,
    barcode VARCHAR(50),
    quantity TEXT,
    nutriscore_grade TEXT,
    url TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cleaned and standardized data
CREATE TABLE IF NOT EXISTS cleaned_data (
    id SERIAL PRIMARY KEY,
    product_name TEXT,
    brand TEXT,
    categories TEXT,
    barcode VARCHAR(50),
    quantity TEXT,
    nutriscore_grade TEXT,
    url TEXT,
    cleaned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Anomalies flagged during analysis
CREATE TABLE IF NOT EXISTS anomalies (
    id SERIAL PRIMARY KEY,
    barcode VARCHAR(50),
    issue TEXT,
    original_value TEXT,
    flagged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- LLM-generated explanations or reports
CREATE TABLE IF NOT EXISTS agent_logs (
    id SERIAL PRIMARY KEY,
    log_type TEXT,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);