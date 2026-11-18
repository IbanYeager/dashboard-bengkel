import sqlite3

conn = sqlite3.connect('data/bengkel.db')
c = conn.cursor()

c.execute("""
    SELECT tgl, count(*), sum(revenue)
    FROM raw_pkb
    WHERE tahun = '2026' AND bulan = '07'
    GROUP BY tgl
    ORDER BY tgl;
""")
print("Dates in 2026 Bulan 07:")
rows = c.fetchall()
for r in rows:
    print(r)

print(f"\nTotal dates present in July 2026: {len(rows)}")

c.execute("""
    SELECT min(tgl), max(tgl)
    FROM raw_pkb
    WHERE tahun = '2026' AND bulan = '07';
""")
print("Date range in July 2026:", c.fetchone())

# Also check June and August
c.execute("SELECT min(tgl), max(tgl), count(*) FROM raw_pkb WHERE tahun = '2026' AND bulan = '06';")
print("June 2026:", c.fetchone())
c.execute("SELECT min(tgl), max(tgl), count(*) FROM raw_pkb WHERE tahun = '2026' AND bulan in ('08', '8.0');")
print("August 2026:", c.fetchone())

conn.close()
