import sqlite3

conn = sqlite3.connect('data/bengkel.db')
c = conn.cursor()

c.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables in data/bengkel.db:", [r[0] for r in c.fetchall()])

c.execute("""
    SELECT tahun, bulan, count(*), sum(revenue)
    FROM raw_pkb
    WHERE tahun = '2026'
    GROUP BY tahun, bulan
    ORDER BY count(*) DESC;
""")
print("\nRaw PKB counts in 2026 by bulan:")
for r in c.fetchall():
    print(r)

# Let's inspect rows with July or '07' or 'Jul' or whatever bulan value they have
c.execute("""
    SELECT DISTINCT bulan, count(*)
    FROM raw_pkb
    WHERE tahun = '2026'
    GROUP BY bulan;
""")
print("\nDistinct bulan values in 2026:")
for r in c.fetchall():
    print(r)

conn.close()
