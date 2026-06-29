import psycopg2
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

def get_connection():
    conn = psycopg2.connect(
        host = os.getenv("DB_HOST"),
        port = os.getenv("DB_PORT"),
        dbname = os.getenv("DB_NAME"),
        user = os.getenv("DB_USER"),
        password = os.getenv("DB_PASSWORD")
    )

    return conn

def get_sqlalchemy_engine():
    connection_string = f"postgresql+psycopg2://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost:5432/{os.getenv("DB_NAME")}"
    return create_engine(connection_string)

if __name__ == "__main__":
    conn = get_connection()
    print("Connected Successfully")
    conn.close()