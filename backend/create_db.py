import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def check_and_create_db():
    try:
        conn = psycopg2.connect('postgresql://postgres:postgres@localhost:5432/postgres')
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='placement_cell'")
        exists = cursor.fetchone()
        if not exists:
            cursor.execute('CREATE DATABASE placement_cell')
            print('Successfully created database placement_cell')
        else:
            print('Database placement_cell already exists')
        cursor.close()
        conn.close()
    except Exception as e:
        print(f'DB Check/Create Exception: {e}')

if __name__ == '__main__':
    check_and_create_db()
