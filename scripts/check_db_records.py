import sqlite3

conn = sqlite3.connect(r"c:\laragon\www\dashboard_bengkel\data\bengkel.db")
cur = conn.cursor()

# Check total records in raw_pkb
cur.execute("SELECT count(*) FROM raw_pkb")
print("Total records in raw_pkb:", cur.fetchone()[0])

# Check distinct years and months in raw_pkb
cur.execute("SELECT DISTINCT tahun, month_name FROM raw_pkb ORDER BY tahun, month_name")
print("Years & months:", cur.fetchall())
