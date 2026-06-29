import schedule 
import time
from datetime import datetime
import logging

from load_bronze import load_to_bronze
from transform_silver import load_to_silver
from transform_gold import load_fact_table

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s] - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def run_daily_pipeline():
    """"Runs the pipeline daily"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f"Pipeline started at: {current_time} (Tashkent time)")

    try:
        logging.info("Executing Step 1: Extracting to Bronze...")
        load_to_bronze()

        logging.info("\nExecuting Step 2: Transforming to Silver...")
        load_to_silver()

        logging.info("\nExecuting Step 3: Updating Gold fact table")
        load_fact_table()

        logging.info(f"\n Pipeline completed successfully at {datetime.now().strftime("%H:%M:%S")}")
    except Exception as e:
        logging.info(f"❌ Pipeline crashed! Error: {str(e)}")

schedule.every().day.at("03:00").do(run_daily_pipeline)

logging.info("Scheduler is now active")

while True:
        try:
            schedule.run_pending()
            time.sleep(60) 
        except Exception as loop_error:
            logging.error(f"⚠️ Scheduler Core Engine Loop Exception encountered: {str(loop_error)}", exc_info=True)
            time.sleep(10)