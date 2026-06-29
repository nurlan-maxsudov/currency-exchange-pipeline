import pandas as pd
from db_connection import get_connection, get_sqlalchemy_engine
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s] - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def populate_dimensions():
    conn = get_connection()
    with conn:
        with conn.cursor() as cursor:
            currencies = [
                ('USD', 'US Dollar', '$', 'United States'),
                ('UZS', 'Uzbekistani Som', 'soʻm', 'Uzbekistan'),
                ('RUB', 'Russian Ruble', '₽', 'Russia'),
                ('EUR', 'Euro', '€', 'Eurozone'),
                ('GBP', 'British Pound', '£', 'United Kingdom')
            ]
            cursor.executemany("""
                INSERT INTO dim_currencies (currency_code, name, symbol, country)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (currency_code) DO NOTHING
            """, currencies)

            cursor.execute("SELECT DISTINCT date FROM cleaned_rates")
            dates = [row[0] for row in cursor.fetchall()]
            
            for d in dates:
                #Checking for weekdays. Saturday = 5, Sunday = 6
                is_weekday = d.weekday() < 5
                cursor.execute("""
                    INSERT INTO dim_dates (date, year, month, day, is_weekday)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (date) DO NOTHING
                """, (d, d.year, d.month, d.day, is_weekday))
                
    logging.info("Dimensions updated successfully")

def load_fact_table():

    logging.info("Gold layer refresh initiated: Fetching data from Silver...")

    conn = get_connection()
    engine = get_sqlalchemy_engine()

    #Extacting the data
    query = """
            SELECT date, base_currency, target_currency, exchange_rate FROM cleaned_rates
            """

    df = pd.read_sql(query, engine)

    if df.empty:
        logging.warning("Gold Layer Warning: No silver records found in 'cleaned_rates'. Aborting refresh.")
        return

    #computing new columns (rate_change_pct and rolling_7day_avg)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by=['target_currency', 'date']).reset_index(drop=True)

    df['prev_rate'] = df.groupby('target_currency')['exchange_rate'].shift(1)
    df['rate_change_pct'] = (df['exchange_rate'] - df['prev_rate']) / df['prev_rate']
    df['rate_change_pct'] = df['rate_change_pct'].fillna(0.0)


    df['rolling_7_day_avg'] = (
        df.groupby('target_currency')['exchange_rate']
        .transform(lambda x: x.rolling(window=7, min_periods=1).mean())
    )

    gold_records = []
    for _, row in df.iterrows():
        gold_records.append((
            row['date'].date(),
            row['target_currency'],
            float(row['exchange_rate']),
            float(row['rate_change_pct']),
            float(row['rolling_7_day_avg']))
        )

    with conn:
        with conn.cursor() as cursor:
            logging.info("Truncating old Gold table 'aggregated_rates' for full refresh.")
            cursor.execute("TRUNCATE TABLE aggregated_rates")
            
            cursor.executemany("""
                    INSERT INTO aggregated_rates (date, target_currency, exchange_rate, rate_change_pct, avg_7_day)
                    VALUES (%s,%s, %s, %s, %s)
                               """, gold_records)
    logging.info(f"Gold Layer Refresh Complete -> Successfully calculated and loaded {len(gold_records)} metric rows.")

if __name__ == "__main__":
    populate_dimensions()
    load_fact_table()