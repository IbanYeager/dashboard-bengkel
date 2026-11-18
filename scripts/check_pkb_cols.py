import sqlite3

conn = sqlite3.connect(r"c:\laragon\www\dashboard_bengkel\data\bengkel.db")
cur = conn.cursor()

# Check what columns raw_pkb has
cur.execute("PRAGMA table_info(raw_pkb)")
cols = [c[1] for c in cur.fetchall()]
print("raw_pkb cols:", cols)
