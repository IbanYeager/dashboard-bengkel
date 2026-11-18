import urllib.request
import csv
import io

url = 'https://docs.google.com/spreadsheets/d/1b60d-JO50LU4KyywuULokmDIU7z3Ts_1/gviz/tq?tqx=out:csv&sheet=INPUT%20PKB'
print("Fetching Google Sheets INPUT PKB...")
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    content = resp.read().decode('utf-8', errors='replace')

reader = csv.reader(io.StringIO(content))
headers = next(reader)
print("Total headers:", len(headers))
for idx, h in enumerate(headers):
    if any(k in h.lower() for k in ['rev', 'pkb', 'tgl', 'bln', 'thn', 'year', 'month', 'ue', 'service', 't-care', 'tcare', 'jasa', 'part']):
        print(f"Col {idx:2d}: \"{h}\"")

sep_2026_rows = []
for row_idx, row in enumerate(reader, 1):
    if len(row) > 2:
        bln = row[1].strip()
        thn = row[2].strip()
        # check year 2026
        if '2026' in thn or '2026' in ''.join(row[:5]):
            if bln in ['09', '9', 'Sep', 'September'] or '2609' in ''.join(row[:15]):
                sep_2026_rows.append(row)

print(f"\nTotal September 2026 rows found: {len(sep_2026_rows)}")
if sep_2026_rows:
    sample = sep_2026_rows[0]
    print("\nSample September 2026 row:")
    for idx, (h, val) in enumerate(zip(headers, sample)):
        if val.strip() and any(k in h.lower() for k in ['rev', 'pkb', 'ue', 'tgl', 'bln', 'thn', 'sa', 'service', 't-care']):
            print(f"  Col {idx:2d} ({h}): \"{val}\"")

    # Check revenue column in all sep_2026_rows
    # Find which column has 'Revenue' in header
    rev_cols = [idx for idx, h in enumerate(headers) if 'revenue' in h.lower()]
    print(f"\nRevenue column indices: {rev_cols}")
    for rc in rev_cols:
        vals = [r[rc] for r in sep_2026_rows if len(r) > rc]
        non_empty = [v for v in vals if v.strip()]
        print(f"  Col {rc} ('{headers[rc]}'): total={len(vals)}, non-empty={len(non_empty)}, sample={non_empty[:3] if non_empty else 'EMPTY'}")
