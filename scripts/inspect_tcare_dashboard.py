import urllib.request
import csv
import io

SHEET_ID = '1ZjHhEWivPdj9eACghYUV3fZ3bbieycUpXdytmEnfkIk'
GID = '208980240'
url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={GID}'

print(f"Downloading DASHBOARD sheet from: {url}")
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=30) as resp:
    content = resp.read().decode('utf-8', errors='ignore')

with open(r'c:\laragon\www\dashboard_bengkel\data\tcare_dashboard_raw.csv', 'w', encoding='utf-8') as f:
    f.write(content)

reader = list(csv.reader(io.StringIO(content)))
print(f"Total rows in DASHBOARD sheet: {len(reader)}")

for idx, row in enumerate(reader):
    non_empty = [(c_idx, val.strip()) for c_idx, val in enumerate(row) if val.strip()]
    if non_empty:
        print(f"Row {idx:2d} ({len(non_empty)} cols): {non_empty[:12]}")
