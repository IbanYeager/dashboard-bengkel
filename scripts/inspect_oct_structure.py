import urllib.request, csv, io, json

sheet_id = '1b60d-JO50LU4KyywuULokmDIU7z3Ts_1'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Daftar%20List%20SO'
print('Fetching live Daftar List SO...')
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=60) as resp:
    content = resp.read().decode('utf-8', errors='replace')

reader = csv.reader(io.StringIO(content))
headers = next(reader)

all_oct_rows = []
for idx, r in enumerate(reader):
    # Check if row is October 2026
    is_oct = False
    for cell in r[:15]:
        if cell.strip() in ['October', 'Oktober']:
            is_oct = True
            break
        if cell.strip() == '10' and len(r) > 4 and ('2026' in r[2:5]):
            is_oct = True
            break
    if is_oct and ('2026' in ' '.join(r[:6])):
        all_oct_rows.append((idx + 2, r))

print(f"Total October 2026 rows: {len(all_oct_rows)}")

# Sample first 5 and last 5 October rows
print("\nFirst 3 October rows:")
for r_idx, r in all_oct_rows[:3]:
    print(f"Row {r_idx}: len={len(r)} -> {r[:15]}")

print("\nLast 3 October rows:")
for r_idx, r in all_oct_rows[-3:]:
    print(f"Row {r_idx}: len={len(r)} -> {r[:15]}")
