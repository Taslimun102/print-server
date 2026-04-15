import sqlite3

conn = sqlite3.connect('print_server.db')
c = conn.cursor()

c.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("admin", "admin123"))

conn.commit()
conn.close()

print("✅ Admin user added")
