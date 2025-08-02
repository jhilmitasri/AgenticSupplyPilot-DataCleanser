import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

def detect_anomalies():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Fetch cleaned data
    cur.execute("SELECT * FROM cleaned_data")
    rows = cur.fetchall()

    anomaly_rows = []

    seen_barcodes = set()
    duplicates = set()

    for row in rows:
        id, product_name, brand, categories, barcode, quantity, nutriscore_grade, url, *_ = row

        # Invalid barcode
        if not barcode or not barcode.isdigit() or len(barcode) < 12:
            anomaly_rows.append((barcode, "Invalid or missing barcode", barcode))

        # Generic categories
        if not categories or categories.strip().lower() in ["uncategorized", "unknown", "n/a", "", "?"]:
            anomaly_rows.append((barcode, "Missing or generic category", categories))

        # Weird quantities
        if not quantity or len(quantity.strip()) < 2 or quantity.lower() in ["0g", "unknown", ""]:
            anomaly_rows.append((barcode, "Suspicious quantity", quantity))

        # Duplicate barcodes
        if barcode in seen_barcodes:
            duplicates.add(barcode)
        else:
            seen_barcodes.add(barcode)

    for dup in duplicates:
        anomaly_rows.append((dup, "Duplicate barcode in batch", dup))

    if anomaly_rows:
        insert_query = """
            INSERT INTO anomalies (barcode, issue, original_value)
            VALUES (%s, %s, %s)
        """
        cur.executemany(insert_query, anomaly_rows)
        print(f"⚠️ Flagged {len(anomaly_rows)} anomalies.")
    else:
        print("✅ No anomalies found.")

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    detect_anomalies()