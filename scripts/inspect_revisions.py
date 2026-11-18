import os
import sqlite3
import json

db_path = 'data/bengkel.db'
if not os.path.exists(db_path):
    print("bengkel.db not found!")
    exit()

conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("--- TABLES ---")
tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print(tables)

print("\n--- RAW_PKB COLUMNS ---")
cur.execute("PRAGMA table_info(raw_pkb)")
pkb_cols = [r[1] for r in cur.fetchall()]
print(pkb_cols)

print("\n--- RAW_SO COLUMNS ---")
cur.execute("PRAGMA table_info(raw_so)")
so_cols = [r[1] for r in cur.fetchall()]
print(so_cols)

print("\n--- DISTINCT SAs in RAW_PKB ---")
cur.execute("SELECT DISTINCT sa, COUNT(*) FROM raw_pkb GROUP BY sa")
print(cur.fetchall())

print("\n--- DISTINCT SAs in RAW_SO ---")
cur.execute("SELECT DISTINCT sa, COUNT(*) FROM raw_so GROUP BY sa")
print(cur.fetchall())

print("\n--- DISTINCT RING_AREA in RAW_PKB ---")
cur.execute("SELECT DISTINCT ring_area, COUNT(*) FROM raw_pkb GROUP BY ring_area")
print(cur.fetchall())

print("\n--- DISTINCT MODEL_SEGMENT in RAW_PKB ---")
cur.execute("SELECT DISTINCT model_segment, COUNT(*) FROM raw_pkb GROUP BY model_segment")
print(cur.fetchall())

print("\n--- DISTINCT TYPE_SERVICE in RAW_PKB ---")
cur.execute("SELECT DISTINCT type_service, COUNT(*) FROM raw_pkb GROUP BY type_service")
print(cur.fetchall())

print("\n--- DISTINCT TYPE_UE in RAW_PKB ---")
cur.execute("SELECT DISTINCT type_ue, COUNT(*) FROM raw_pkb GROUP BY type_ue")
print(cur.fetchall())

print("\n--- DISTINCT ARRIVAL_TYPE in RAW_PKB ---")
cur.execute("SELECT DISTINCT arrival_type, COUNT(*) FROM raw_pkb GROUP BY arrival_type")
print(cur.fetchall())

conn.close()
