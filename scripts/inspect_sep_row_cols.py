import urllib.request
import csv
import io

url = 'https://docs.google.com/spreadsheets/d/1b60d-JO50LU4KyywuULokmDIU7z3Ts_1/gviz/tq?tqx=out:csv&sheet=INPUT%20PKB'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    content = resp.read().decode('utf-8', errors='replace')

reader = csv.reader(io.StringIO(content))
headers = next(reader)

for row_idx, row in enumerate(reader, 1):
    if len(row) > 10 and row[10].strip() == '146PKB2609-0001':
        print(f"=== ROW FOR 146PKB2609-0001 (Row {row_idx}) ===")
        for col_idx, (h, val) in enumerate(zip(headers, row)):
            if val.strip():
                print(f"Col {col_idx:2d} ({h}): \"{val}\"")
        break
