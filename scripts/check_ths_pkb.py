import sqlite3

conn = sqlite3.connect('data/bengkel.db')
cur = conn.cursor()

cur.execute("SELECT arrival_type, COUNT(*) FROM raw_pkb GROUP BY arrival_type")
print("Arrival types in raw_pkb:")
for r in cur.fetchall():
    print(" ", r)

# Let's check mechanic or other columns that might contain THS
cur.execute("SELECT mechanic, COUNT(*) FROM raw_pkb WHERE mechanic LIKE '%THS%' GROUP BY mechanic")
print("Mechanic with THS:")
for r in cur.fetchall():
    print(" ", r)

# Let's check tipe_kendaraan or arrival_type or others
cur.execute("SELECT DISTINCT arrival_type FROM raw_pkb")
print("Distinct arrival_type:", cur.fetchall())

conn.close()
