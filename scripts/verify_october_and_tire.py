import json

with open('data/dashboard_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print("=== MONTHLY KPIS 2026 ===")
kpis_2026 = d.get('monthly_kpis', {}).get('2026', {})
print("Months in 2026:", list(kpis_2026.keys()))
if 'October' in kpis_2026:
    print("October 2026 KPI:", json.dumps(kpis_2026['October'], indent=2))
else:
    print("ERROR: October not in monthly_kpis['2026']!")

print("\n=== TARGETS 2026 ===")
targets_2026 = d.get('targets', {}).get('2026', {})
print("Targets in 2026:", list(targets_2026.keys()))
if 'October' in targets_2026:
    print("October 2026 Targets:", json.dumps(targets_2026['October'], indent=2))

print("\n=== SA PERFORMANCE OCTOBER 2026 ===")
sa_perf = [x for x in d.get('sa_performance', []) if x.get('year') == 2026 and x.get('month_name') == 'October']
print("SA Performance Oct 2026:", json.dumps(sa_perf, indent=2))

print("\n=== SA CROSS SELLING SEPTEMBER 2026 TIRE ===")
tire_sep = [x for x in d.get('sa_cross_selling', []) if x.get('year') == 2026 and x.get('month_name') == 'September' and x.get('category') == 'TIRE']
print("TIRE Sep 2026 in sa_cross_selling:", json.dumps(tire_sep, indent=2))

print("\n=== SA CROSS SELLING OCTOBER 2026 ===")
oct_cross = [x for x in d.get('sa_cross_selling', []) if x.get('year') == 2026 and x.get('month_name') == 'October']
print(f"Total October cross selling records: {len(oct_cross)}")
for x in oct_cross[:10]:
    print(x)
