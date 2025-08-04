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

def clean_record(row):
    try:
        (
            product_name, brand, categories, barcode,
            quantity, nutriscore_grade, url, last_updated_at
        ) = row

        return (
            (product_name or "").strip().title(),
            (brand or "Unknown").strip().lower(),
            (categories or "Uncategorized").strip().lower(),
            barcode,
            (quantity or "").strip().lower(),
            (nutriscore_grade or "not_set").strip().lower(),
            url,
            last_updated_at
        )
    except Exception as e:
        print(f"[CLEANING ERROR] Failed to clean row: {row} -> {e}")
        return None

def clean_data():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Fetch all raw data
    cur.execute("SELECT * FROM raw_data")
    raw_rows = cur.fetchall()

    cleaned = [clean_record(row) for row in raw_rows]

    insert_query = """
        INSERT INTO cleaned_data (
            product_name, brand, categories, barcode,
            quantity, nutriscore_grade, url, last_updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    cur.executemany(insert_query, cleaned)
    conn.commit()
    print(f"✅ Cleaned and inserted {len(cleaned)} records.")

    cur.close()
    conn.close()

if __name__ == "__main__":
    clean_data()