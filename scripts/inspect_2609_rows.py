import urllib.request
import csv
import io

url = 'https://docs.google.com/spreadsheets/d/1b60d-JO50LU4KyywuULokmDIU7z3Ts_1/gviz/tq?tqx=out:csv&sheet=INPUT%20PKB'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    content = resp.read().decode('utf-8', errors='replace')

reader = csv.reader(io.StringIO(content))
headers = next(reader)

# Let's inspect rows with 2609
pkb_2609 = []
for idx, r in enumerate(reader, 1):
    pkb = r[10] if len(r) > 10 else ''
    if '146PKB2609' in pkb:
        pkb_2609.append((idx, r))

print(f"Total rows with PKB 146PKB2609: {len(pkb_2609)}")
if pkb_2609:
    # check dates
    dates = set(r[12] for idx, r in pkb_2609 if len(r) > 12)
    print("Unique PKB Dates in 146PKB2609:", sorted(list(dates))[:10])
    
    # Check revenue in all columns
    non_empty_cols = set()
    for idx, r in pkb_2609:
        for c_idx, val in enumerate(r):
            if val.strip():
                non_empty_cols.add(c_idx)
    
    print("\nNon-empty columns in 146PKB2609 rows:")
    for c in sorted(non_empty_cols):
        h = headers[c] if c < len(headers) else f"Col {c}"
        sample_vals = [r[c] for idx, r in pkb_2609 if len(r) > c and r[c].strip()][:3]
        print(f"  Col {c:2d} ({h:<30}): {sample_vals}")
