import urllib.request
import csv
import io
import json

url = 'https://docs.google.com/spreadsheets/d/1b60d-JO50LU4KyywuULokmDIU7z3Ts_1/gviz/tq?tqx=out:csv&gid=2141708170'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
content = urllib.request.urlopen(req).read().decode('utf-8')
reader = list(csv.reader(io.StringIO(content)))
header = reader[0]

print('Total rows in ATTACKLIST:', len(reader) - 1)
print('Columns:', {i: h for i, h in enumerate(header[:15])})

# Analyze by Quartal and Bulan as well
overall = {}
by_quartal = {}

for r in reader[1:]:
    if len(r) > 8:
        q = r[0].strip()
        k1 = r[1].strip()
        k2 = r[2].strip()
        k3 = r[3].strip()
        cai = r[4].strip().upper()
        j = r[8].strip()
        bulan = r[15].strip() if len(r) > 15 else ''
        
        if j not in overall:
            overall[j] = {'total': 0, 'cai': 0, 'not_cai': 0, 'pct': 0}
        overall[j]['total'] += 1
        if cai == 'CAI':
            overall[j]['cai'] += 1
        elif cai == 'NOT CAI':
            overall[j]['not_cai'] += 1

print("\n--- OVERALL JUDGEMENT CUST (ALL ROWS) ---")
for k, v in sorted(overall.items(), key=lambda x: -x[1]['total']):
    v['pct'] = round(v['cai'] / v['total'] * 100, 1) if v['total'] > 0 else 0
    print(f"{k:35} | Total: {v['total']:5} | CAI: {v['cai']:5} | NOT CAI: {v['not_cai']:5} | Pct: {v['pct']}%")

# Also check for Quartal 3 (or September specifically)
print("\n--- BY QUARTAL FOR EXPIRED SOON ---")
q_stats = {}
for r in reader[1:]:
    if len(r) > 8:
        q = r[0].strip()
        j = r[8].strip()
        cai = r[4].strip().upper()
        if 'EXPIRED SOON' in j.upper():
            key = f"Q{q} - {j}"
            if key not in q_stats:
                q_stats[key] = {'total': 0, 'cai': 0, 'not_cai': 0}
            q_stats[key]['total'] += 1
            if cai == 'CAI':
                q_stats[key]['cai'] += 1
            elif cai == 'NOT CAI':
                q_stats[key]['not_cai'] += 1

for k, v in sorted(q_stats.items()):
    pct = round(v['cai'] / v['total'] * 100, 1) if v['total'] > 0 else 0
    print(f"{k:45} | Total: {v['total']:4} | CAI: {v['cai']:4} | Pct: {pct}%")
