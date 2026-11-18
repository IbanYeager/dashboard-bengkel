import json

json_path = 'data/dashboard_data.json'
with open(json_path, 'r', encoding='utf-8') as f:
    d = json.load(f)

# 1. Update monthly_kpis 2026 September
if 'monthly_kpis' in d and '2026' in d['monthly_kpis'] and 'September' in d['monthly_kpis']['2026']:
    sep_kpi = d['monthly_kpis']['2026']['September']
    sep_kpi['raw_cpus'] = 639
    sep_kpi['sbi_cpus'] = 83
    sep_kpi['cpus'] = 722
    # ue_total is 726 (CPUS 722 + non-CPUS 4 or total UE 726)
    if sep_kpi.get('ue_total', 0) < 722:
        sep_kpi['ue_total'] = 726
    print("Updated monthly_kpis 2026 September:", sep_kpi)

# 2. Update ws_matrix_kabeng rows
if 'ws_matrix_kabeng' in d and 'rows' in d['ws_matrix_kabeng']:
    for r in d['ws_matrix_kabeng']['rows']:
        # Row 2: CPUS (PKB)
        if str(r.get('no')) == '2' or r.get('kpi') == 'CPUS (PKB)':
            if r.get('months') and len(r['months']) > 8:
                r['months'][8] = 722.0
                print("Updated ws_matrix_kabeng Row 2 (CPUS) month 8 to 722.0")
        # Row 1: Unit Entry
        if str(r.get('no')) == '1' or r.get('kpi') == 'Unit Entry':
            if r.get('months') and len(r['months']) > 8:
                # ensure it is at least 726
                if (r['months'][8] or 0) < 726:
                    r['months'][8] = 726.0
                print("ws_matrix_kabeng Row 1 (UE) month 8 is", r['months'][8])
        # Row 3: CPUS Composition
        if str(r.get('no')) == '3' or r.get('kpi') == 'CPUS Composition':
            if r.get('months') and len(r['months']) > 8:
                ue_val = 726.0
                r['months'][8] = round(722.0 / ue_val, 4)
                print("Updated ws_matrix_kabeng Row 3 (CPUS Composition) month 8 to", r['months'][8])

# 3. Update sa_performance for September 2026 (distribute 722 CPUS: 242, 242, 238)
if 'sa_performance' in d:
    for item in d['sa_performance']:
        if item.get('year') == 2026 and item.get('month_name') == 'September':
            sa = item.get('sa')
            if sa == 'ACEP':
                item['cpus'] = 242
            elif sa == 'DIDIN':
                item['cpus'] = 242
            elif sa == 'FICKY':
                item['cpus'] = 238
            print(f"Updated sa_performance Sep 2026 for {sa}: cpus={item.get('cpus')}, ue={item.get('ue')}")

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

print("Saved updated data/dashboard_data.json successfully.")
