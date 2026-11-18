import sqlite3

conn = sqlite3.connect('bengkel.db')
c = conn.cursor()

# Check tables
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables:", [r[0] for r in c.fetchall()])

# Check pkb transactions in 2026 by month
try:
    c.execute("""
        SELECT strftime('%Y-%m', tgl_pkb) as ym, count(*), sum(total_revenue)
        FROM pkb_transactions
        WHERE tgl_pkb >= '2026-01-01'
        GROUP BY ym
        ORDER BY ym;
    """)
    print("\nPKB Transactions by month (pkb_transactions):")
    for r in c.fetchall():
        print(r)
except Exception as e:
    print("Error querying pkb_transactions:", e)

# Check all tables with 'pkb' or 'trans'
for tbl in ['transaksi_pkb', 'pkb', 'raw_pkb']:
    try:
        c.execute(f"SELECT count(*) FROM {tbl};")
        print(f"Table {tbl} count:", c.fetchone()[0])
    except:
        pass

conn.close()
