import urllib.request, csv, io, json

sheet_id = '1b60d-JO50LU4KyywuULokmDIU7z3Ts_1'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Daftar%20List%20SO'
print('Fetching Daftar List SO...')
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=60) as resp:
    content = resp.read().decode('utf-8', errors='replace')

reader = csv.reader(io.StringIO(content))
headers = next(reader)
print("Headers length:", len(headers))

# Let's inspect rows for October 2026
oct_rows = []
for idx, r in enumerate(reader):
    is_oct = False
    for cell in r:
        c = cell.strip()
        if c in ['October', 'Oktober']:
            is_oct = True
            break
    if not is_oct and len(r) > 4 and r[3].strip() == '2026' and r[2].strip() == '10':
        is_oct = True
    if is_oct:
        oct_rows.append((idx + 2, r))

print(f"Total October rows: {len(oct_rows)}")

# Specifically examine DIDIN TIRE
print("\n--- DIDIN TIRE ROWS IN OCTOBER ---")
for r_idx, r in oct_rows:
    row_str = ' '.join(r).upper()
    if 'DIDIN' in row_str and 'TIRE' in row_str:
        print(f"Row {r_idx}: {[x for x in r if x.strip()]}")

# Also examine all TIRE rows in October
print("\n--- ALL TIRE ROWS IN OCTOBER ---")
for r_idx, r in oct_rows:
    row_str = ' '.join(r).upper()
    if 'TIRE' in row_str:
        sa = 'UNKNOWN'
        for s in ['DIDIN', 'FICKY', 'ACEP']:
            if s in row_str:
                sa = s
        print(f"SA: {sa} | Row {r_idx}: {[x for x in r if x.strip()]}")
