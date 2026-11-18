#!/usr/bin/env python3
"""Validate dashboard_data.json against live Google Sheets CSV export."""
import csv, io, collections, json, re, os

SPREADSHEET_CSV = r"C:\Users\HP\.gemini\antigravity-ide\brain\789226ba-a5f1-4894-af21-94487dd8f2a1\.system_generated\steps\6\content.md"
DASHBOARD_JSON = r"c:\laragon\www\dashboard_bengkel\data\dashboard_data.json"

def parse_rev(s):
    if not s or s.strip() in ['-', '#REF!', '#N/A', '#VALUE!', 'FALSE', 'TRUE', '']:
        return 0
    s = re.sub(r'^(?:Rp\.?|RP\.?|rp\.?)\s*', '', s.strip()).strip()
    if '.' in s and ',' in s:
        if s.rfind('.') < s.rfind(','):
            s = s.replace('.', '').replace(',', '.')
        else:
            s = s.replace(',', '')
    elif '.' in s:
        dots = s.count('.')
        if dots > 1:
            s = s.replace('.', '')
        else:
            parts = s.split('.')
            if len(parts[1]) == 3 and len(parts[0]) <= 3:
                s = s.replace('.', '')
    elif ',' in s:
        commas = s.count(',')
        if commas > 1:
            s = s.replace(',', '')
        else:
            parts = s.split(',')
            if len(parts[1]) == 3 and len(parts[0]) <= 3:
                s = s.replace(',', '')
            else:
                s = s.replace(',', '.')
    s = re.sub(r'[^0-9.-]', '', s)
    try:
        return float(s)
    except:
        return 0

