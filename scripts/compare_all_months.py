import json

with open('data/dashboard_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

kb = d.get('ws_matrix_kabeng', {})
kb_rows = {str(r.get('no')): r for r in kb.get('rows', [])}

months_order = ['January','February','March','April','May','June','July','August','September','October','November','December']
months_short = ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des']

print("=== COMPARISON FOR 2026: monthly_kpis vs ws_matrix_kabeng ===")
print(f"{'Month':10} | {'KPI UE':>7} {'WS UE':>7} | {'KPI CPUS':>8} {'WS CPUS':>8} | {'KPI Rev (Jt)':>12} {'WS Rev (Jt)':>12} | {'KPI SBE':>7} {'WS SBE':>7} | {'KPI TC':>7} {'WS TC':>7}")
print("-" * 105)

ue_row = kb_rows.get('1', {}).get('months', [])
cpus_row = kb_rows.get('2', {}).get('months', [])
sbe_row = kb_rows.get('5', {}).get('months', [])
tc_row = kb_rows.get('7', {}).get('months', [])
rev_row = kb_rows.get('12', {}).get('months', [])

kpis_2026 = d.get('monthly_kpis', {}).get('2026', {})

for idx, m in enumerate(months_order):
    mk = kpis_2026.get(m, {})
    k_ue = mk.get('ue_total', 0)
    k_cpus = mk.get('cpus', 0)
    k_rev = (mk.get('total_revenue', 0) or 0) / 1_000_000
    k_sbe = mk.get('sbe_count', 0)
    k_tc = mk.get('tcare_count', 0)
    
    w_ue = ue_row[idx] if idx < len(ue_row) else 0
    w_cpus = cpus_row[idx] if idx < len(cpus_row) else 0
    w_rev = ((rev_row[idx] or 0) * 1000) / 1_000_000 if idx < len(rev_row) and rev_row[idx] else 0
    w_sbe = sbe_row[idx] if idx < len(sbe_row) else 0
    w_tc = tc_row[idx] if idx < len(tc_row) else 0
    
    print(f"{m:10} | {k_ue:7} {w_ue:7} | {k_cpus:8} {w_cpus:8} | {k_rev:12.1f} {w_rev:12.1f} | {k_sbe:7} {w_sbe:7} | {k_tc:7} {w_tc:7}")

print("\n=== 2025 monthly_kpis ===")
kpis_2025 = d.get('monthly_kpis', {}).get('2025', {})
for m in months_order:
    mk = kpis_2025.get(m, {})
    if mk:
        print(f"{m:10}: UE={mk.get('ue_total'):4}, CPUS={mk.get('cpus'):4}, Rev={mk.get('total_revenue',0):13,.0f}, SBE={mk.get('sbe_count'):3}, TC={mk.get('tcare_count'):3}")

print("\n=== 2024 monthly_kpis ===")
kpis_2024 = d.get('monthly_kpis', {}).get('2024', {})
for m in months_order:
    mk = kpis_2024.get(m, {})
    if mk:
        print(f"{m:10}: UE={mk.get('ue_total'):4}, CPUS={mk.get('cpus'):4}, Rev={mk.get('total_revenue',0):13,.0f}, SBE={mk.get('sbe_count'):3}, TC={mk.get('tcare_count'):3}")
