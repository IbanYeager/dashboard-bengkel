import json

with open('data/dashboard_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print("=== MONTHLY KPIS 2026 ===")
kpis = d.get('monthly_kpis', {}).get('2026', {})
for m, v in sorted(kpis.items(), key=lambda x: ['January','February','March','April','May','June','July','August','September','October','November','December'].index(x[0]) if x[0] in ['January','February','March','April','May','June','July','August','September','October','November','December'] else 99):
    print(f"{m:10}: UE={v.get('ue_total'):4}, CPUS={v.get('cpus'):4}, Raw={v.get('raw_cpus'):4}, SBI={v.get('sbi_cpus'):3}, Rev={v.get('total_revenue'):13,.0f}, TCare={v.get('tcare_count'):3}, SBE={v.get('sbe_count'):3}")

print("\n=== WS MATRIX KABENG (46 KPIs) ===")
kb = d.get('ws_matrix_kabeng', {})
rows = kb.get('rows', [])
months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
print(f"{'No':3} {'KPI':30} " + " ".join([f"{m:>7}" for m in months]) + f" {'Total':>9}")
for r in rows:
    no = str(r.get('no'))
    if no in ['1', '2', '5', '7', '12', '13', '26', '34']:
        vals_str = " ".join([f"{v:>7.1f}" if isinstance(v, (int, float)) else f"{str(v):>7}" for v in r.get('months', [])])
        tot = f"{r.get('total'):>9.1f}" if isinstance(r.get('total'), (int, float)) else f"{str(r.get('total')):>9}"
        print(f"#{no:2} {r.get('kpi')[:30]:30} {vals_str} {tot}")
