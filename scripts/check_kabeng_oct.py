import json

with open('data/dashboard_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

kabeng = d.get('ws_matrix_kabeng', {})
rows = kabeng.get('rows', [])
print(f'Total Kabeng rows: {len(rows)}')
for r in rows[:15]:
    kpi = r.get('kpi')
    months = r.get('months', [])
    sep_v = months[8] if len(months)>8 else 'N/A'
    oct_v = months[9] if len(months)>9 else 'N/A'
    print(f"{r.get('no')}. {kpi}: Sep={sep_v}, Oct={oct_v}")
