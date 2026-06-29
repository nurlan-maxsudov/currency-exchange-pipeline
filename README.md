# Currency Exchange Rate ETL Pipeline

A production-grade, 3-tier (Bronze, Silver, Gold) ELT/ETL data pipeline that automates the collection, cleaning, and reporting of currency exchange rates using the Frankfurter API.

The pipeline fetches currency conversions from a **USD** base against targeted currencies (**EUR, GBP, RUB, UZS**) and stores them inside a structured PostgreSQL database using a Star Schema framework.

---

## 🛠️ Project Architecture

- **Bronze Layer (`load_bronze.py`)**: Directly calls the API, extracts the raw data payload, and logs the raw JSON structure dynamically into a staging audit table (`raw_rates`). It prevents duplicate network requests using an auditing date check strategy.
- **Silver Layer (`transform_silver.py`)**: Automatically scans the raw audit layer for newly available data, parses the incoming nested JSON keys, cleans corrupt value anomalies (such as fields containing values <= 0), forces rigid casting of types, and merges records safely into a deduplicated schema (`cleaned_rates`).
- **Gold Layer (`transform_gold.py`)**: Computes analytical dimension structures (`dim_dates`, `dim_currencies`) and performs full table metric updates inside the core analytical fact table (`aggregated_rates`), computing tracking variations such as 7-day rolling performance averages and percentage rate deltas via Pandas.

---

## 🚀 Getting Started

### 1. Prerequisites & Installation

Ensure you have Python 3.10+ and a live PostgreSQL instance running. Install the essential execution dependencies from your terminal:

```bash
pip install -r requirements.txt
```

(Alternatively, ensure you have manually installed: `pandas`, `psycopg2`, `sqlalchemy`, `python-dotenv`, and `schedule`.)

### 2. Configuration (.env)

To protect your production credentials, set up an environment file. Create a file named `.env` in the root directory of this project:

```
DB_NAME=your_database_name
DB_USER=your_postgres_username
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

---

## 🕹️ Execution Controls (One-Button Scripts)

You do not need to call your three execution layers independently or manage complex terminal commands. The workflow is completely automated through simple orchestration files.

### A. How to Run a Historical Backfill

When you need to pull missing historical ranges (e.g., the last 1–2 years or a specific month) day-by-day:

1. Open `run_backfill.py`.
2. Locate the control panel variables at the top of the file:

   ```python
   START_DATE_STR = "2025-01-01"
   END_DATE_STR   = "2025-01-05"
   ```

3. Update the dates to your desired history window.
4. Click your editor's Run button (or execute `python run_backfill.py` in your terminal). The file will automatically loop through every calendar day, handle data stages, and rebuild the analytics tables seamlessly.

### B. How to Run the Daily Automation Scheduler

To launch the background production manager — which monitors timeframes silently and automatically kicks off an end-to-end processing pass every morning at 03:00 AM Tashkent Time:

1. Open your terminal or runtime panel.
2. Run the main orchestrator script:

   ```bash
   python run_pipeline.py
   ```

3. Leave this script running. It will continuously monitor the system clock and manage updates automatically while sleeping in between to preserve server CPU resources.
