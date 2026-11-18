import sqlite3
import json
from collections import defaultdict

def map_sbe_km(lookup_job, type_service):
    j = str(lookup_job or '').strip().upper()
    s = str(type_service or '').strip().upper()
    if 'SBE' not in s and 'SBI' not in s and j not in ['1K', '5K LOW', '10K', '20K', '30K', '40K', '50K', '60K', '70K', '80K', '90K', '100K']:
        return None
    if j in ['1K', '5K LOW'] or s == 'SBI':
        return '1K'
    if j == '10K':
        return '10K'
    if j in ['20K', '30K', '40K', '50K', '60K', '70K', '80K', '90K', '100K']:
        return j
    if 'SBE' in s:
        return '100K UP'
    return None

conn = sqlite3.connect('data/bengkel.db')
cur = conn.cursor()
cur.execute("SELECT tahun, month_name, sa, lookup_job, type_service FROM raw_pkb")
rows = cur.fetchall()

agg = defaultdict(lambda: defaultdict(int))
for yr, m, sa, j, s in rows:
    cat = map_sbe_km(j, s)
    if cat:
        sa_code = sa if sa in ['DIDIN', 'FICKY', 'ACEP'] else 'OTHER'
        agg[(yr, m, sa_code)][cat] += 1
        agg[(yr, m, 'ALL')][cat] += 1

print(f"Aggregated SBE combinations: {len(agg)}")

with open('data/dashboard_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

ac = data.get('analytics_charts', [])
updated_count = 0
for r in ac:
    key = (r.get('year'), r.get('month_name'), r.get('sa'))
    if key in agg:
        r['type_sbe'] = dict(agg[key])
        updated_count += 1
    else:
        r['type_sbe'] = {}

print(f"Updated {updated_count} / {len(ac)} records in analytics_charts.")

# Verify 2026 July ALL
for r in ac:
    if r.get('year') == 2026 and r.get('month_name') == 'July' and r.get('sa') == 'ALL':
        print("Sample 2026 July ALL type_sbe:", r['type_sbe'])
        print("Sum of July SBE units:", sum(r['type_sbe'].values()))

with open('data/dashboard_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)

print("Successfully saved updated data/dashboard_data.json")
