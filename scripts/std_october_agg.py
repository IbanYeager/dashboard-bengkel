import urllib.request, csv, io, json
from collections import defaultdict

sheet_id = '1b60d-JO50LU4KyywuULokmDIU7z3Ts_1'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Daftar%20List%20SO'
print('Fetching live Daftar List SO...')
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=90) as resp:
    content = resp.read().decode('utf-8', errors='replace')

reader = csv.reader(io.StringIO(content))
headers = next(reader)

COMMODITY_LIST = [
    'CHEMICAL SMM', 'FULL SYNT', 'OPL CAR CARE', 'OPL AC',
    'SPOORING', 'BATTERY', 'TIRE', 'REMATCHING', 'CROSS SELLING TAM', 'SMM OIL'
]

# We will aggregate by: (SA, Category)
agg = defaultdict(lambda: {'qty': 0.0, 'rev': 0.0, 'count': 0})

def clean_num(s):
    if not s or s.strip() in ['-', '#REF!', '#N/A', '#VALUE!', 'FALSE', 'TRUE', '']:
        return 0.0
    s = s.strip().replace('Rp', '').replace('rp', '').replace('RP', '').replace(' ', '')
    if '.' in s and ',' in s:
        if s.rfind('.') < s.rfind(','):
            s = s.replace('.', '').replace(',', '.')
        else:
            s = s.replace(',', '')
    elif ',' in s:
        s = s.replace(',', '.')
    try:
        return float(s)
    except:
        return 0.0

oct_rows_count = 0
for r_idx, r in enumerate(reader):
    if len(r) < 41:
        continue
    # Year in Col 3, Month in Col 2 or Col 12
    y_str = r[3].strip() if len(r) > 3 else ""
    m_str = r[2].strip() if len(r) > 2 else ""
    m_name = r[12].strip() if len(r) > 12 else ""
    
    is_oct_2026 = False
    if y_str in ['2026', '2026.0'] and (m_str in ['10', '10.0', 'October', 'Oktober'] or m_name in ['October', 'Oktober']):
        is_oct_2026 = True
    elif m_name in ['October', 'Oktober'] and '2026' in ' '.join(r[:5]):
        is_oct_2026 = True
        
    if not is_oct_2026:
        continue
    oct_rows_count += 1
    
    sa = r[5].strip().upper() if len(r) > 5 else ""
    cat = r[11].strip().upper() if len(r) > 11 else ""
    
    # Check if category is OPL from col 0 if col 11 is empty
    if not cat and len(r) > 0 and r[0].strip():
        opl_val = r[0].strip().upper()
        if 'AC' in opl_val:
            cat = 'OPL AC'
        elif any(k in opl_val for k in ['CAR CARE', 'EC', 'ANTI RAT', 'ENGINE']):
            cat = 'OPL CAR CARE'
            
    if sa not in ['DIDIN', 'FICKY', 'ACEP'] or cat not in COMMODITY_LIST:
        continue
        
    # Qty in col 47, if 0 check col 33 or 29
    qty = clean_num(r[47]) if len(r) > 47 else 0.0
    if qty == 0:
        qty = clean_num(r[33]) if len(r) > 33 else 0.0
    if qty == 0:
        qty = clean_num(r[29]) if len(r) > 29 else 0.0
        
    # Rev in col 40 (Transaction Amount), if 0 check col 43 (Total Transaction Amount)
    rev = clean_num(r[40]) if len(r) > 40 else 0.0
    if rev == 0:
        rev = clean_num(r[43]) if len(r) > 43 else 0.0
        
    agg[(sa, cat)]['qty'] += qty
    agg[(sa, cat)]['rev'] += rev
    agg[(sa, cat)]['count'] += 1

print(f"Total October 2026 rows matched: {oct_rows_count}")

# Print out results
for sa in ['DIDIN', 'FICKY', 'ACEP']:
    print(f"\n==================== SA: {sa} ====================")
    total_sa_rev = sum(agg[(sa, c)]['rev'] for c in COMMODITY_LIST)
    for c in COMMODITY_LIST:
        info = agg[(sa, c)]
        pct = (info['rev'] / total_sa_rev * 100) if total_sa_rev > 0 else 0
        print(f"  {c:20s}: Qty={info['qty']:5.1f} | Rev=Rp {info['rev']:12,.0f} ({pct:4.1f}%) | {info['count']} tx")
    print(f"  {'TOTAL':20s}: Rev=Rp {total_sa_rev:12,.0f}")
