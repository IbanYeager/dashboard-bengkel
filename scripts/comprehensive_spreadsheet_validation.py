import urllib.request, csv, io, json, re
from collections import defaultdict

print("=" * 70)
print("COMPREHENSIVE DATA VALIDATION: SPREADSHEETS vs DASHBOARD")
print("=" * 70)

# 1. Fetch Input PKB
URL_PKB = "https://docs.google.com/spreadsheets/d/1b60d-JO50LU4KyywuULokmDIU7z3Ts_1/export?format=csv&gid=177004909"
print(f"1. Downloading Input PKB (GID 177004909)...")
req = urllib.request.Request(URL_PKB, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=90) as resp:
    pkb_csv = resp.read().decode('utf-8', errors='replace')

reader = csv.reader(io.StringIO(pkb_csv))
pkb_header = next(reader)

def clean_rev(s):
    if not s or s.strip() in ['-', '#REF!', '#N/A', '#VALUE!', 'FALSE', 'TRUE', '']:
        return 0.0
    s = re.sub(r'^(?:Rp\.?|RP\.?|rp\.?)\s*', '', s.strip()).strip()
    if '.' in s and ',' in s:
        if s.rfind('.') < s.rfind(','): s = s.replace('.', '').replace(',', '.')
        else: s = s.replace(',', '')
    elif '.' in s:
        dots = s.count('.')
        if dots > 1: s = s.replace('.', '')
        else:
            parts = s.split('.')
            if len(parts[1]) == 3 and len(parts[0]) <= 3: s = s.replace('.', '')
    elif ',' in s:
        commas = s.count(',')
        if commas > 1: s = s.replace(',', '')
        else:
            parts = s.split(',')
            if len(parts[1]) == 3 and len(parts[0]) <= 3: s = s.replace(',', '')
            else: s = s.replace(',', '.')
    s = re.sub(r'[^0-9.-]', '', s)
    try: return float(s)
    except: return 0.0

MONTH_MAP = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
    7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'
}

pkb_by_month = defaultdict(list)
for r in reader:
    if len(r) < 50:
        continue
    y = r[2].strip()
    if y != '2026':
        continue
    try:
        m_num = int(float(r[1].strip()))
    except:
        continue
    m_name = MONTH_MAP.get(m_num)
    if m_name:
        pkb_by_month[m_name].append(r)

print(f"PKB 2026 months present: {sorted(pkb_by_month.keys(), key=lambda m: list(MONTH_MAP.values()).index(m))}")

# Load dashboard_data.json
with open('data/dashboard_data.json', 'r', encoding='utf-8') as f:
    dash = json.load(f)

kpis_2026 = dash.get('monthly_kpis', {}).get('2026', {})

print("\n" + "=" * 70)
print("A. AUDIT MONTHLY KPIS 2026 (PKB vs DASHBOARD)")
print("=" * 70)

months_ordered = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October'
]

discrepancies = []

for m in months_ordered:
    rows = pkb_by_month.get(m, [])
    sheet_ue = len(rows)
    sheet_cpus = sum(1 for r in rows if r[43].strip() == 'CPUS')
    sheet_sbe = sum(1 for r in rows if r[44].strip() == 'SBE')
    sheet_tcare = sum(1 for r in rows if r[49].strip() == 'T-CARE')
    sheet_rev = sum(clean_rev(r[57]) if len(r) > 57 else 0.0 for r in rows)
    
    dash_m = kpis_2026.get(m, {})
    dash_ue = dash_m.get('ue_total', 0)
    dash_cpus = dash_m.get('cpus', 0)
    dash_sbe = dash_m.get('sbe_count', 0)
    dash_tcare = dash_m.get('tcare_count', 0)
    dash_rev = dash_m.get('total_revenue', 0.0)
    
    match_ue = (sheet_ue == dash_ue)
    match_cpus = (sheet_cpus == dash_cpus)
    match_sbe = (sheet_sbe == dash_sbe)
    match_tcare = (sheet_tcare == dash_tcare)
    match_rev = abs(sheet_rev - dash_rev) < 10.0
    
    status = "OK" if (match_ue and match_cpus and match_sbe and match_tcare and match_rev) else "MISMATCH"
    print(f"[{status}] {m:10s} | UE: {dash_ue:4d} (sheet {sheet_ue:4d}) | CPUS: {dash_cpus:4d} (sheet {sheet_cpus:4d}) | SBE: {dash_sbe:4d} (sheet {sheet_sbe:4d}) | T-Care: {dash_tcare:4d} (sheet {sheet_tcare:4d}) | Rev: Rp {dash_rev:12,.0f} (sheet {sheet_rev:12,.0f})")
    
    if not (match_ue and match_cpus and match_sbe and match_tcare and match_rev):
        discrepancies.append((m, 'Monthly KPI', f"UE: {dash_ue} vs {sheet_ue}, CPUS: {dash_cpus} vs {sheet_cpus}, SBE: {dash_sbe} vs {sheet_sbe}, TCare: {dash_tcare} vs {sheet_tcare}, Rev: {dash_rev} vs {sheet_rev}"))

