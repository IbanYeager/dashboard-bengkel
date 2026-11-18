import csv

with open(r'c:\laragon\www\dashboard_bengkel\data\sbi_raw.csv', 'r', encoding='utf-8') as f:
    reader = list(csv.reader(f))

print(f"Total rows: {len(reader)}")
for i in range(min(45, len(reader))):
    row_nonempty = [(idx, val) for idx, val in enumerate(reader[i]) if val.strip() != '']
    print(f"Row {i:2d}: {row_nonempty[:10]}")
