from extract import fetch_rates
from db_connection import get_connection
import json

def get_latest_date():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT MAX(fetch_date) FROM raw_rates"
    )

    latest_date = cursor.fetchone()

    return latest_date[0]

print(get_latest_date())