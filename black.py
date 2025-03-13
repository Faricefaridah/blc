import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("Connection successful.")
    except Error as e:
        print(e)
    return conn

def create_table(conn):
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS blacklisted_clients (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        id_number TEXT NOT NULL,
        shop TEXT NOT NULL,
        phone_number TEXT NOT NULL
    );
    """
    try:
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        print("Table created successfully.")
    except Error as e:
        print(e)

def insert_client(conn, client):
    sql = """
    INSERT INTO blacklisted_clients(name, id_number, shop, phone_number)
    VALUES(?, ?, ?, ?)
    """
    try:
        cursor = conn.cursor()
        cursor.execute(sql, client)
        conn.commit()
        print("Client added successfully.")
    except Error as e:
        print(e)

def select_all_clients(conn):
    sql = "SELECT * FROM blacklisted_clients"
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            print(row)
    except Error as e:
        print(e)

database = "blacklist.db"
conn = create_connection(database)
create_table(conn)

# Example of adding a client
client = ("ISAAC KIMANI", "35269093", "AL YASEEN", "0703339053")
insert_client(conn, client)

# Query the database to check if the client was added
select_all_clients(conn)

if conn:
    conn.close()
    print("Connection closed.")
