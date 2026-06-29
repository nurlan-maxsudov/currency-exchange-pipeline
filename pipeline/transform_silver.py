from db_connection import get_connection


def fetch_unprocessed_bronze_rows(target_date = None):
    conn = get_connection()
    with conn:
        with conn.cursor() as cursor:
            if target_date:

                cursor.execute("SELECT raw_json FROM raw_rates WHERE fetch_date = %s",
                            (target_date,))
            else:
                cursor.execute("""
                            SELECT b.raw_json
                            FROM raw_rates b
                            WHERE b.fetch_date NOT IN (
                            SELECT DISTINCT s.date FROM cleaned_rates s
                            )
                            """)
            rows = cursor.fetchall()
    return rows



def load_to_silver(target_date=None):
    rows = fetch_unprocessed_bronze_rows()

    if not rows:
        print("Silver layer is already up-to-date. No new rows to process")
        return
    conn = get_connection()

    with conn:
        with conn.cursor() as cursor:
            for row in rows:
                currency_list = row[0]

                for currency in currency_list:

                    date = currency['date']
                    base_currency = str(currency['base']).upper().strip()
                    target_currency = str(currency['quote']).upper().strip()
                    
                    exchange_rate = float(currency['rate'])

                    if exchange_rate <= 0:
                        continue

                    cursor.execute(
                        """INSERT INTO cleaned_rates (date, base_currency, target_currency, exchange_rate) 
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (date, target_currency) DO NOTHING""",
                        (date, base_currency, target_currency, exchange_rate)
                    )        

    print(f"Silver load done")

if __name__ == "__main__":
    load_to_silver()