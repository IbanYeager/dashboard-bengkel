import json

with open('data/dashboard_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

for r in d.get('ws_matrix_kabeng', {}).get('rows', []):
    if str(r.get('no')) in ['1', '2', '5', '7', '8', '12', '13', '14']:
        print(f"No {r['no']}: {r['kpi']} ({r['satuan']}) -> Jan: {r['months'][0]}, Aug: {r['months'][7]}, Sep: {r['months'][8]}")

jan_kpis = d.get('monthly_kpis', {}).get('2026', {}).get('January', {})
aug_kpis = d.get('monthly_kpis', {}).get('2026', {}).get('August', {})
print("\nMonthly KPIs comparison:")
print("Jan monthly_kpis:", jan_kpis)
print("Aug monthly_kpis:", aug_kpis)
