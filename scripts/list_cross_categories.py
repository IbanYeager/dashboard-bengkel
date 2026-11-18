import sqlite3

conn = sqlite3.connect('data/bengkel.db')
cur = conn.cursor()

cur.execute("SELECT cross_category, COUNT(*), SUM(transaction_amount) FROM raw_so GROUP BY cross_category ORDER BY COUNT(*) DESC")
rows = cur.fetchall()
print(f"{'Category':<25} | {'Count':<8} | {'Revenue':>15}")
print("-" * 55)
for r in rows:
    cat = r[0] if r[0] else '(EMPTY)'
    cnt = r[1]
    rev = r[2] if r[2] else 0
    print(f"{cat:<25} | {cnt:<8} | {rev:>15,.0f}")

conn.close()