month_names_map = {1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',
                   7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'}

with open(SPREADSHEET_CSV, 'r', encoding='utf-8') as f:
    content = f.read()
idx = content.index('---')
csv_text = content[idx+4:].strip()
reader = csv.reader(io.StringIO(csv_text))
header = next(reader)

months_data = collections.defaultdict(lambda: {
    'total': 0, 'cpus': 0, 'sbi': 0, 'sbe': 0, 'gr_oil': 0, 'gr_other': 0, 'twc': 0,
    'aktif': 0, 'pasif': 0, 'new_cust': 0, 'inactive': 0,
    'tcare': 0, 'non_tcare': 0, 'cai': 0,
    'revenue': 0, 'cpus_revenue': 0, 'dates': set(),
    'raw_cpus': 0,
})

for row in reader:
    if len(row) < 50 or row[2] != '2026':
        continue
    try:
        mnum = int(row[1])
    except:
        continue
    mn = month_names_map.get(mnum, '')
    if not mn:
        continue
    d = months_data[mn]
    d['total'] += 1
    d['dates'].add(row[0])

    if row[43] == 'CPUS':
        d['cpus'] += 1
    elif row[43] == 'SBI':
        d['sbi'] += 1

    if row[44] == 'SBE': d['sbe'] += 1
    elif row[44] == 'GR OIL': d['gr_oil'] += 1
    elif row[44] == 'GR OTHER': d['gr_other'] += 1
    elif row[44] == 'TWC': d['twc'] += 1
    elif row[44] == 'SBI': pass

    if row[47] == 'AKTIF': d['aktif'] += 1
    elif row[47] == 'PASIF': d['pasif'] += 1
    elif row[47] == 'NEW CUST': d['new_cust'] += 1
    elif row[47] == 'INACTIVE': d['inactive'] += 1

    if row[49] == 'T-CARE': d['tcare'] += 1
    elif row[49] == 'NON T-CARE': d['non_tcare'] += 1

    if row[48] == 'CAI': d['cai'] += 1

    rev = parse_rev(row[57]) if len(row) > 57 else 0
    d['revenue'] += rev
    if row[43] == 'CPUS':
        d['cpus_revenue'] += rev

    # raw_cpus: SBE only
    if row[44] == 'SBE':
        d['raw_cpus'] += 1

with open(DASHBOARD_JSON, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 100)
print("FULL VALIDATION: SPREADSHEET vs DASHBOARD 2026")
print("=" * 100)

discrepancies = []
for mn in ['January','February','March','April','May','June','July','August','September','October']:
    s = months_data[mn]
    db = data['monthly_kpis']['2026'].get(mn, {})

    db_ue = db.get('ue_total', 'N/A')
    db_cpus = db.get('cpus', 'N/A')
    db_sbe = db.get('sbe_count', 'N/A')
    db_rev = db.get('total_revenue', 'N/A')
    db_tcare = db.get('tcare_count', 'N/A')

    issues = []
    if db_ue != s['total']:
        issues.append(f"UE: dashboard={db_ue}, spreadsheet={s['total']}")
    if db_cpus != s['cpus']:
        issues.append(f"CPUS: dashboard={db_cpus}, spreadsheet={s['cpus']}")
    if db_sbe != s['sbe']:
        issues.append(f"SBE_count: dashboard={db_sbe}, spreadsheet={s['sbe']}")

    max_date = max(s['dates'], key=lambda x: int(x)) if s['dates'] else '?'
    status = 'MISMATCH' if issues else 'OK'
    print(f"\n{mn} (data s/d tgl {max_date}): {status}")
    print(f"  UE:    spreadsheet={s['total']:>4d}  dashboard={db_ue}")
    print(f"  CPUS:  spreadsheet={s['cpus']:>4d}  dashboard={db_cpus}")
    print(f"  SBE:   spreadsheet={s['sbe']:>4d}  dashboard={db_sbe}")
    print(f"  T-Care: spreadsheet={s['tcare']:>4d}  dashboard={db_tcare}")
    print(f"  Revenue: spreadsheet={s['revenue']:>15,.0f}  dashboard={db_rev}")
    print(f"  Breakdown: SBE={s['sbe']} GR_OIL={s['gr_oil']} GR_OTHER={s['gr_other']} TWC={s['twc']} SBI={s['sbi']}")

    if issues:
        discrepancies.append((mn, issues, s))

print("\n" + "=" * 100)
if discrepancies:
    print(f"DISCREPANCIES FOUND IN {len(discrepancies)} MONTH(S):")
    for mn, issues, s in discrepancies:
        print(f"\n  {mn}:")
        for iss in issues:
            print(f"    - {iss}")
else:
    print("All months match!")

# Also validate AO report
print("\n\n" + "=" * 100)
print("AO REPORT VALIDATION")
print("=" * 100)

AO_CSV = r"C:\Users\HP\.gemini\antigravity-ide\brain\789226ba-a5f1-4894-af21-94487dd8f2a1\.system_generated\steps\7\content.md"
AO_JSON = r"c:\laragon\www\dashboard_bengkel\data\ao_report_data.json"

with open(AO_CSV, 'r', encoding='utf-8') as f:
    ao_content = f.read()
ao_idx = ao_content.index('---')
ao_text = ao_content[ao_idx+4:].strip()
ao_lines = ao_text.split('\n')

print(f"\nAO Spreadsheet has {len(ao_lines)} lines")

with open(AO_JSON, 'r', encoding='utf-8') as f:
    ao_data = json.load(f)

# Parse key values from AO spreadsheet
ao_reader = csv.reader(io.StringIO(ao_text))
ao_rows = list(ao_reader)

# Key values from spreadsheet:
# Row index 14 (line 23 in content): TOTAL CPUS ACTUAL
# Let's parse them

def safe_int(s):
    try:
        return int(float(s.strip().replace(',', '').replace('%', '')))
    except:
        return None

print("\nSection 1: Target Setting & Weekly Performance")
print(f"  Spreadsheet W3 actual from row:")

# Row 14 (0-indexed): TOTAL CPUS ACTUAL
for i, row in enumerate(ao_rows):
    for j, cell in enumerate(row):
        if 'TOTAL CPUS ACTUAL' in str(cell):
            print(f"  Row {i}: {row}")
            # Values should be at columns after this
            actuals = []
            for k in range(j+1, min(j+7, len(row))):
                v = safe_int(row[k])
                if v is not None:
                    actuals.append(v)
            print(f"  Parsed CPUS Actuals: {actuals}")
            break

# Compare key AO values
print(f"\n  AO JSON weekly actuals: {ao_data['section_1_target_setting']['weekly_performance']['total_cpus_actual']}")
print(f"  AO JSON CPUS target: {ao_data['section_1_target_setting']['kpi_tree']['cpus_target']}")

# Parse spreadsheet for CPUS ACTUAL
for i, row in enumerate(ao_rows):
    joined = ','.join(row)
    if 'TOTAL CPUS ACTUAL' in joined:
        vals = []
        for cell in row:
            v = safe_int(cell)
            if v is not None:
                vals.append(v)
        print(f"\n  Spreadsheet CPUS ACTUAL row values: {vals}")
    if 'WALK-IN ACTUAL' in joined:
        vals = []
        for cell in row:
            v = safe_int(cell)
            if v is not None:
                vals.append(v)
        print(f"  Spreadsheet WALK-IN ACTUAL row values: {vals}")
    if 'BOOKING SHOW ACTUAL' in joined:
        vals = []
        for cell in row:
            v = safe_int(cell)
            if v is not None:
                vals.append(v)
        print(f"  Spreadsheet BOOKING SHOW ACTUAL row values: {vals}")
    if 'NO SHOW ACTUAL' in joined:
        vals = []
        for cell in row:
            v = safe_int(cell)
            if v is not None:
                vals.append(v)
        print(f"  Spreadsheet NO SHOW ACTUAL row values: {vals}")
    if 'BOOKING ACTUAL' in joined and 'BOOKING SHOW' not in joined:
        vals = []
        for cell in row:
            v = safe_int(cell)
            if v is not None:
                vals.append(v)
        print(f"  Spreadsheet BOOKING ACTUAL row values: {vals}")

# Compare with JSON
wp = ao_data['section_1_target_setting']['weekly_performance']
print(f"\n  JSON total_cpus_actual: {wp['total_cpus_actual']}")
print(f"  JSON walkin_actual: {wp['walkin_actual']}")
print(f"  JSON booking_show_actual: {wp['booking_show_actual']}")
print(f"  JSON no_show_actual: {wp['no_show_actual']}")
print(f"  JSON booking_actual: {wp['booking_actual']}")

# Check cumulative
print(f"\n  JSON cumulative target: {ao_data['section_1_target_setting']['cumulative_chart']['target']}")
print(f"  JSON cumulative actual: {ao_data['section_1_target_setting']['cumulative_chart']['actual']}")
