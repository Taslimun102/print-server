import sqlite3
import os
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "print_server.db")

os.makedirs(os.path.join(BASE_DIR, "database"), exist_ok=True)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# USERS TABLE
c.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
''')

# FILE TABLE
c.execute('''
CREATE TABLE files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    status TEXT,
    user TEXT
)
''')

conn.commit()
conn.close()

print("✅ Database Ready")
