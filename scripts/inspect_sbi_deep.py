import csv
import json

with open(r'c:\laragon\www\dashboard_bengkel\data\sbi_raw.csv', 'r', encoding='utf-8') as f:
    raw_rows = list(csv.reader(f))

non_empty = [r for r in raw_rows if any(cell.strip() for cell in r)]
header_idx = 6
headers = [c.strip().replace('\n', ' ') for c in non_empty[header_idx]]
data_rows = non_empty[header_idx + 1:]

print("=== Summary Rows 0 - 5 Detail ===")
for r_i in range(header_idx):
    r = non_empty[r_i]
    non_blank = [(c_i, c) for c_i, c in enumerate(r) if c.strip()]
    print(f"Row {r_i}: {non_blank}")

print("\n=== Sample of First 3 Data Rows with All 47 Headers ===")
for r_i in range(min(3, len(data_rows))):
    print(f"\n--- Data Row {r_i + 1} ---")
    row = data_rows[r_i]
    for c_i, h in enumerate(headers):
        val = row[c_i] if c_i < len(row) else ''
        if val.strip():
            print(f"  {c_i:2d}. {h}: {val}")
