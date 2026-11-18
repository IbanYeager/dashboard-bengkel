import sqlite3

conn = sqlite3.connect('data/bengkel.db')
cur = conn.cursor()

print("=== REVENUE COMPARISONS FOR 2026 ===")

# 1. Total revenue in raw_pkb by month
print("\n--- RAW_PKB by Month (2026) ---")
cur.execute("""
SELECT month_name, 
       COUNT(id) as total_ue,
       COUNT(CASE WHEN type_ue = 'CPUS' THEN 1 END) as cpus_count,
       SUM(revenue) as total_rev,
       SUM(CASE WHEN type_ue = 'CPUS' THEN revenue ELSE 0 END) as cpus_rev
FROM raw_pkb
WHERE tahun = 2026
GROUP BY month_name
ORDER BY MIN(id)
""")
for r in cur.fetchall():
    print(f"Month: {r[0]:<10} | UE: {r[1]:<5} | CPUS: {r[2]:<5} | TotRev: {r[3]:>15,.0f} | CPUSRev: {r[4]:>15,.0f}")

# 2. Total revenue in raw_so by month
print("\n--- RAW_SO by Month (2026) ---")
cur.execute("""
SELECT month_name, 
       COUNT(id) as total_so_rows,
       SUM(qty) as total_qty,
       SUM(transaction_amount) as total_amount
FROM raw_so
WHERE tahun = 2026
GROUP BY month_name
ORDER BY MIN(id)
""")
for r in cur.fetchall():
    print(f"Month: {r[0]:<10} | SO Rows: {r[1]:<6} | Qty: {r[2]:<8.1f} | TotAmount: {r[3]:>15,.0f}")

# 3. SA Performance Revenue in raw_pkb vs raw_so for 2026
print("\n--- SA Revenue in RAW_PKB vs RAW_SO (2026 Total) ---")
cur.execute("""
SELECT sa, COUNT(id) as ue, SUM(revenue) as pkb_rev
FROM raw_pkb
WHERE tahun = 2026
GROUP BY sa
""")
pkb_sa = {r[0]: (r[1], r[2]) for r in cur.fetchall()}

cur.execute("""
SELECT sa, COUNT(id) as so_count, SUM(qty) as total_qty, SUM(transaction_amount) as so_rev
FROM raw_so
WHERE tahun = 2026
GROUP BY sa
""")
so_sa = {r[0]: (r[1], r[2], r[3]) for r in cur.fetchall()}

all_sas = sorted(list(set(list(pkb_sa.keys()) + list(so_sa.keys()))))
for sa in all_sas:
    p = pkb_sa.get(sa, (0, 0))
    s = so_sa.get(sa, (0, 0, 0))
    print(f"SA: {sa:<8} | PKB UE: {p[0]:<5} | PKB Rev: {p[1]:>14,.0f} | SO Rev: {s[2]:>14,.0f}")

conn.close()
