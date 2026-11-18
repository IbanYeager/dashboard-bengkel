import sqlite3
from collections import defaultdict
import json

conn = sqlite3.connect('data/bengkel.db')
cur = conn.cursor()

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

cur.execute("""
SELECT tahun, month_name, sa, lookup_job, type_service
FROM raw_pkb
""")
rows = cur.fetchall()

agg = defaultdict(lambda: defaultdict(int))
for yr, m, sa, j, s in rows:
    cat = map_sbe_km(j, s)
    if cat:
        sa_code = sa if sa in ['DIDIN', 'FICKY', 'ACEP'] else 'OTHER'
        agg[(yr, m, sa_code)][cat] += 1
        agg[(yr, m, 'ALL')][cat] += 1

print(f"Total aggregated SBE (yr, month, sa) keys: {len(agg)}")

# Check with dashboard_data.json
with open('data/dashboard_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

ac = d.get('analytics_charts', [])
matched = 0
for r in ac:
    key = (r['year'], r['month_name'], r['sa'])
    if key in agg:
        matched += 1
print(f"Matched with analytics_charts records: {matched} / {len(ac)}")
for k, v in list(agg.items())[:5]:
    print(k, dict(v))
