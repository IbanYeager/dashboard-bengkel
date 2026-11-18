import sqlite3

conn = sqlite3.connect('data/bengkel.db')
cur = conn.cursor()

cur.execute("SELECT COUNT(1) FROM raw_so WHERE tahun=2026 AND month_name='October'")
print("October 2026 raw_so count:", cur.fetchone()[0])

cur.execute("""
SELECT sa, cross_category, SUM(qty), SUM(transaction_amount) 
FROM raw_so 
WHERE tahun=2026 AND month_name='October' AND cross_category='TIRE' 
GROUP BY sa
""")
print("TIRE in raw_so:", cur.fetchall())

cur.execute("SELECT DISTINCT CAST(tanggal AS INT) FROM raw_so WHERE tahun=2026 AND month_name='October' ORDER BY 1")
print("Days in raw_so October 2026:", [r[0] for r in cur.fetchall()])
