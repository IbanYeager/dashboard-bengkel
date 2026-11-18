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

oct_2026_rows = []
for r_idx, r in enumerate(reader):
    if len(r) < 10:
        continue
    
    # Check if year is strictly 2026 and month is October
    # Check col 3 (TAHUN)
    y_str = r[3].strip() if len(r) > 3 else ""
    # In some rows col 3 is '2026', col 2 is '10'
    # Or in shifted rows:
    row_line = ' '.join(r[:8])
    if '2026' not in row_line:
        continue
    
    # Check if month is 10 or October
    is_oct = False
    if len(r) > 2 and r[2].strip() in ['10', '10.0', 'October', 'Oktober']:
        is_oct = True
    elif len(r) > 12 and r[12].strip() in ['October', 'Oktober']:
        is_oct = True
    elif 'October' in row_line or 'Oktober' in row_line or ' 10 ' in row_line or '/10/' in row_line:
        is_oct = True
        
    if is_oct and ('2026' in row_line):
        oct_2026_rows.append((r_idx + 2, r))

print(f"Total October 2026 rows: {len(oct_2026_rows)}")

days = defaultdict(int)
for r_idx, r in oct_2026_rows:
    d = r[1].strip()
    days[d] += 1

print("\nDays in October 2026:")
for d in sorted(days.keys(), key=lambda x: int(float(x)) if x.replace('.','').isdigit() else 999):
    print(f"  Day {d}: {days[d]} rows")
