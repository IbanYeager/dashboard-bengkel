import sqlite3

conn = sqlite3.connect(r'data\bengkel.db')
cur = conn.cursor()
cur.execute("""
SELECT tahun, month_name, COUNT(*), SUM(revenue), 
       SUM(CASE WHEN type_ue='CPUS' THEN revenue ELSE 0 END),
       COUNT(CASE WHEN type_ue='CPUS' THEN 1 END)
FROM raw_pkb
WHERE tahun=2026
GROUP BY month_name
ORDER BY MIN(id)
""")
print(f"{'Year':<5} | {'Month':<10} | {'Total PKB':<10} | {'CPUS PKB':<10} | {'Total Rev':<18} | {'CPUS Rev':<18}")
print("-" * 80)
for row in cur.fetchall():
    print(f"{row[0]:<5} | {row[1]:<10} | {row[2]:<10} | {row[5]:<10} | Rp {row[3]:<15,.0f} | Rp {row[4]:<15,.0f}")
