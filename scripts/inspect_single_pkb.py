import sqlite3

conn = sqlite3.connect('data/bengkel.db')
cur = conn.cursor()

cur.execute("SELECT * FROM raw_pkb WHERE pkb_no = '146PKB2604-0832'")
row = cur.fetchone()
cur.execute("PRAGMA table_info(raw_pkb)")
cols = [r[1] for r in cur.fetchall()]
for c, v in zip(cols, row):
    print(f"  {c}: {v}")

conn.close()
