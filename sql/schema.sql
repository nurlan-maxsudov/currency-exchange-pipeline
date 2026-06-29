CREATE TABLE raw_rates (
    id SERIAL PRIMARY KEY,
    fetch_date DATE NOT NULL,
    base_currency VARCHAR(3) NOT NULL,
    raw_json JSONB NOT NULL,
    inserted_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE cleaned_rates (
    date DATE NOT NULL,
    base_currency VARCHAR(3) NOT NULL,
    target_currency VARCHAR(3) NOT NULL,
    exchange_rate DECIMAL (15,6) NOT NULL,
    load_timestamp TIMESTAMP DEFAULT NOW()
);

CREATE TABLE dim_currencies (
    currency_code VARCHAR(3) NOT NULL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    symbol VARCHAR(2) NOT NULL,
    country VARCHAR(30) NOT NULL
);

CREATE TABLE dim_dates (
    date DATE NOT NULL PRIMARY KEY,
    year INT NOT NULL,
    month INT NOT NULL,
    day INT NOT NULL,
    is_weekday BOOLEAN NOT NULL
);

CREATE TABLE aggregated_rates (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL REFERENCES dim_dates(date),
    target_currency VARCHAR(3) NOT NULL REFERENCES dim_currencies(currency_code),
    exchange_rate DECIMAL(15,6) NOT NULL,
    rate_change_pct DECIMAL(10,4),
    avg_7_day DECIMAL(15,6),
    load_timestamp TIMESTAMP DEFAULT NOW()
);

