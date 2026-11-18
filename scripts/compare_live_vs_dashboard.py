import json
import csv
import re
from collections import defaultdict

def clean_num(val):
    if val is None or val == "":
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    if not s or s in ['-', '#REF!', '#N/A', '#VALUE!', 'FALSE', 'TRUE']:
        return 0.0
    s = re.sub(r'^(?:Rp\.?|RP\.?|rp\.?)\s*', '', s, flags=re.IGNORECASE).strip()
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
        return 0.0

MONTH_NUM_TO_NAME = {
    '01': 'January', '02': 'February', '03': 'March', '04': 'April',
    '05': 'May', '06': 'June', '07': 'July', '08': 'August',
    '09': 'September', '10': 'October', '11': 'November', '12': 'December'
}

# 1. Parse live INPUT PKB CSV
live_pkb = defaultdict(lambda: {
    'rows': 0, 'pkbs': set(), 'nopols': set(), 'rev': 0.0,
    'tcare': 0, 'sbe': 0, 'by_sa': defaultdict(lambda: {'ue': set(), 'cpus': set(), 'rev': 0.0}),
    'by_segment': defaultdict(lambda: {'ue': set(), 'rev': 0.0}),
    'by_ring': defaultdict(lambda: {'ue': set(), 'rev': 0.0})
})

with open(r'data\live_input_pkb.csv', 'r', encoding='utf-8', errors='ignore') as f:
    reader = csv.reader(f)
    headers = next(reader)
    for r in reader:
        if len(r) < 15:
            continue
        thn = r[2].strip()
        bln = r[1].strip()
        if thn != '2026':
            continue
        try:
            bln_str = f"{int(bln):02d}"
        except:
            bln_str = bln
        m_name = MONTH_NUM_TO_NAME.get(bln_str, bln_str)
        
        m_dict = live_pkb[m_name]
        m_dict['rows'] += 1
        pkb = r[10].strip()
        nopol = r[9].strip()
        if pkb:
            m_dict['pkbs'].add(pkb)
        if nopol:
            m_dict['nopols'].add(nopol)
        
        rev = clean_num(r[57]) if len(r) > 57 else 0.0
        m_dict['rev'] += rev
        
        tc = ((r[49] if len(r) > 49 else '') + ' ' + (r[50] if len(r) > 50 else '') + ' ' + (r[51] if len(r) > 51 else '')).lower()
        if 't-care' in tc or 'tcare' in tc:
            m_dict['tcare'] += 1
            
        srv = ((r[43] if len(r) > 43 else '') + ' ' + (r[44] if len(r) > 44 else '')).upper()
        if 'SBI' in srv or 'SBE' in srv or 'SERVICE BERKALA' in srv:
            m_dict['sbe'] += 1
            
        # SA
        sa = (r[42] if len(r) > 42 else (r[25] if len(r) > 25 else '')).upper().strip()
        sa_clean = 'OTHER'
        if 'ACEP' in sa: sa_clean = 'ACEP'
        elif 'DIDIN' in sa: sa_clean = 'DIDIN'
        elif 'FICKY' in sa: sa_clean = 'FICKY'
        
        if pkb: m_dict['by_sa'][sa_clean]['ue'].add(pkb)
        if nopol: m_dict['by_sa'][sa_clean]['cpus'].add(nopol)
        m_dict['by_sa'][sa_clean]['rev'] += rev

# 2. Load dashboard_data.json
with open(r'data\dashboard_data.json', 'r', encoding='utf-8') as f:
    dash = json.load(f)

dash_2026 = dash.get('monthly_kpis', {}).get('2026', {})

print("=" * 80)
print(f"{'MONTH':<12} | {'METRIC':<10} | {'LIVE GSHEET':<18} | {'DASHBOARD JSON':<18} | {'STATUS'}")
print("=" * 80)

for m_name in ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October']:
    live_m = live_pkb[m_name]
    dash_m = dash_2026.get(m_name, {})
    
    l_ue = len(live_m['pkbs'])
    d_ue = dash_m.get('ue_total', 0)
    match_ue = "MATCH" if l_ue == d_ue else f"DIFF ({d_ue - l_ue:+d})"
    
    l_cpus = len(live_m['nopols'])
    d_cpus = dash_m.get('cpus', 0)
    match_cpus = "MATCH" if l_cpus == d_cpus else f"DIFF ({d_cpus - l_cpus:+d})"
    
    l_rev = live_m['rev']
    d_rev = dash_m.get('total_revenue', 0.0)
    diff_rev = d_rev - l_rev
    match_rev = "MATCH" if abs(diff_rev) < 1000 else f"DIFF ({diff_rev:+,.0f})"
    
    print(f"{m_name:<12} | {'UE':<10} | {l_ue:<18} | {d_ue:<18} | {match_ue}")
    print(f"{'':<12} | {'CPUS':<10} | {l_cpus:<18} | {d_cpus:<18} | {match_cpus}")
    print(f"{'':<12} | {'REVENUE':<10} | Rp {l_rev:<15,.0f} | Rp {d_rev:<15,.0f} | {match_rev}")
    print("-" * 80)
