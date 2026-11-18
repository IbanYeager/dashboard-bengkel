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
print("Headers:", len(headers))

# Let's inspect all rows where month is October 2026
oct_rows = []
for r_idx, r in enumerate(reader):
    if len(r) < 10:
        continue
    # Let's see: year 2026 and month October / 10
    # In Daftar List SO:
    # Col 1: Tanggal (day)
    # Col 2: BULAN (month: 10 or 10.0 or October)
    # Col 3: TAHUN (year: 2026 or 2026.0)
    # Or Col 12: BULAN ('October')
    
    # Let's check:
    is_oct_2026 = False
    
    # Check standard positions
    y_str = r[3].strip() if len(r) > 3 else ""
    m_str = r[2].strip() if len(r) > 2 else ""
    if (y_str in ['2026', '2026.0'] or '2026' in y_str) and (m_str in ['10', '10.0', 'October', 'Oktober']):
        is_oct_2026 = True
    elif len(r) > 12 and r[12].strip() in ['October', 'Oktober'] and '2026' in ' '.join(r[:5]):
        is_oct_2026 = True
    elif len(r) > 4 and ('October' in r[4] or 'Oktober' in r[4] or '10/2026' in r[4] or '10/26' in r[4]):
        is_oct_2026 = True
        
    if is_oct_2026:
        oct_rows.append((r_idx + 2, r))

print(f"Total October 2026 rows extracted: {len(oct_rows)}")

# Check dates distribution
day_counts = defaultdict(int)
for r_idx, r in oct_rows:
    day = r[1].strip() if len(r) > 1 else "?"
    day_counts[day] += 1

print("Day counts in October 2026:")
for d in sorted(day_counts.keys(), key=lambda x: int(float(x)) if x.replace('.','').isdigit() else 999):
    print(f"  Day {d}: {day_counts[d]} rows")
