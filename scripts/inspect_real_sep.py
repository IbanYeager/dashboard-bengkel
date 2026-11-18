import urllib.request
import csv
import io

url = 'https://docs.google.com/spreadsheets/d/1b60d-JO50LU4KyywuULokmDIU7z3Ts_1/gviz/tq?tqx=out:csv&sheet=INPUT%20PKB'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    content = resp.read().decode('utf-8', errors='replace')

reader = csv.reader(io.StringIO(content))
headers = next(reader)

# Let's inspect the exact column names:
for i, h in enumerate(headers):
    if i in [0, 1, 2, 10, 12, 25, 30, 42, 43, 44, 49, 57]:
        print(f"Col {i:2d}: '{h}'")

real_sep_rows = []
for idx, row in enumerate(reader, 1):
    pkb_no = row[10] if len(row) > 10 else ''
    pkb_date = row[12] if len(row) > 12 else ''
    periode = row[30] if len(row) > 30 else ''
    bln = row[1] if len(row) > 1 else ''
    thn = row[2] if len(row) > 2 else ''
    
    # Check if this row is September 2026
    if '2609' in pkb_no or '09/2026' in pkb_date or '/09/26' in pkb_date or 'September 2026' in periode or (thn == '2026' and bln in ['09', '9', 'Sep', 'September']):
        real_sep_rows.append((idx, row))

print(f"\nREAL September 2026 rows count: {len(real_sep_rows)}")
if real_sep_rows:
    print(f"First 5 September 2026 rows:")
    for r_idx, r in real_sep_rows[:5]:
        pkb = r[10] if len(r) > 10 else ''
        dt = r[12] if len(r) > 12 else ''
        sa = r[25] if len(r) > 25 else ''
        ue = r[43] if len(r) > 43 else ''
        srv = r[44] if len(r) > 44 else ''
        rev = r[57] if len(r) > 57 else ''
        print(f"  Row {r_idx:5d} | PKB: {pkb:<18} | Date: {dt:<10} | SA: {sa:<8} | UE: {ue:<5} | Srv: {srv:<8} | Rev: '{rev}'")

    print(f"\nLast 5 September 2026 rows:")
    for r_idx, r in real_sep_rows[-5:]:
        pkb = r[10] if len(r) > 10 else ''
        dt = r[12] if len(r) > 12 else ''
        sa = r[25] if len(r) > 25 else ''
        ue = r[43] if len(r) > 43 else ''
        srv = r[44] if len(r) > 44 else ''
        rev = r[57] if len(r) > 57 else ''
        print(f"  Row {r_idx:5d} | PKB: {pkb:<18} | Date: {dt:<10} | SA: {sa:<8} | UE: {ue:<5} | Srv: {srv:<8} | Rev: '{rev}'")
