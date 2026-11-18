import json

with open('data/dashboard_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("="*60)
print("1. SEPTEMBER 2026 AUDIT")
print("="*60)
sep_kpi = data['monthly_kpis']['2026']['September']
print("September KPIs:", sep_kpi)

# Check SA Performance in Sep 2026
sa_sep = [x for x in data['sa_performance'] if x['year'] == 2026 and x['month_name'] == 'September']
for sa in sa_sep:
    print(f"  SA {sa['sa']}: UE={sa['ue']}, CPUS={sa['cpus']}, Rev=Rp {sa['revenue']:,.0f}, TCare={sa['tcare_ue']}")

# Check Cross Selling in Sep 2026
tire_sep = [x for x in data['sa_cross_selling'] if x['year'] == 2026 and x['month_name'] == 'September' and x['category'] == 'TIRE']
print("\nTIRE Sales in September 2026 by SA:")
tot_tire_rev = sum(x['revenue'] for x in tire_sep)
for t in tire_sep:
    share = (t['revenue'] / tot_tire_rev) * 100 if tot_tire_rev > 0 else 0
    # Radar formula: (share / 33.333%) * 100%
    ach = min(150, round((share / (100/3)) * 100, 1))
    print(f"  {t['sa']}: Qty={t['qty']}, Rev=Rp {t['revenue']:,.0f}, Share={share:.1f}%, Ach={ach}%")

print("\n" + "="*60)
print("2. OCTOBER 2026 AUDIT")
print("="*60)
oct_kpi = data['monthly_kpis']['2026']['October']
print("October KPIs:")
print(f"  UE Total: {oct_kpi['ue_total']} Unit")
print(f"  CPUS: {oct_kpi['cpus']} Unit")
print(f"  Total Revenue: Rp {oct_kpi['total_revenue']:,.0f}")
print(f"  CPUS Revenue: Rp {oct_kpi['cpus_revenue']:,.0f}")
print(f"  T-Care Count: {oct_kpi['tcare_count']}")
print(f"  SBE Count: {oct_kpi['sbe_count']}")

oct_tgt = data['targets']['2026']['October']
print(f"\nOctober Targets:")
print(f"  Target CPUS: {oct_tgt['cpus']}")
print(f"  Target Revenue: Rp {oct_tgt['revenue_total']:,.0f}")

print("\nOctober SA Performance:")
sa_oct = [x for x in data['sa_performance'] if x['year'] == 2026 and x['month_name'] == 'October']
for sa in sa_oct:
    print(f"  SA {sa['sa']}: UE={sa['ue']}, CPUS={sa['cpus']}, Rev=Rp {sa['revenue']:,.0f}, TCare={sa['tcare_ue']}, SBE={sa['sbe_ue']}")

oct_cross = [x for x in data['sa_cross_selling'] if x['year'] == 2026 and x['month_name'] == 'October']
print(f"\nOctober Cross Selling Total Categories: {len(oct_cross)}")
tot_cross_rev = sum(x['revenue'] for x in oct_cross)
print(f"Total October Cross Selling Omset: Rp {tot_cross_rev:,.0f}")
