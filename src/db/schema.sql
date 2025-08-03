-- Raw ingested data from Open Food Facts API
CREATE TABLE IF NOT EXISTS raw_data (
    product_name TEXT,
    brand TEXT,
    categories TEXT,
    barcode TEXT PRIMARY KEY,
    quantity TEXT,
    nutriscore_grade TEXT,
    url TEXT,
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Cleaned and standardized data
CREATE TABLE IF NOT EXISTS cleaned_data (
    id SERIAL PRIMARY KEY,
    product_name TEXT,
    brand TEXT,
    categories TEXT,
    barcode TEXT,
    quantity TEXT,
    nutriscore_grade TEXT,
    url TEXT,
    last_updated_at TIMESTAMP
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

CREATE OR REPLACE FUNCTION update_last_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.last_updated_at = NOW();
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$
BEGIN
   IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'raw_data') THEN
      DROP TRIGGER IF EXISTS set_last_updated_at ON raw_data;
   END IF;
END$$;

CREATE TRIGGER set_last_updated_at
BEFORE UPDATE ON raw_data
FOR EACH ROW
EXECUTE FUNCTION update_last_updated_at_column();