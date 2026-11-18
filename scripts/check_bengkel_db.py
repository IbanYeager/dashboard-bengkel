import sqlite3

conn = sqlite3.connect('bengkel.db')
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("Tables:", tables)

for t in tables:
    name = t[0]
    count = conn.execute(f"SELECT count(*) FROM {name}").fetchone()[0]
    print(f"Table {name}: {count} rows")
