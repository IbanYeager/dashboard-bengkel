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

years = defaultdict(lambda: defaultdict(lambda: {
    'rows': 0, 'pkbs': set(), 'nopols': set(), 'rev': 0.0,
    'tcare': 0, 'sbe': 0, 'dates': set()
}))

with open(r'data\live_input_pkb.csv', 'r', encoding='utf-8', errors='ignore') as f:
    reader = csv.reader(f)
    headers = next(reader)
    for r in reader:
        if len(r) < 15:
            continue
        thn = r[2].strip()
        bln = r[1].strip()
        if not thn:
            continue
        
        # normalize month number
        try:
            bln_int = int(bln)
            bln_str = f"{bln_int:02d}"
        except:
            bln_str = bln
            
        m_dict = years[thn][bln_str]
        m_dict['rows'] += 1
        pkb = r[10].strip()
        nopol = r[9].strip()
        if pkb:
            m_dict['pkbs'].add(pkb)
        if nopol:
            m_dict['nopols'].add(nopol)
        
        # Revenue
        rev_val = clean_num(r[57]) if len(r) > 57 else 0.0
        m_dict['rev'] += rev_val
            
        # T-Care
        tc = ((r[49] if len(r) > 49 else '') + ' ' + (r[50] if len(r) > 50 else '') + ' ' + (r[51] if len(r) > 51 else '')).lower()
        if 't-care' in tc or 'tcare' in tc:
            m_dict['tcare'] += 1
            
        # SBE
        srv = ((r[43] if len(r) > 43 else '') + ' ' + (r[44] if len(r) > 44 else '')).upper()
        if 'SBI' in srv or 'SBE' in srv or 'SERVICE BERKALA' in srv:
            m_dict['sbe'] += 1
            
        dt = r[12].strip() if len(r) > 12 else ''
        if dt:
            m_dict['dates'].add(dt)

print('=== SUMMARY PER TAHUN & BULAN (LIVE GID 177004909 - INPUT PKB) ===')
for y in sorted(years.keys()):
    print(f'\n--- TAHUN {y} ---')
    for b in sorted(years[y].keys()):
        d = years[y][b]
        sample_dates = sorted(list(d['dates']))[-3:] if d['dates'] else []
        print(f"Bulan {b:>2s}: Rows={d['rows']:5d} | UE(PKB)={len(d['pkbs']):4d} | CPUS(Nopol)={len(d['nopols']):4d} | Rev=Rp {d['rev']:16,.0f} | TCare={d['tcare']:3d} | SBE={d['sbe']:3d} | Latest Dates: {sample_dates}")
