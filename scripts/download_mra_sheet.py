import urllib.request

sheet_id = '1b60d-JO50LU4KyywuULokmDIU7z3Ts_1'
gid = '2141708170'
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid={gid}"

print("Downloading CSV for GID 2141708170...")
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=30) as r:
    content = r.read().decode('utf-8', errors='ignore')

out_path = 'data/mra_raw_sheet.csv'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Saved {len(content)} chars to {out_path}")

# Inspect headers and first few rows
import csv
with open(out_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    headers = next(reader)
    print("Headers count:", len(headers))
    for i, h in enumerate(headers):
        print(f"  Col {i} ({chr(65+i) if i < 26 else str(i)}): {h}")
    
    rows = list(reader)
    print("Total data rows:", len(rows))
    print("First 3 rows:")
    for r in rows[:3]:
        print(" ", r[:16])
