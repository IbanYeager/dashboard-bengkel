import urllib.request, csv, io, json
from collections import Counter

sheet_id = '1b60d-JO50LU4KyywuULokmDIU7z3Ts_1'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Daftar%20List%20SO'
print('Fetching live Daftar List SO...')
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=90) as resp:
    content = resp.read().decode('utf-8', errors='replace')

reader = csv.reader(io.StringIO(content))
headers = next(reader)

# Let's inspect all October 2026 rows
oct_rows = []
for idx, r in enumerate(reader):
    if len(r) < 10:
        continue
    line = ' '.join(r[:8])
    if '2026' in line and ('10' in line or 'October' in line or 'Oktober' in line):
        oct_rows.append((idx + 2, r))

print(f"Total October 2026 candidates: {len(oct_rows)}")

# Let's check where SA is found in each row
sa_col_positions = Counter()
cat_col_positions = Counter()

KNOWN_SAS = {'DIDIN', 'FICKY', 'ACEP'}
KNOWN_CATS = {
    'CHEMICAL SMM', 'FULL SYNT', 'OPL CAR CARE', 'OPL AC',
    'SPOORING', 'BATTERY', 'TIRE', 'REMATCHING', 'CROSS SELLING TAM', 'SMM OIL',
    'SYNT', 'WIPER FLUID', 'OLI SMM'
}

for r_idx, r in oct_rows:
    for ci, cell in enumerate(r):
        c_up = cell.strip().upper()
        if c_up in KNOWN_SAS:
            sa_col_positions[ci] += 1
        if c_up in KNOWN_CATS:
            cat_col_positions[ci] += 1

print("SA column positions:", sa_col_positions)
print("Category column positions:", cat_col_positions)
