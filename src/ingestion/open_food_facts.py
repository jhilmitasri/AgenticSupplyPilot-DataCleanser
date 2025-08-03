import requests
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import os
from datetime import datetime
import time

load_dotenv()

BASE_URL = "https://world.openfoodfacts.org/cgi/search.pl?search_simple=1&action=process&json=1&page_size=1000&page="

# Database connection helper
def connect_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", 5432),
        user=os.getenv("DB_USER", "aspuser"),
        password=os.getenv("DB_PASSWORD", "asppassword"),
        dbname=os.getenv("DB_NAME", "aspdb")
    )

def fetch_products_from_page(page):
    url = BASE_URL + str(page)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        return []
    products = response.json().get("products", [])
    return products

def insert_products(products):
    if not products:
        return 0

    connection = connect_db()
    cursor = connection.cursor()
    insert_query = """
        INSERT INTO raw_data (
            product_name, brand, categories, barcode, quantity,
            nutriscore_grade, url, last_updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (barcode) DO NOTHING
    """

    batch_size = 100
    total_inserted = 0

    for i in range(0, len(products), batch_size):
        batch = products[i:i + batch_size]
        data = [
            (
                p.get("product_name"),
                p.get("brands"),
                p.get("categories"),
                p.get("code"),
                p.get("quantity"),
                p.get("nutriscore_grade"),
                p.get("url"),
                datetime.utcnow()
            )
            for p in batch
        ]
        cursor.executemany(insert_query, data)
        connection.commit()
        inserted = cursor.rowcount
        total_inserted += inserted
        print(f"[DB] Inserted batch {i//batch_size + 1}: {inserted} records")

    cursor.close()
    connection.close()
    return total_inserted

def run_ingestion(max_pages=200):
    page = 1
    total_inserted = 0

    while page <= max_pages:
        print(f"[INFO] Fetching page {page}...")
        products = fetch_products_from_page(page)

        if not products:
            print(f"[INFO] No products returned on page {page}. Stopping.")
            break

        inserted = insert_products(products)
        print(f"[INFO] Page {page}: Inserted {inserted} products.")
        total_inserted += inserted

        page += 1
        time.sleep(1)  # Be kind to the API

    print(f"[DONE] Ingestion complete. Total products inserted: {total_inserted}")

if __name__ == "__main__":
    run_ingestion(max_pages=200)