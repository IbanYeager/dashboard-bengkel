import sqlite3
import json

conn = sqlite3.connect('data/bengkel.db')
c = conn.cursor()

print("--- DIDIN IN SEP 2026 RAW_SO ---")
c.execute("SELECT * FROM raw_so WHERE sa LIKE '%DIDIN%' AND (bulan='9.0' OR bulan='09' OR month_name='September') AND tahun=2026")
rows = c.fetchall()
print(f"Total Didin rows in Sep 2026: {len(rows)}")
for r in rows:
    if 'TIRE' in str(r).upper():
        print("Found TIRE in Didin rows:", r)

print("\n--- ALL CROSS CATEGORIES IN SEP 2026 ---")
c.execute("SELECT sa, cross_category, count(*), sum(transaction_amount) FROM raw_so WHERE (bulan='9.0' OR bulan='09' OR month_name='September') AND tahun=2026 GROUP BY sa, cross_category")
for r in c.fetchall():
    print(r)

print("\n--- ANY TIRE IN 2026 ---")
c.execute("SELECT tahun, month_name, sa, cross_category, product_desc, qty, transaction_amount FROM raw_so WHERE cross_category LIKE '%TIRE%' AND tahun=2026")
for r in c.fetchall():
    print(r)
