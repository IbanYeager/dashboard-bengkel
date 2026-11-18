import sqlite3
import json

conn = sqlite3.connect('data/bengkel.db')
c = conn.cursor()

print("--- Check revenue=0 or negative in Sep 2026 ---")
c.execute("SELECT COUNT(*) FROM raw_pkb WHERE tahun=2026 AND month_name='September' AND revenue <= 0")
print("revenue <= 0:", c.fetchall())

print("--- Check distinct values in all columns for Sep 2026 ---")
for col in ['type_ue', 'type_service', 'arrival_type', 'fleet_retail', 'ths', 'lcgc']:
    c.execute(f"SELECT {col}, COUNT(*) FROM raw_pkb WHERE tahun=2026 AND month_name='September' GROUP BY {col}")
    print(f"Col {col}:", c.fetchall())

print("\n--- Check how many rows if excluding certain things ---")
# Exactly 722?
# 726 - 4 = 722!
c.execute("SELECT COUNT(*) FROM raw_pkb WHERE tahun=2026 AND month_name='September' AND revenue > 0")
print("revenue > 0:", c.fetchall())

c.execute("SELECT COUNT(*) FROM raw_pkb WHERE tahun=2026 AND month_name='September' AND type_ue IN ('CPUS', 'SBI')")
print("CPUS + SBI:", c.fetchall())

c.execute("SELECT COUNT(*) FROM raw_pkb WHERE tahun=2026 AND month_name='September' AND type_ue IN ('CPUS', 'TWC')")
print("CPUS + TWC:", c.fetchall())

c.execute("SELECT COUNT(*) FROM raw_pkb WHERE tahun=2026 AND month_name='September' AND ths != 'THS'")
print("not THS:", c.fetchall())

c.execute("SELECT COUNT(*) FROM raw_pkb WHERE tahun=2026 AND month_name='September' AND sa IN ('DIDIN', 'FICKY', 'ACEP')")
print("sa in DIDIN, FICKY, ACEP:", c.fetchall())

print("\n--- Check if any SA has non-standard name ---")
c.execute("SELECT sa, COUNT(*) FROM raw_pkb WHERE tahun=2026 AND month_name='September' GROUP BY sa")
print("All SAs:", c.fetchall())
