from extract import fetch_rates
from db_connection import get_connection
import json
from datetime import datetime

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
    data = fetch_rates(base_currency=base_currency, target_currencies=target_currencies, date=date)
    if not data:
        print(f"No data returned for date: {date}. Skipping.")
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

        print(f"Inserted bronze row for {fetch_date}")
    else:
        print(f"Bronze data for {fetch_date} already exists. Skipped")

if __name__ == "__main__":
    load_to_bronze(date='2026-01-21')