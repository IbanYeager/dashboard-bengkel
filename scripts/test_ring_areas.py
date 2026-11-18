import sqlite3

# Let's write a python test to check if we can aggregate all these parameters cleanly from raw_pkb
conn = sqlite3.connect('data/bengkel.db')
cur = conn.cursor()

# Check sample ring_area counts
cur.execute("SELECT ring_area, COUNT(*) FROM raw_pkb WHERE tahun=2026 GROUP BY ring_area")
print("2026 Ring Areas:", cur.fetchall())

conn.close()
