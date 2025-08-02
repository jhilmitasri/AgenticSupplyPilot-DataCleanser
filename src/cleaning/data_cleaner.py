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
    product_name = (row[1] or "").strip().title()
    brand = (row[2] or "Unknown").strip().lower()
    categories = (row[3] or "Uncategorized").strip().lower()
    barcode = row[4]
    quantity = (row[5] or "").strip().lower()
    nutriscore_grade = (row[6] or "not_set").strip().lower()
    url = row[7]
    return (product_name, brand, categories, barcode, quantity, nutriscore_grade, url)

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
            quantity, nutriscore_grade, url
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    cur.executemany(insert_query, cleaned)
    conn.commit()
    print(f"✅ Cleaned and inserted {len(cleaned)} records.")

    cur.close()
    conn.close()

if __name__ == "__main__":
    clean_data()