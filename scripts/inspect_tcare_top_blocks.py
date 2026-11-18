import csv

with open(r'c:\laragon\www\dashboard_bengkel\data\tcare_dashboard_raw.csv', 'r', encoding='utf-8') as f:
    rows = list(csv.reader(f))

print(f"Total rows: {len(rows)}")

for i in range(min(45, len(rows))):
    items = [(idx, val.strip()) for idx, val in enumerate(rows[i]) if val.strip()]
    if items:
        print(f"\n--- Row {i} ({len(items)} cols) ---")
        for c, v in items:
            print(f"  [{c}]: {v}")
