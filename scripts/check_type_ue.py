import csv
from collections import defaultdict
import json

counts = defaultdict(lambda: {'total': 0, 'cpus_type': 0, 'sbi_type': 0, 'twc_type': 0, 'rtj_type': 0})
with open(r'data\live_input_pkb.csv', 'r', encoding='utf-8', errors='ignore') as f:
    reader = csv.reader(f)
    next(reader)
    for r in reader:
        if len(r) > 43 and r[2] == '2026':
            bln = r[1].strip()
            counts[bln]['total'] += 1
            t_ue = r[43].strip()
            if t_ue == 'CPUS':
                counts[bln]['cpus_type'] += 1
            elif t_ue == 'SBI':
                counts[bln]['sbi_type'] += 1
            elif t_ue == 'TWC':
                counts[bln]['twc_type'] += 1
            elif t_ue == 'RTJ':
                counts[bln]['rtj_type'] += 1

with open(r'data\dashboard_data.json', 'r', encoding='utf-8') as f:
    dash = json.load(f)

MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October']
MONTH_MAP = {'01':'January', '02':'February', '03':'March', '04':'April', '05':'May', '06':'June', '07':'July', '08':'August', '09':'September', '10':'October'}

print(f"{'Bln':<4} | {'Month':<10} | {'Total Live':<10} | {'Dash UE':<10} | {'CPUS type':<10} | {'Dash CPUS':<10} | {'SBI type':<8} | {'TWC':<5}")
print("-" * 80)
for b in sorted(counts.keys(), key=lambda x: int(x)):
    c = counts[b]
    b_pad = f"{int(b):02d}"
    m_name = MONTH_MAP.get(b_pad, b)
    d_m = dash['monthly_kpis']['2026'].get(m_name, {})
    d_ue = d_m.get('ue_total', '-')
    d_cpus = d_m.get('cpus', '-')
    print(f"{b:<4} | {m_name:<10} | {c['total']:<10} | {d_ue:<10} | {c['cpus_type']:<10} | {d_cpus:<10} | {c['sbi_type']:<8} | {c['twc_type']:<5}")
