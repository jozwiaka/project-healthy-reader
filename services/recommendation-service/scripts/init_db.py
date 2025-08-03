import os
import psycopg2

from config.settings import recommendation_db_url

SQL_FILE = "db/init.sql"

def run_sql_file(path: str, conn):
    with open(path, "r") as f:
        sql = f.read()
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()

def main():
    print("🔌 Connecting to the database...")
    conn = psycopg2.connect(recommendation_db_url)
    try:
        run_sql_file(SQL_FILE, conn)
        print("Database initialized successfully.")
    except Exception:
        print("Database already exists")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
