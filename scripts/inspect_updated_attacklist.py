import urllib.request
import csv
import io
from collections import Counter

url = 'https://docs.google.com/spreadsheets/d/1b60d-JO50LU4KyywuULokmDIU7z3Ts_1/gviz/tq?tqx=out:csv&gid=2141708170'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
content = urllib.request.urlopen(req).read().decode('utf-8')
reader = list(csv.reader(io.StringIO(content)))
header = reader[0]
rows = reader[1:]

print("Total rows:", len(rows))
print("Header Col 15:", header[15])

# Find where 'Agu-26' or 'Sep-26' appears
bulan_counts = Counter(r[15].strip() for r in rows if len(r) > 15)
print("Bulan Col 15 distribution:")
for k, v in bulan_counts.items():
    print(f"  '{k}': {v}")

# What about the empty ones? Check Tgl FU (Col 39) or other date columns for empty ones
empty_rows = [r for r in rows if len(r) > 15 and not r[15].strip()]
print(f"Total rows with empty Col 15: {len(empty_rows)}")
tgl_fu_counts = Counter()
for r in empty_rows:
    tgl_fu = r[39].strip() if len(r) > 39 else ''
    month_str = ''
    if '-' in tgl_fu:
        parts = tgl_fu.split('-')
        if len(parts) >= 2:
            month_str = parts[1]
    elif '/' in tgl_fu:
        parts = tgl_fu.split('/')
        if len(parts) >= 2:
            month_str = parts[1]
    tgl_fu_counts[month_str] += 1

print("In empty Col 15 rows, Tgl FU months distribution:")
for k, v in tgl_fu_counts.items():
    print(f"  '{k}': {v}")

# Check rows around 350 to 375
print("\nRows 350 to 375:")
for idx in range(350, min(375, len(rows))):
    r = rows[idx]
    q = r[0] if len(r) > 0 else ''
    cai = r[4] if len(r) > 4 else ''
    j = r[8] if len(r) > 8 else ''
    b = r[15] if len(r) > 15 else ''
    fu = r[39] if len(r) > 39 else ''
    print(f"Row {idx+2}: Q={q} | CAI={cai:7} | J={j:28} | Bulan={b:8} | TglFU={fu}")
