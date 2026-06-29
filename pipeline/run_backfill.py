import logging
from datetime import datetime, timedelta


from load_bronze import load_to_bronze
from transform_silver import load_to_silver
from transform_gold import populate_dimensions, load_fact_table

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s] - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)


START_DATE_STR = "2025-01-01"
END_DATE_STR   = "2025-01-05" 

def execute_automated_backfill():
    start_date = datetime.strptime(START_DATE_STR, "%Y-%m-%d").date()
    end_date = datetime.strptime(END_DATE_STR, "%Y-%m-%d").date()
    
    logging.info(f" Starting automated backfill sequence from {start_date} to {end_date}...")
    
    current_date = start_date
    total_days_processed = 0
    
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        logging.info(f"\n{"="*50}\n PROCESSING DATE: {date_str}\n{"="*50}")
        
        #1 bronze
        logging.info(f"Step 1/3: Fetching and loading {date_str} to Bronze...")
        load_to_bronze(date=date_str)
        
        #2 silver
        logging.info(f"Step 2/3: Cleaning and moving {date_str} to Silver...")
        load_to_silver(target_date=date_str)
        
        # next day
        current_date += timedelta(days=1)
        total_days_processed += 1

    #3 gold
    logging.info(f"\n{"="*50}\nStep 3/3: Finalizing Gold Layer & Recomputing Metrics...\n{"="*50}")
    populate_dimensions()
    load_fact_table()
    
    logging.info(f"✅ SUCCESS! Backfill complete. Processed {total_days_processed} days sequence cleanly.")

if __name__ == "__main__":
    execute_automated_backfill()