import sqlite3

conn = sqlite3.connect('data/bengkel.db')
cur = conn.cursor()

cur.execute("SELECT pkb_no, sa, revenue, type_service, type_ue FROM raw_pkb WHERE tahun=2026 LIMIT 5")
rows = cur.fetchall()
print("Sample PKB rows:")
for r in rows:
    pkb = r[0]
    cur.execute("SELECT SUM(qty), SUM(transaction_amount) FROM raw_so WHERE wo = ?", (pkb,))
    so_sum = cur.fetchone()
    print(f"PKB: {pkb:<15} | SA: {r[1]:<6} | PKB Rev: {r[2]:>12,.0f} | SO Rev: {so_sum[1] if so_sum and so_sum[1] else 0:>12,.0f}")

conn.close()
