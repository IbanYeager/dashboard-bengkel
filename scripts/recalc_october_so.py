import urllib.request, csv, io, json

sheet_id = '1b60d-JO50LU4KyywuULokmDIU7z3Ts_1'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Daftar%20List%20SO'
print('Fetching live Daftar List SO...')
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=60) as resp:
    content = resp.read().decode('utf-8', errors='replace')

reader = csv.reader(io.StringIO(content))
headers = next(reader)

# Let's inspect rows starting from row 140000 (October 2026 is around 146000-150000)
# But let's check any row with year 2026 and month October
commodities = [
    'CHEMICAL SMM', 'FULL SYNT', 'OPL CAR CARE', 'OPL AC',
    'SPOORING', 'BATTERY', 'TIRE', 'REMATCHING', 'CROSS SELLING TAM', 'SMM OIL'
]

# We want to aggregate: sa -> commodity -> {qty, revenue, rows}
oct_agg = {
    'DIDIN': {c: {'qty': 0.0, 'revenue': 0.0, 'count': 0} for c in commodities},
    'FICKY': {c: {'qty': 0.0, 'revenue': 0.0, 'count': 0} for c in commodities},
    'ACEP': {c: {'qty': 0.0, 'revenue': 0.0, 'count': 0} for c in commodities},
}

for r_idx, r in enumerate(reader):
    if len(r) < 10:
        continue
    # Check if row is October 2026
    # Let's see: r[3] == '2026' or r[2] == '10' or 'October' in r or 'Oktober' in r
    is_oct_2026 = False
    for cell in r:
        if cell.strip() in ['October', 'Oktober']:
            # verify year 2026
            if '2026' in ' '.join(r):
                is_oct_2026 = True
                break
    if not is_oct_2026:
        continue

    # Identify SA
    sa = None
    for s in ['DIDIN', 'FICKY', 'ACEP']:
        # SA name is usually in col 4 or 5
        for col_i in range(min(10, len(r))):
            if r[col_i].strip().upper() == s:
                sa = s
                break
        if sa:
            break
    if not sa:
        continue

    # Identify commodity
    comm = None
    for c in commodities:
        for col_i in range(min(15, len(r))):
            if r[col_i].strip().upper() == c:
                comm = c
                break
        if comm:
            break
    if not comm:
        continue

    # Now parse qty and revenue
    # In row structure:
    # Look at row 147467 (DIDIN TIRE):
    # ['-', '13', '10', '2026', 'DIDIN', 'GR OTHER', 'TIRE', 'October', '146', '146PKB2610-0342', 'Material', '4265P-1BK00-01N', 'Blackhawk HH31, 175/65 R14', '146 - TR KIARACONDONG', '146 - KC - MATERIAL', '146 - KC - MATERIAL - DEFAULT LOC', 'GR NEW ENTRY', 'No', '2', '0', '0', '0', '2', 'No', '550000', '1100000', '10', '110000', '990000', '891892', '98108', '990000', 'Yes', 'RADEN ADJENG WIRIS WIGNAWATI', '>250rb', '2']
    # QTY: col 22 (value '2') or last column (col 35)
    # Revenue: value '990000' is at col 28 or col 31 (Net after discount)
    #
    # Look at row 148812 (DIDIN TIRE with 'Pcs' inserted):
    # ['-', '17', '10', '2026', 'DIDIN', 'SBE', 'TIRE', 'October', '146', '146PKB2610-0456', 'Material', '4265P-1DU00-82N', 'DUNLOP ENASAVE EC300+ 215/60 R17', '146 - TR KIARACONDONG', '146 - KC - MATERIAL', '146 - KC - MATERIAL - DEFAULT LOC', 'SBE STANDARD', 'No', '2', '0', '0', '0', '2', 'No', 'Pcs', '1609400', '3218800', '10', '321880', '2896920', '2609838', '287082', '2896920', 'Yes', 'KANTOR WILAYAH BADAN PERTANAHAN NASIONAL PROP. JAWA BARA', '>250rb', '2']
    
    # Notice: Qty is after 'No' -> r[col of 'No' + 5] or r[col of 'No' + 1]
    # Let's see: r[17] == 'No', r[18] == '2', r[22] == '2', r[23] == 'No'
    # And Revenue is the number before DPP ('2609838') and PPN ('287082') -> Net Total = 2896920.
    # Let's inspect where revenue is reliably located!
    # In row 147467: 990000 is at index 28 (and 31). DPP is 891892, PPN is 98108.
    # In row 148812: 2896920 is at index 29 (and 32). DPP is 2609838, PPN is 287082.
    # Because of 'Pcs' at index 24, columns 25 onwards are shifted by +1!
    
    # Find 'Yes' which is before Customer Name:
    # In 147467: r[32] == 'Yes', r[31] == '990000'
    # In 148812: r[33] == 'Yes', r[32] == '2896920'
    # The cell right before 'Yes' is ALWAYS Total Net Revenue!
    
    rev_val = 0.0
    qty_val = 0.0
    
    # Find 'Yes'
    for ci, c in enumerate(r):
        if c.strip() == 'Yes' and ci > 25:
            try:
                rev_val = float(r[ci - 1].replace('.', '').replace(',', '.').strip())
            except:
                pass
            break
            
    # Find qty: last cell or cell after second 'No'
    # Last non-empty cell in r is often qty or #REF!
    # Let's check cells from end backwards:
    for c in reversed(r):
        c_clean = c.replace(',', '.').strip()
        try:
            val = float(c_clean)
            if 0 < val <= 500: # reasonable qty
                qty_val = val
                break
        except:
            continue
            
    oct_agg[sa][comm]['qty'] += qty_val
    oct_agg[sa][comm]['revenue'] += rev_val
    oct_agg[sa][comm]['count'] += 1

print("\n--- CALCULATED OCTOBER 2026 COMMODITIES ---")
for sa in ['DIDIN', 'FICKY', 'ACEP']:
    print(f"\nSA: {sa}")
    for comm in commodities:
        info = oct_agg[sa][comm]
        print(f"  {comm:18s} : Qty={info['qty']:6.1f} | Rev=Rp {info['revenue']:12,.0f} ({info['count']} tx)")

# Now load existing dashboard_data.json and compare
with open('data/dashboard_data.json', 'r', encoding='utf-8') as f:
    curr_data = json.load(f)

curr_oct = {
    'DIDIN': {},
    'FICKY': {},
    'ACEP': {}
}
for x in curr_data.get('sa_cross_selling', []):
    if x.get('year') == 2026 and x.get('month_name') == 'October':
        curr_oct[x['sa']][x['category']] = x

print("\n--- COMPARISON WITH DASHBOARD_DATA.JSON ---")
for sa in ['DIDIN', 'FICKY', 'ACEP']:
    for comm in commodities:
        calc = oct_agg[sa][comm]
        curr = curr_oct[sa].get(comm, {'qty': 0, 'revenue': 0})
        diff_qty = calc['qty'] - curr['qty']
        diff_rev = calc['revenue'] - curr['revenue']
        if abs(diff_qty) > 0.01 or abs(diff_rev) > 1:
            print(f"DIFF: {sa} - {comm:18s} | Calc Qty={calc['qty']} (Curr={curr['qty']}) | Calc Rev={calc['revenue']} (Curr={curr['revenue']})")
