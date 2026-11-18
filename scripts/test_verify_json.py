import json

with open('data/dashboard_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

ac = d.get('analytics_charts', [])
rec_2026 = [r for r in ac if r.get('year') == 2026 and r.get('sa') == 'ALL']
print(f"2026 ALL months count: {len(rec_2026)}")
for r in rec_2026:
    s = sum(r['type_sbe'].values())
    print(f"{r['month_name']:<12}: sum={s} | {r['type_sbe']}")
