import schedule 
import time
from datetime import datetime

from load_bronze import load_to_bronze
from transform_silver import load_to_silver
from transform_gold import load_fact_table

def run_daily_pipeline():
    """"Runs the pipeline daily"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Pipeline started at: {current_time} (Tashkent time)")

    try:
        print("Executing Step 1: Extracting to Bronze...")
        load_to_bronze(date='2026-01-20')

        print("\nExecuting Step 2: Transforming to Silver...")
        load_to_silver()

        print("\nExecuting Step 3: Updating Gold fact table")
        load_fact_table()

        print(f"\n Pipeline completed successfully at {datetime.now().strftime("%H:%M:%S")}")
    except Exception as e:
        print(f"❌ Pipeline crashed! Error: {str(e)}")

schedule.every().day.at("03:00").do(run_daily_pipeline)

print("Scheduler is now active")
