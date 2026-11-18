import sqlite3
import json

conn = sqlite3.connect('data/bengkel.db')
c = conn.cursor()

print("="*70)
print("1. AUDIT RAW_PKB IN DATABASE")
print("="*70)
c.execute("SELECT count(*) FROM raw_pkb")
print("Total raw_pkb rows:", c.fetchone()[0])

c.execute("""
SELECT tahun, month_name, count(*), 
       count(CASE WHEN type_ue = 'CPUS' THEN 1 END) as cpus,
       sum(revenue) as total_rev
FROM raw_pkb
WHERE tahun = 2026
GROUP BY tahun, month_name
ORDER BY CASE month_name
    WHEN 'January' THEN 1 WHEN 'February' THEN 2 WHEN 'March' THEN 3
    WHEN 'April' THEN 4 WHEN 'May' THEN 5 WHEN 'June' THEN 6
    WHEN 'July' THEN 7 WHEN 'August' THEN 8 WHEN 'September' THEN 9
    WHEN 'October' THEN 10 WHEN 'November' THEN 11 WHEN 'December' THEN 12
    ELSE 13 END
""")
print("\n2026 Monthly Summary in raw_pkb:")
for r in c.fetchall():
    print(f"  {r[1]:10}: Total UE={r[2]:4d}, CPUS={r[3]:4d}, Revenue=Rp {r[4]:,.0f}")

print("\n" + "="*70)
print("2. AUDIT RAW_SO IN DATABASE")
print("="*70)
c.execute("SELECT count(*) FROM raw_so")
print("Total raw_so rows:", c.fetchone()[0])

c.execute("""
SELECT tahun, month_name, count(*), sum(transaction_amount) as total_rev
FROM raw_so
WHERE tahun = 2026
GROUP BY tahun, month_name
ORDER BY CASE month_name
    WHEN 'January' THEN 1 WHEN 'February' THEN 2 WHEN 'March' THEN 3
    WHEN 'April' THEN 4 WHEN 'May' THEN 5 WHEN 'June' THEN 6
    WHEN 'July' THEN 7 WHEN 'August' THEN 8 WHEN 'September' THEN 9
    WHEN 'October' THEN 10 WHEN 'November' THEN 11 WHEN 'December' THEN 12
    ELSE 13 END
""")
print("\n2026 Monthly Summary in raw_so:")
for r in c.fetchall():
    print(f"  {r[1]:10}: Records={r[2]:6d}, Total Amount=Rp {r[3]:,.0f}")

print("\n" + "="*70)
print("3. DISTINCT CROSS CATEGORIES IN RAW_SO (2026)")
print("="*70)
c.execute("""
SELECT cross_category, count(*), sum(transaction_amount)
FROM raw_so
WHERE tahun = 2026 AND cross_category != ''
GROUP BY cross_category
ORDER BY sum(transaction_amount) DESC
""")
for r in c.fetchall():
    print(f"  {r[0]:25}: count={r[1]:5d}, sum=Rp {r[2]:,.0f}")

print("\n" + "="*70)
print("4. SA PERFORMANCE IN 2026 RAW_SO (SEPTEMBER & OCTOBER)")
print("="*70)
c.execute("""
SELECT month_name, sa, count(*), sum(transaction_amount)
FROM raw_so
WHERE tahun = 2026 AND month_name IN ('September', 'October')
GROUP BY month_name, sa
ORDER BY month_name, sa
""")
for r in c.fetchall():
    print(f"  {r[0]:10} | {r[1]:10}: records={r[2]:5d}, sum=Rp {r[3]:,.0f}")
