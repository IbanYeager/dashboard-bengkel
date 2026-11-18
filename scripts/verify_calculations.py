import json

with open(r"c:\laragon\www\dashboard_bengkel\data\dashboard_data.json", 'r', encoding='utf-8') as f:
    data = json.load(f)

# 1. Test Q1 2026 CPUS and Revenue
q1_months = ['January', 'February', 'March']
cpus_2026_q1 = sum([data['monthly_kpis'].get('2026', {}).get(m, {}).get('cpus', 0) for m in q1_months])
raw_cpus_2026_q1 = sum([data['monthly_kpis'].get('2026', {}).get(m, {}).get('raw_cpus', 0) for m in q1_months])
sbi_cpus_2026_q1 = sum([data['monthly_kpis'].get('2026', {}).get(m, {}).get('sbi_cpus', 0) for m in q1_months])

tgt_cpus_2026_q1 = sum([data['targets'].get('2026', {}).get(m, {}).get('cpus', 0) for m in q1_months])
rev_2026_q1 = sum([data['monthly_kpis'].get('2026', {}).get(m, {}).get('cpus_revenue', 0) for m in q1_months])
tgt_rev_2026_q1 = sum([data['targets'].get('2026', {}).get(m, {}).get('revenue_total', 0) for m in q1_months])

cpus_2025_q1 = sum([data['monthly_kpis'].get('2025', {}).get(m, {}).get('cpus', 0) for m in q1_months])
rev_2025_q1 = sum([data['monthly_kpis'].get('2025', {}).get(m, {}).get('cpus_revenue', 0) for m in q1_months])

print(f"=== VERIFICATION REPORT ===")
print(f"Q1 2026 Raw CPUS: {raw_cpus_2026_q1}")
print(f"Q1 2026 SBI CPUS: {sbi_cpus_2026_q1} (Jan: 13, Feb: 8, Mar: 57)")
print(f"Q1 2026 Total Actual CPUS: {cpus_2026_q1} (Expected from Excel KPI TREE row 16 / DASHBOARD: 2284) -> {'MATCH!' if cpus_2026_q1 == 2284 else 'DIFF'}")
print(f"Q1 2026 Target CPUS: {tgt_cpus_2026_q1} (Expected from Excel: 1993) -> {'MATCH!' if tgt_cpus_2026_q1 == 1993 else 'DIFF'}")
print(f"Q1 2026 CPUS Achieve: {cpus_2026_q1 / tgt_cpus_2026_q1 * 100:.3f}% (Expected: 114.601%)")

# Full 2026 YTD
ytd_months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August']
cpus_2026_ytd = sum([data['monthly_kpis'].get('2026', {}).get(m, {}).get('cpus', 0) for m in ytd_months])
tgt_cpus_2026_ytd = sum([data['targets'].get('2026', {}).get(m, {}).get('cpus', 0) for m in ytd_months])
print(f"2026 YTD Actual CPUS: {cpus_2026_ytd} (Expected from Excel: 6042) -> {'MATCH!' if cpus_2026_ytd == 6042 else 'DIFF'}")
print(f"2026 YTD Target CPUS: {tgt_cpus_2026_ytd} (Expected from Excel: 5397) -> {'MATCH!' if tgt_cpus_2026_ytd == 5397 else 'DIFF'}")

# Full 2025
all_months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
cpus_2025_total = sum([data['monthly_kpis'].get('2025', {}).get(m, {}).get('cpus', 0) for m in all_months])
tgt_cpus_2025_total = sum([data['targets'].get('2025', {}).get(m, {}).get('cpus', 0) for m in all_months])
print(f"2025 Total Actual CPUS: {cpus_2025_total} (Expected from Excel: 8544) -> {'MATCH!' if cpus_2025_total == 8544 else 'DIFF'}")
print(f"2025 Total Target CPUS: {tgt_cpus_2025_total} (Expected from Excel: 7230) -> {'MATCH!' if tgt_cpus_2025_total == 7230 else 'DIFF'}")

# Verify Analytics Charts
print("\n=== ANALYTICS CHARTS VERIFICATION ===")
analytics = data.get('analytics_charts', [])
print(f"Total analytics records: {len(analytics)}")
sample_2026_jul = next((x for x in analytics if x['year'] == 2026 and x['month_name'] == 'July' and x['sa'] == 'ALL'), None)
if sample_2026_jul:
    print("July 2026 (ALL):")
    print("  CUST AREA:", sample_2026_jul['cust_area'])
    print("  TYPE CUST:", sample_2026_jul['type_cust'])
    print("  KOMPOSISI UE:", sample_2026_jul['komposisi_ue'])
    print("  KOMPOSISI CPUS:", sample_2026_jul['komposisi_cpus'])
    print("  TYPE SBE:", sample_2026_jul['type_sbe'])
    print("  CAR SEGMENT:", sample_2026_jul['car_segment'])
