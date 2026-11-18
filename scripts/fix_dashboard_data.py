#!/usr/bin/env python3
"""
Sync dashboard_data.json with live Google Sheets spreadsheet data.
Fixes all discrepancies found during validation.
"""
import csv, io, collections, json, re, os, copy

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

# ── Step 1: Parse spreadsheet ──────────────────────────────────────────────
print("Reading spreadsheet CSV...")
with open(SPREADSHEET_CSV, 'r', encoding='utf-8') as f:
    content = f.read()
idx = content.index('---')
csv_text = content[idx+4:].strip()
reader = csv.reader(io.StringIO(csv_text))
header = next(reader)

all_rows = []
for row in reader:
    if len(row) >= 50:
        all_rows.append(row)

print(f"  Total records: {len(all_rows)}")

# Aggregate by year-month
def aggregate_month(rows):
    d = {
        'total': len(rows), 'cpus': 0, 'sbi': 0, 'sbe': 0, 'gr_oil': 0, 'gr_other': 0, 'twc': 0,
        'aktif': 0, 'pasif': 0, 'new_cust': 0, 'inactive': 0,
        'tcare': 0, 'non_tcare': 0, 'cai': 0,
        'revenue': 0, 'cpus_revenue': 0,
        'raw_cpus': 0, 'sbi_count_actual': 0,
    }
    for r in rows:
        # TYPE UE (col 43)
        if r[43] == 'CPUS':
            d['cpus'] += 1
        elif r[43] == 'SBI':
            d['sbi'] += 1

        # Type Service (col 44)
        if r[44] == 'SBE': d['sbe'] += 1
        elif r[44] == 'GR OIL': d['gr_oil'] += 1
        elif r[44] == 'GR OTHER': d['gr_other'] += 1
        elif r[44] == 'TWC': d['twc'] += 1
        elif r[44] == 'SBI': d['sbi_count_actual'] += 1

        # Status (col 47)
        status = r[47].strip().upper()
        if status == 'AKTIF': d['aktif'] += 1
        elif status == 'PASIF': d['pasif'] += 1
        elif status == 'NEW CUST': d['new_cust'] += 1
        elif status == 'INACTIVE': d['inactive'] += 1

        # T-CARE NATIONAL (col 49)
        if r[49] == 'T-CARE': d['tcare'] += 1
        elif r[49] == 'NON T-CARE': d['non_tcare'] += 1

        # ATTACKLIST (col 48)
        if r[48] == 'CAI': d['cai'] += 1

        # Revenue (col 57)
        rev = parse_rev(r[57]) if len(r) > 57 else 0
        d['revenue'] += rev
        if r[43] == 'CPUS':
            d['cpus_revenue'] += rev

        # raw_cpus = SBE only
        if r[44] == 'SBE':
            d['raw_cpus'] += 1

    return d

months_by_year = collections.defaultdict(lambda: collections.defaultdict(list))
for row in all_rows:
    year = row[2]
    try:
        mnum = int(row[1])
    except:
        continue
    mn = month_names_map.get(mnum, '')
    if mn:
        months_by_year[year][mn].append(row)

# ── Step 2: Load & update dashboard_data.json ──────────────────────────────
print("\nLoading dashboard_data.json...")
with open(DASHBOARD_JSON, 'r', encoding='utf-8') as f:
    data = json.load(f)

changes = []

# Update 2026 monthly_kpis
for mn in ['January','February','March','April','May','June','July','August','September','October']:
    rows = months_by_year['2026'][mn]
    if not rows:
        continue
    agg = aggregate_month(rows)
    
    db = data['monthly_kpis']['2026'].get(mn, {})
    
    # Track changes
    def update_field(key, new_val, label=None):
        old = db.get(key)
        if old != new_val:
            changes.append(f"  {mn} {label or key}: {old} -> {new_val}")
            db[key] = new_val
    
    update_field('ue_total', agg['total'])
    update_field('cpus', agg['cpus'])
    update_field('raw_cpus', agg['raw_cpus'])
    update_field('sbe_count', agg['sbe'], 'sbe_count (SBE only)')
    update_field('tcare_count', agg['tcare'], 'tcare_count (T-CARE from col)')
    update_field('total_revenue', agg['revenue'])
    update_field('cpus_revenue', agg['cpus_revenue'])
    update_field('sbi_cpus', agg['sbi'])
    
    data['monthly_kpis']['2026'][mn] = db

# Also update breakdown section for 2026 if it exists
if 'breakdown' in data and '2026' in data.get('breakdown', {}):
    for mn in ['January','February','March','April','May','June','July','August','September','October']:
        rows = months_by_year['2026'][mn]
        if not rows:
            continue
        agg = aggregate_month(rows)
        
        if mn in data['breakdown']['2026']:
            bd = data['breakdown']['2026'][mn]
            
            # Update type_service breakdown
            if 'type_service' in bd:
                bd['type_service'] = {
                    'SBE': agg['sbe'],
                    'GR OIL': agg['gr_oil'],
                    'GR OTHER': agg['gr_other'],
                    'TWC': agg['twc'],
                    'SBI': agg['sbi']
                }
            
            # Update status breakdown
            if 'customer_status' in bd:
                bd['customer_status'] = {
                    'AKTIF': agg['aktif'],
                    'PASIF': agg['pasif'],
                    'NEW CUST': agg['new_cust'],
                    'INACTIVE': agg['inactive']
                }

# Update meta
data['meta']['generated_at'] = '2026-10-19 11:45:00'

# Count total records
total_records = sum(len(months_by_year[y][m]) for y in months_by_year for m in months_by_year[y])
data['meta']['total_pkb_records'] = total_records

# ── Step 3: Save ───────────────────────────────────────────────────────────
print(f"\nApplying {len(changes)} changes:")
for c in changes:
    print(c)

with open(DASHBOARD_JSON, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print(f"\nSaved {DASHBOARD_JSON}")

# ── Step 4: Verify ────────────────────────────────────────────────────────
print("\n\nVerification after update:")
with open(DASHBOARD_JSON, 'r', encoding='utf-8') as f:
    data2 = json.load(f)

for mn in ['January','February','March','April','May','June','July','August','September','October']:
    rows = months_by_year['2026'][mn]
    if not rows:
        continue
    agg = aggregate_month(rows)
    db = data2['monthly_kpis']['2026'].get(mn, {})
    
    ok = True
    if db.get('ue_total') != agg['total']: ok = False
    if db.get('cpus') != agg['cpus']: ok = False
    if db.get('sbe_count') != agg['sbe']: ok = False
    if db.get('tcare_count') != agg['tcare']: ok = False
    
    status = "OK" if ok else "STILL MISMATCHED"
    print(f"  {mn}: UE={db.get('ue_total')} CPUS={db.get('cpus')} SBE={db.get('sbe_count')} T-Care={db.get('tcare_count')} -> {status}")

print("\nDashboard data sync complete.")