print("\n" + "=" * 70)
print("B. AUDIT SA PERFORMANCE OCTOBER 2026 (PKB & SO vs DASHBOARD)")
print("=" * 70)

# Check SA totals in PKB for October 2026
sa_pkb_oct = defaultdict(lambda: {'ue': 0, 'cpus': 0, 'tcare': 0, 'rev': 0.0})
for r in pkb_by_month.get('October', []):
    sa = r[42].strip().upper() if len(r) > 42 else ''
    if not sa and len(r) > 25:
        sa = r[25].strip().upper()
    if sa in ['DIDIN', 'FICKY', 'ACEP']:
        sa_pkb_oct[sa]['ue'] += 1
        if len(r) > 43 and r[43].strip() == 'CPUS':
            sa_pkb_oct[sa]['cpus'] += 1
        if len(r) > 49 and r[49].strip() == 'T-CARE':
            sa_pkb_oct[sa]['tcare'] += 1
        sa_pkb_oct[sa]['rev'] += clean_rev(r[57]) if len(r) > 57 else 0.0

dash_sa_totals = {
    x['sa']: x for x in dash.get('sa_monthly_totals', [])
    if str(x.get('year')) == '2026' and x.get('month_name') == 'October'
}

for sa in ['DIDIN', 'FICKY', 'ACEP']:
    st = sa_pkb_oct[sa]
    dt = dash_sa_totals.get(sa, {})
    match_ue = (st['ue'] == dt.get('ue'))
    match_cpus = (st['cpus'] == dt.get('cpus'))
    match_tc = (st['tcare'] == dt.get('tcare'))
    match_rev = abs(st['rev'] - dt.get('revenue', 0)) < 10.0
    status = "OK" if (match_ue and match_cpus and match_tc and match_rev) else "MISMATCH"
    print(f"[{status}] SA {sa:6s} PKB Totals: UE={dt.get('ue')} (sheet {st['ue']}) | CPUS={dt.get('cpus')} (sheet {st['cpus']}) | TCare={dt.get('tcare')} (sheet {st['tcare']}) | Rev=Rp {dt.get('revenue', 0):,.0f} (sheet {st['rev']:,.0f})")

print("\n" + "=" * 70)
print("C. AUDIT SA CROSS SELLING COMMODITIES (OCTOBER 2026)")
print("=" * 70)
dash_sa_cross = defaultdict(dict)
for x in dash.get('sa_cross_selling', []):
    if str(x.get('year')) == '2026' and x.get('month_name') == 'October':
        dash_sa_cross[x['sa']][x['category']] = x

for sa in ['DIDIN', 'FICKY', 'ACEP']:
    print(f"\n--- SA {sa} Commodities ---")
    for cat in ['CHEMICAL SMM', 'FULL SYNT', 'OPL CAR CARE', 'OPL AC', 'SPOORING', 'BATTERY', 'TIRE', 'REMATCHING', 'SMM OIL', 'CROSS SELLING TAM']:
        item = dash_sa_cross[sa].get(cat, {})
        print(f"  {cat:20s}: QTY={item.get('qty', 0):5.1f} | Rev=Rp {item.get('revenue', 0):12,.0f}")

