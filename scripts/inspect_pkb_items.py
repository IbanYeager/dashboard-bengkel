import sqlite3

conn = sqlite3.connect('data/bengkel.db')
cur = conn.cursor()

cur.execute("SELECT * FROM raw_so WHERE wo = '146PKB2604-0832'")
rows = cur.fetchall()
for r in rows:
    print(r)

conn.close()
