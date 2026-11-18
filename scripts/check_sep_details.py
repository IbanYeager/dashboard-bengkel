import sqlite3

conn = sqlite3.connect('data/bengkel.db')
c = conn.cursor()

print("--- PKB numbers in Sep 2026 ---")
c.execute("SELECT MIN(pkb_no), MAX(pkb_no), COUNT(*) FROM raw_pkb WHERE tahun=2026 AND month_name='September'")
print(c.fetchall())
c.execute("SELECT pkb_no, tgl, type_ue FROM raw_pkb WHERE tahun=2026 AND month_name='September' ORDER BY pkb_no DESC LIMIT 10")
for r in c.fetchall():
    print(r)

c.execute("SELECT tgl, COUNT(*), SUM(CASE WHEN type_ue='CPUS' THEN 1 ELSE 0 END) FROM raw_pkb WHERE tahun=2026 AND month_name='September' GROUP BY tgl ORDER BY tgl")
for r in c.fetchall():
    print(r)

print("\n--- all columns distinct for non-CPUS in Sep 2026 ---")
c.execute("SELECT type_service, COUNT(*) FROM raw_pkb WHERE tahun = 2026 AND month_name = 'September' AND (type_ue != 'CPUS' OR type_ue IS NULL) GROUP BY type_service")
for r in c.fetchall():
    print(r)

print("\n--- check SA distribution in Sep 2026 ---")
c.execute("SELECT sa, COUNT(*), SUM(CASE WHEN type_ue = 'CPUS' THEN 1 ELSE 0 END) FROM raw_pkb WHERE tahun = 2026 AND month_name = 'September' GROUP BY sa")
for r in c.fetchall():
    print(r)
