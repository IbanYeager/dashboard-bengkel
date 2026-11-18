import csv

with open(r'c:\laragon\www\dashboard_bengkel\data\sbi_raw.csv', 'r', encoding='utf-8') as f:
    raw_rows = list(csv.reader(f))

rows = [r for r in raw_rows if any(cell.strip() for cell in r)]

print("Top 7 rows detail:")
for i in range(min(7, len(rows))):
    print(f"\n=== Row {i} ===")
    for c_idx, val in enumerate(rows[i]):
        if val.strip():
            print(f"[{c_idx}] {val.strip()}", end="  |  ")
    print()
