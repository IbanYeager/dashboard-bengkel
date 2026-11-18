import sqlite3
from collections import defaultdict

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
SELECT sa, lookup_job, type_service
FROM raw_pkb
WHERE tahun = 2026
""")
rows = cur.fetchall()

sa_sbe = defaultdict(lambda: defaultdict(int))
for sa, j, s in rows:
    cat = map_sbe_km(j, s)
    if cat:
        sa_name = sa if sa in ['DIDIN', 'FICKY', 'ACEP'] else 'OTHER'
        sa_sbe[sa_name][cat] += 1
        sa_sbe['ALL'][cat] += 1

cats = ['1K', '10K', '20K', '30K', '40K', '50K', '60K', '70K', '80K', '90K', '100K', '100K UP']
header = f"{'SA':<10}" + "".join([f"{c:>8}" for c in cats]) + f"{'TOTAL':>10}"
print(header)
print("-" * len(header))
for sa in ['ALL', 'DIDIN', 'FICKY', 'ACEP', 'OTHER']:
    cnts = [sa_sbe[sa].get(c, 0) for c in cats]
    print(f"{sa:<10}" + "".join([f"{n:>8}" for n in cnts]) + f"{sum(cnts):>10}")
