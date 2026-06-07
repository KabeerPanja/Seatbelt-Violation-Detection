import sqlite3
from config import DB_NAME

def connect():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate_number TEXT,
            violation_type TEXT
        )
    """)

    conn.commit()
    conn.close()

def insert(plate, violation="No Seatbelt"):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO violations (plate_number, violation_type)
        VALUES (?, ?)
    """, (plate, violation))

    conn.commit()
    conn.close()