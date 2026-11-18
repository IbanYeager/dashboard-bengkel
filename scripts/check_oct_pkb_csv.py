import urllib.request
import csv
import io

url = 'https://docs.google.com/spreadsheets/d/1b60d-JO50LU4KyywuULokmDIU7z3Ts_1/gviz/tq?tqx=out:csv&sheet=INPUT%20PKB'
print("Fetching Google Sheets INPUT PKB CSV...")
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=30) as resp:
    content = resp.read().decode('utf-8', errors='replace')

reader = csv.reader(io.StringIO(content))
headers = next(reader)
print("Headers count:", len(headers))

oct_2026_rows = []
all_months_2026 = set()
for row_idx, row in enumerate(reader, 1):
    if len(row) > 2:
        bln = row[1].strip()
        thn = row[2].strip()
        if '2026' in thn:
            all_months_2026.add(bln)
            if bln in ['10', 'Okt', 'October', 'okt', 'october'] or '2610' in ''.join(row[:15]):
                oct_2026_rows.append((row_idx, row))

print("All 2026 months in Google Sheets INPUT PKB:", sorted(list(all_months_2026)))
print(f"Total October 2026 rows found: {len(oct_2026_rows)}")
if oct_2026_rows:
    print("Sample October row:")
    for idx, (h, val) in enumerate(zip(headers, oct_2026_rows[0][1])):
        if val.strip():
            print(f"  Col {idx} ({h}): {val}")
