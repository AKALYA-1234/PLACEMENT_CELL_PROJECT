import psycopg2

users = ['openpg', 'postgres', 'odoo', 'admin', 'root']
passwords = ['openpgpwd', 'postgres', 'odoo', 'admin', 'root', '123456', 'password', 'postgres123', 'admin123', 'root123', '1234', '0000', '12345678', 'password123', '']

for u in users:
    for p in passwords:
        try:
            conn = psycopg2.connect(host='localhost', port=5432, user=u, password=p, dbname='postgres')
            print(f"MATCH FOUND! User: '{u}', Password: '{p}'")
            conn.close()
            exit(0)
        except Exception as e:
            err = str(e)
            if "database \"postgres\" does not exist" in err:
                try:
                    conn = psycopg2.connect(host='localhost', port=5432, user=u, password=p, dbname='template1')
                    print(f"MATCH FOUND (template1)! User: '{u}', Password: '{p}'")
                    conn.close()
                    exit(0)
                except:
                    pass

print("No match found with default list.")
