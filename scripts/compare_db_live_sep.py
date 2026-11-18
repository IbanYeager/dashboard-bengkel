import sqlite3
import csv
import re

def clean_num(val):
    if val is None or val == "":
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    if not s or s in ['-', '#REF!', '#N/A', '#VALUE!', 'FALSE', 'TRUE']:
        return 0.0
    s = re.sub(r'^(?:Rp\.?|RP\.?|rp\.?)\s*', '', s, flags=re.IGNORECASE).strip()
    if '.' in s and ',' in s:
        if s.rfind('.') < s.rfind(','):
            s = s.replace('.', '').replace(',', '.')
        else:
            s = s.replace(',', '')
    elif '.' in s:
        dots = s.count('.')
        if dots > 1:
            s = s.replace('.', '')
        else:
            parts = s.split('.')
            if len(parts[1]) == 3 and len(parts[0]) <= 3:
                s = s.replace('.', '')
    elif ',' in s:
        commas = s.count(',')
        if commas > 1:
            s = s.replace(',', '')
        else:
            parts = s.split(',')
            if len(parts[1]) == 3 and len(parts[0]) <= 3:
                s = s.replace(',', '')
            else:
                s = s.replace(',', '.')

    s = re.sub(r'[^0-9.-]', '', s)
    try:
        return float(s)
    except:
        return 0.0

conn = sqlite3.connect('data/bengkel.db')
cur = conn.cursor()
cur.execute("SELECT pkb_no, revenue FROM raw_pkb WHERE tahun=2026 AND month_name='September'")
db_pkbs = dict(cur.fetchall())

live_pkbs = {}
with open('data/live_input_pkb.csv', 'r', encoding='utf-8', errors='ignore') as f:
    reader = csv.reader(f)
    next(reader)
    for r in reader:
        if len(r) > 57 and r[2].strip() == '2026' and r[1].strip() in ['9', '09']:
            pkb = r[10].strip()
            rev = clean_num(r[57])
            live_pkbs[pkb] = (rev, r[57])

print(f"September PKBs in DB: {len(db_pkbs)}")
print(f"September PKBs in Live: {len(live_pkbs)}")

diffs = []
for pkb, db_rev in db_pkbs.items():
    if pkb in live_pkbs:
        l_rev, raw_str = live_pkbs[pkb]
        if abs(db_rev - l_rev) > 1.0:
            diffs.append((pkb, db_rev, l_rev, raw_str))
    else:
        diffs.append((pkb, db_rev, 'MISSING', ''))

print(f"Differences found: {len(diffs)}")
for d in diffs[:15]:
    print(f"PKB: {d[0]} | DB: {d[1]:>12,.0f} | Live: {str(d[2]):>12} | Raw: {d[3]}")

# Also check sum of diffs
sum_diff = sum(d[1] - (d[2] if isinstance(d[2], (int, float)) else 0) for d in diffs)
print(f"Total diff sum: {sum_diff:,.0f}")
