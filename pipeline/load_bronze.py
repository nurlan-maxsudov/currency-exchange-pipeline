from extract import fetch_rates
from db_connection import get_connection
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s] - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)

def check_date_exists(target_date):
    #Returns True if the date already exists in the raw audit log.
    conn = get_connection()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM raw_rates WHERE fetch_date = %s LIMIT 1",
                (target_date,)
            )
            return cursor.fetchone() is not None




def load_to_bronze(base_currency="USD", target_currencies=["EUR", "GBP", "RUB", "UZS"], date=None):

    logging.info(f"Initiating API fetch for base: {base_currency}, targets: {target_currencies}, date: {date}")
    try:
        data = fetch_rates(base_currency=base_currency, target_currencies=target_currencies, date=date)
    except Exception as e:
        logging.error(f"API Fetch failed for date {date}! Error: {str(e)}")
        return

    if not data:
        logging.warning(f"No data returned from API for date: {date}. Skipping Bronze load")
        return
    
    fetch_date = date if date else data[0]['date']
    
    if not check_date_exists(fetch_date):

        conn = get_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                "INSERT INTO raw_rates (fetch_date, base_currency, raw_json) VALUES (%s, %s, %s)",
                (fetch_date, base_currency, json.dumps(data))
                )

        logging.info(f"Successfully inserted 1 raw Bronze row for execution date: {fetch_date}")
    else:
        logging.info(f"Bronze data for {fetch_date} already exists. Skipped")

if __name__ == "__main__":
    load_to_bronze(date='2026-01-22')