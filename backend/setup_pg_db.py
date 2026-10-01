import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DB_NAME = "placement_cell"
USER = "openpg"
PASS = "openpgpwd"
HOST = "localhost"
PORT = 5432

def init_db():
    conn = psycopg2.connect(host=HOST, port=PORT, user=USER, password=PASS, dbname="postgres")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    cursor.execute("SELECT 1 FROM pg_database WHERE datname=%s", (DB_NAME,))
    exists = cursor.fetchone()
    
    if not exists:
        cursor.execute(f'CREATE DATABASE "{DB_NAME}"')
        print(f"Database '{DB_NAME}' created successfully!")
    else:
        print(f"Database '{DB_NAME}' already exists.")
        
    cursor.close()
    conn.close()

if __name__ == "__main__":
    init_db()
