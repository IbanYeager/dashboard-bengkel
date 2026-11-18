import zipfile
import xml.etree.ElementTree as ET
import sqlite3

conn = sqlite3.connect('data/bengkel.db')
c = conn.cursor()

# Check Jan..Aug 2026 in raw_pkb
print("Month, Total rows, CPUS, SBI, TWC, Others:")
c.execute("""
SELECT month_name, 
       COUNT(*), 
       SUM(CASE WHEN type_ue = 'CPUS' THEN 1 ELSE 0 END),
       SUM(CASE WHEN type_ue = 'SBI' THEN 1 ELSE 0 END),
       SUM(CASE WHEN type_ue = 'TWC' THEN 1 ELSE 0 END),
       SUM(CASE WHEN type_ue NOT IN ('CPUS', 'SBI', 'TWC') THEN 1 ELSE 0 END)
FROM raw_pkb
WHERE tahun = 2026
GROUP BY month_name
""")
for r in c.fetchall():
    print(r)
