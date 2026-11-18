import json

with open('data/dashboard_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Let's check for Year = 2026, Month = 'all', SA = 'all'
# 1. Executive KPI Total Revenue
monthly_kpis = data.get('monthly_kpis', {}).get('2026', {})
tot_rev_kpi = sum(m.get('total_revenue', 0) for m in monthly_kpis.values())
tot_cpus_rev_kpi = sum(m.get('cpus_revenue', 0) for m in monthly_kpis.values())
tot_ue_kpi = sum(m.get('ue_total', 0) for m in monthly_kpis.values())
tot_cpus_kpi = sum(m.get('cpus', 0) for m in monthly_kpis.values())
tot_raw_cpus_kpi = sum(m.get('raw_cpus', 0) for m in monthly_kpis.values())

print("1. Executive Summary KPIs (2026 all):")
print(f"   Total UE: {tot_ue_kpi}")
print(f"   CPUS (with SBI added): {tot_cpus_kpi}")
print(f"   Raw CPUS: {tot_raw_cpus_kpi}")
print(f"   Total Revenue: {tot_rev_kpi:,.0f}")
print(f"   CPUS Revenue: {tot_cpus_rev_kpi:,.0f}")

# 2. SA Performance (2026 all)
sa_perf = data.get('sa_performance', [])
sa_rev_sum = sum(item.get('revenue', 0) for item in sa_perf if str(item.get('year')) == '2026')
sa_ue_sum = sum(item.get('ue', 0) for item in sa_perf if str(item.get('year')) == '2026')
sa_cpus_sum = sum(item.get('cpus', 0) for item in sa_perf if str(item.get('year')) == '2026')
print("\n2. SA Performance Table (2026 all):")
print(f"   SA Total UE: {sa_ue_sum}")
print(f"   SA Total CPUS: {sa_cpus_sum}")
print(f"   SA Total Revenue: {sa_rev_sum:,.0f}")

# 3. Breakdown Table (2026 all)
breakdown = data.get('breakdown', [])
bd_2026 = [b for b in breakdown if str(b.get('year')) == '2026']
bd_cpus_u = sum(b.get('units', 0) for b in bd_2026 if b.get('type_ue') == 'CPUS')
bd_cpus_r = sum(b.get('revenue', 0) for b in bd_2026 if b.get('type_ue') == 'CPUS')
bd_all_u = sum(b.get('units', 0) for b in bd_2026)
bd_all_r = sum(b.get('revenue', 0) for b in bd_2026)
print("\n3. Operational Breakdown (2026 all):")
print(f"   All Units: {bd_all_u}")
print(f"   CPUS Units: {bd_cpus_u}")
print(f"   CPUS Revenue: {bd_cpus_r:,.0f}")
print(f"   All Revenue: {bd_all_r:,.0f}")

# Breakdown by categories as rendered in dashboard.js:
sbe_r = sum(b.get('revenue', 0) for b in bd_2026 if b.get('type_service') == 'SBE')
gr_other_r = sum(b.get('revenue', 0) for b in bd_2026 if b.get('type_service') == 'GR OTHER')
gr_oil_r = sum(b.get('revenue', 0) for b in bd_2026 if b.get('type_service') == 'GR OIL')
twc_r = sum(b.get('revenue', 0) for b in bd_2026 if b.get('type_service') == 'TWC' or b.get('type_ue') == 'TWC')
sbi_r = sum(b.get('revenue', 0) for b in bd_2026 if b.get('type_service') == 'SBI' or b.get('type_ue') == 'SBI')
print(f"   SBE Rev: {sbe_r:,.0f}")
print(f"   GR OTHER Rev: {gr_other_r:,.0f}")
print(f"   GR OIL Rev: {gr_oil_r:,.0f}")
print(f"   TWC Rev: {twc_r:,.0f}")
print(f"   SBI Rev: {sbi_r:,.0f}")
print(f"   Sum of Service Revs: {(sbe_r + gr_other_r + gr_oil_r + twc_r + sbi_r):,.0f}")

# 4. Cross Selling Total Revenue
cross = data.get('cross_selling', [])
cross_rev = sum(c.get('revenue', 0) for c in cross if str(c.get('year')) == '2026')
cross_qty = sum(c.get('qty', 0) for c in cross if str(c.get('year')) == '2026')
print("\n4. Cross Selling Table (2026 all):")
print(f"   Total Cross Revenue: {cross_rev:,.0f}")
print(f"   Total Cross Qty: {cross_qty}")
