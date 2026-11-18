import json

DATA_PATH = 'data/dashboard_data.json'

with open(DATA_PATH, 'r', encoding='utf-8') as f:
    d = json.load(f)

print("Fixing July 2026 data in dashboard_data.json...")

# 1. Update monthly_kpis['2026']['July']
mk_2026 = d.setdefault('monthly_kpis', {}).setdefault('2026', {})
old_july = mk_2026.get('July', {})
print("Old July monthly_kpis:", old_july)

mk_2026['July'] = {
    'quartal': 3,
    'raw_cpus': 706,
    'sbi_cpus': 73,
    'cpus': 779,
    'ue_total': 829,
    'cpus_revenue': 1241872400.0,
    'total_revenue': 1241872400.0,
    'tcare_count': 308,
    'sbi_count': 73,
    'sbe_count': 417
}
print("New July monthly_kpis:", mk_2026['July'])

# 2. Update sa_performance for July 2026
sa_perf = d.get('sa_performance', [])
for sp in sa_perf:
    if str(sp.get('year')) == '2026' and sp.get('month_name') == 'July':
        sa = sp.get('sa')
        if sa == 'ACEP':
            sp['ue'] = 306
            sp['cpus'] = 269
            sp['revenue'] = 437593900.0
            sp['tcare_ue'] = 122
            sp['sbe_ue'] = 141
        elif sa == 'DIDIN':
            sp['ue'] = 260
            sp['cpus'] = 244
            sp['revenue'] = 464748800.0
            sp['tcare_ue'] = 73
            sp['sbe_ue'] = 114
        elif sa == 'FICKY':
            sp['ue'] = 263
            sp['cpus'] = 266
            sp['revenue'] = 339529700.0
            sp['tcare_ue'] = 113
            sp['sbe_ue'] = 162
        print(f"Updated sa_performance July {sa}:", sp)

# 3. Update sa_monthly_totals for July 2026
smt = d.get('sa_monthly_totals', [])
for r in smt:
    if r.get('year') == 2026 and r.get('month_name') == 'July':
        sa = r.get('sa')
        if sa == 'ACEP':
            r['ue'] = 306
            r['cpus'] = 269
            r['tcare'] = 122
            r['revenue'] = 437593900.0
        elif sa == 'DIDIN':
            r['ue'] = 260
            r['cpus'] = 244
            r['tcare'] = 73
            r['revenue'] = 464748800.0
        elif sa == 'FICKY':
            r['ue'] = 263
            r['cpus'] = 266
            r['tcare'] = 113
            r['revenue'] = 339529700.0
        print(f"Updated sa_monthly_totals July {sa}:", r)

# 4. Update ws_matrix_kabeng to ensure September is also bridged and July is full
if 'ws_matrix_kabeng' in d and 'rows' in d['ws_matrix_kabeng']:
    rows = d['ws_matrix_kabeng']['rows']
    sep_data = mk_2026.get('September', {})
    for row in rows:
        no = str(row.get('no', ''))
        # Ensure July (index 6) has correct values
        if no == '1': # Unit Entry
            row['months'][6] = 829.0
            if sep_data.get('ue_total'): row['months'][8] = sep_data.get('ue_total')
        elif no == '2': # CPUS
            row['months'][6] = 779.0
            if sep_data.get('cpus'): row['months'][8] = sep_data.get('cpus')
        elif no == '5': # SBE Total
            row['months'][6] = 417.0
            if sep_data.get('sbe_count'): row['months'][8] = sep_data.get('sbe_count')
        elif no == '7': # SBE T-Care
            row['months'][6] = 308.0
            if sep_data.get('tcare_count'): row['months'][8] = sep_data.get('tcare_count')
        elif no == '8': # SBE T-Care %
            row['months'][6] = round(308.0 / 417.0, 3) # 73.9%
            sbe_s = sep_data.get('sbe_count', 0)
            tc_s = sep_data.get('tcare_count', 0)
            if sbe_s > 0: row['months'][8] = round(tc_s / sbe_s, 3)
        elif no == '9': # SBE Non T-Care
            row['months'][6] = round((417.0 - 308.0) / 417.0, 3) # 26.1%
            sbe_s = sep_data.get('sbe_count', 0)
            tc_s = sep_data.get('tcare_count', 0)
            if sbe_s > 0: row['months'][8] = round((sbe_s - tc_s) / sbe_s, 3)
        elif no == '12': # Total Revenue
            row['months'][6] = 1241872.4
            if sep_data.get('total_revenue'): row['months'][8] = round(sep_data.get('total_revenue') / 1000.0, 3)
            
        # Recalculate Total YTD for row
        nums = [v for v in row['months'] if isinstance(v, (int, float))]
        if nums and no in ['1', '2', '5', '7', '12', '13', '14', '15', '16', '26', '34']:
            row['total'] = round(sum(nums), 1)

    # Also update ws_matrix_excel
    d['ws_matrix_excel'] = {
        '2026': d['ws_matrix_kabeng']['rows'],
        'kabeng': d['ws_matrix_kabeng']
    }

# Save updated dashboard_data.json
with open(DATA_PATH, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print("\nSuccessfully updated data/dashboard_data.json!")
