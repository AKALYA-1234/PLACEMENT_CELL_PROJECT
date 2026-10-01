import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

passwords = [
    'postgres', 'admin', 'root', '123456', 'password', 'postgres123',
    'admin123', 'root123', '1234', '0000', '12345678', 'password123',
    'DELL', 'dell', 'ssg', 'placement', ''
]
users = ['postgres', 'DELL', 'dell']

found = False

for u in users:
    for pwd in passwords:
        try:
            conn = psycopg2.connect(host='localhost', port=5432, user=u, password=pwd, dbname='postgres')
            print(f"SUCCESS! User: '{u}', Password: '{pwd}'")
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM pg_database WHERE datname='placement_cell'")
            if not cursor.fetchone():
                cursor.execute("CREATE DATABASE placement_cell")
                print("Database 'placement_cell' created!")
            else:
                print("Database 'placement_cell' already exists.")
            cursor.close()
            conn.close()
            found = True
            break
        except Exception as e:
            pass
    if found:
        break

if not found:
    print("NO_MATCH")
