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

# Let's inspect all October 2026 rows
results = {
    'DIDIN': defaultdict(lambda: {'qty': 0.0, 'rev': 0.0, 'items': []}),
    'FICKY': defaultdict(lambda: {'qty': 0.0, 'rev': 0.0, 'items': []}),
    'ACEP': defaultdict(lambda: {'qty': 0.0, 'rev': 0.0, 'items': []}),
}

oct_count = 0
for r_idx, r in enumerate(reader):
    if len(r) < 10:
        continue
    row_line = ' '.join(r[:8])
    if '2026' not in row_line:
        continue
    is_oct = False
    if len(r) > 2 and r[2].strip() in ['10', '10.0', 'October', 'Oktober']:
        is_oct = True
    elif len(r) > 12 and r[12].strip() in ['October', 'Oktober']:
        is_oct = True
    elif 'October' in row_line or 'Oktober' in row_line:
        is_oct = True
    if not is_oct:
        continue
    oct_count += 1

    # Find SA
    sa = None
    for s in ['DIDIN', 'FICKY', 'ACEP']:
        if s in [x.strip().upper() for x in r[:10]]:
            sa = s
            break
    if not sa:
        continue

    # Find Commodity
    cat = None
    for c in COMMODITY_LIST:
        for cell in r[:15]:
            if cell.strip().upper() == c:
                cat = c
                break
        if cat:
            break
            
    if not cat:
        # Check col 11 or 12 specifically
        continue

    # Parse Qty and Revenue
    # Qty is usually after 'No'
    qty = 0.0
    for cell in reversed(r):
        c_str = cell.replace(',', '.').strip()
        try:
            val = float(c_str)
            if 0 < val <= 500:
                qty = val
                break
        except:
            continue
            
    # Revenue is Transaction Amount
    # In Daftar List SO, Transaction Amount is right before DPP ('Total Base Amount')
    # Or let's inspect where transaction amount is
    rev = 0.0
    # Find 'Yes' in Billable (col 44 or around index 32-45)
    for i in range(len(r)-1, 20, -1):
        if r[i].strip() == 'Yes':
            # Previous cell is often revenue
            try:
                rev = float(r[i-1].replace('.', '').replace(',', '.').strip())
                break
            except:
                pass
                
    results[sa][cat]['qty'] += qty
    results[sa][cat]['rev'] += rev
    results[sa][cat]['items'].append((r_idx + 2, qty, rev, r))

print(f"Total October 2026 rows processed: {oct_count}")

# Print summary
for sa in ['DIDIN', 'FICKY', 'ACEP']:
    print(f"\n==================== SA: {sa} ====================")
    for c in COMMODITY_LIST:
        info = results[sa][c]
        print(f"  {c:20s}: Qty={info['qty']:5.1f} | Rev=Rp {info['rev']:12,.0f} ({len(info['items'])} rows)")

# Specifically print DIDIN TIRE
print("\n--- DIDIN TIRE DETAILS ---")
for r_idx, qty, rev, r in results['DIDIN']['TIRE']['items']:
    print(f"Row {r_idx}: Qty={qty}, Rev={rev} -> {[x for x in r if x.strip()]}")