print("\n" + "=" * 70)
print("D. AUDIT AO REPORT (SPREADSHEET vs ao_report_data.json)")
print("=" * 70)
URL_AO = "https://docs.google.com/spreadsheets/d/1LQYpCsXsU3o6N4cAMQH7Da44rXhSlksO/export?format=csv&gid=1124551793"
req = urllib.request.Request(URL_AO, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=60) as resp:
    ao_csv = resp.read().decode('utf-8', errors='replace')

ao_rows = list(csv.reader(io.StringIO(ao_csv)))
with open('data/ao_report_data.json', 'r', encoding='utf-8') as f:
    ao_data = json.load(f)

# Compare Key Metrics
# 1. Total Target CPUS (Row 19 col 7, zero-indexed: row 18 col 6 or row 19 col 6)
sheet_target_cpus = ao_rows[19][6] if len(ao_rows) > 19 and len(ao_rows[19]) > 6 else "?"
sheet_actual_cpus = ao_rows[19][7] if len(ao_rows) > 19 and len(ao_rows[19]) > 7 else "?"
sheet_pct_cpus = ao_rows[19][8] if len(ao_rows) > 19 and len(ao_rows[19]) > 8 else "?"

dash_target_cpus = ao_data.get('total_target_cpus', {}).get('value')
dash_actual_cpus = ao_data.get('total_actual_cpus', {}).get('value')
dash_pct_cpus = ao_data.get('pct_target_cpus', {}).get('value')

print(f"Total Target CPUS : Dash={dash_target_cpus} | Sheet={sheet_target_cpus}")
print(f"Total Actual CPUS : Dash={dash_actual_cpus} | Sheet={sheet_actual_cpus}")
print(f"Total % vs Target : Dash={dash_pct_cpus} | Sheet={sheet_pct_cpus}")

# Section 1 weeks
w_tar = ao_data.get('section_1_weekly', {}).get('target_cpus_weeks', [])
w_act = ao_data.get('section_1_weekly', {}).get('actual_cpus_weeks', [])
w_pct = ao_data.get('section_1_weekly', {}).get('vs_target_weeks', [])
print(f"Section 1 Target Weeks : {w_tar}")
print(f"Section 1 Actual Weeks : {w_act}")
print(f"Section 1 % Weeks      : {w_pct}")

# Section 2 Non T-Care
walkin = ao_data.get('section_2_non_tcare', {}).get('walk_in', {}).get('actual_total')
bk_act = ao_data.get('section_2_non_tcare', {}).get('booking', {}).get('actual_total')
bks_act = ao_data.get('section_2_non_tcare', {}).get('booking_show', {}).get('actual_total')
print(f"Walk-in Actual Total      : {walkin}")
print(f"Booking Actual Total      : {bk_act}")
print(f"Booking Show Actual Total : {bks_act}")

# Section 3 SBI
sbi_badge = ao_data.get('section_3_sbi', {}).get('target_rate_badge')
sbi_ncs_tar = ao_data.get('section_3_sbi', {}).get('target', {}).get('ncs_m1_total')
sbi_ncs_act = ao_data.get('section_3_sbi', {}).get('actual', {}).get('ncs_m1_total')
sbi_tot_act = ao_data.get('section_3_sbi', {}).get('actual', {}).get('total_total')
sbi_gap = ao_data.get('section_3_sbi', {}).get('gap', {}).get('gap_kumulatif_total')
print(f"SBI Target Rate Badge     : {sbi_badge}")
print(f"SBI NCS M-1 Target / Act  : {sbi_ncs_tar} / {sbi_ncs_act}")
print(f"SBI Actual Total          : {sbi_tot_act}")
print(f"SBI Gap Kumulatif Total   : {sbi_gap}")

print("\n" + "=" * 70)
print("E. AUDIT FUNNELLING DATA (data/funnelling_data.json)")
print("=" * 70)
with open('data/funnelling_data.json', 'r', encoding='utf-8') as f:
    funnel = json.load(f)
print(f"Funnelling keys: {list(funnel.keys())[:10]}")
if 'periods' in funnel:
    print(f"Funnelling periods: {list(funnel['periods'].keys())}")
