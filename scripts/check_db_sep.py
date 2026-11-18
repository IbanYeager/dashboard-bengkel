import sqlite3
import json

conn = sqlite3.connect('data/bengkel.db')
c = conn.cursor()

# Check raw_pkb
print("--- DB raw_pkb counts for 2026 ---")
c.execute("SELECT month_name, COUNT(*), SUM(CASE WHEN type_ue = 'CPUS' THEN 1 ELSE 0 END), SUM(revenue) FROM raw_pkb WHERE tahun = 2026 GROUP BY month_name")
for row in c.fetchall():
    print(row)

# Check dashboard_data.json
print("\n--- dashboard_data.json monthly_kpis 2026 ---")
with open('data/dashboard_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

kpis_2026 = d.get('monthly_kpis', {}).get('2026', {})
for m, v in kpis_2026.items():
    print(m, "UE:", v.get('ue_total'), "CPUS:", v.get('cpus_total'), "Rev:", v.get('revenue_total'))

print("\n--- dashboard_data.json targets 2026 ---")
targets_2026 = d.get('targets', {}).get('2026', {})
for m, v in targets_2026.items():
    print(m, v)
