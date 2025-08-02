import requests
import psycopg2
from psycopg2.extras import execute_values
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

API_URL = "https://world.openfoodfacts.org/cgi/search.pl?search_simple=1&action=process&json=1&page_size=20"

def fetch_products():
    response = requests.get(API_URL)
    response.raise_for_status()
    return response.json().get("products", [])

def transform(product):
    return (
        product.get("product_name", ""),
        product.get("brands", ""),
        product.get("categories", ""),
        product.get("code", ""),
        product.get("quantity", ""),
        product.get("nutriscore_grade", ""),
        product.get("url", "")
    )

def insert_into_postgres(products):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    insert_query = """
        INSERT INTO raw_data (
            product_name, brand, categories, barcode,
            quantity, nutriscore_grade, url
        )
        VALUES %s
    """

    rows = [transform(prod) for prod in products]
    execute_values(cursor, insert_query, rows)
    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ Inserted {len(rows)} products into raw_data.")

def run_ingestion():
    print("📥 Fetching product data...")
    products = fetch_products()
    if products:
        insert_into_postgres(products)
    else:
        print("⚠️ No products found.")

if __name__ == "__main__":
    run_ingestion()