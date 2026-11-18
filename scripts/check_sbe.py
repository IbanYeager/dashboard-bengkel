import sqlite3

conn = sqlite3.connect('data/bengkel.db')
cur = conn.cursor()
cur.execute("SELECT lookup_job, type_service, count(id) FROM raw_pkb WHERE tahun=2026 AND month_name='July' GROUP BY lookup_job, type_service")
print("July 2026 lookup_job and type_service:")
for r in cur.fetchall():
    print(r)
