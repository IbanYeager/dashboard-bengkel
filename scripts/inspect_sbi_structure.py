import csv

with open(r'c:\laragon\www\dashboard_bengkel\data\sbi_raw.csv', 'r', encoding='utf-8') as f:
    raw_rows = list(csv.reader(f))

# Filter non-empty rows
rows = [r for r in raw_rows if any(cell.strip() for cell in r)]
print(f"Total non-empty rows: {len(rows)}")

# Let's inspect rows 0 to 15 in non-empty rows
for i in range(min(15, len(rows))):
    print(f"--- Row {i} ---")
    for col_idx, val in enumerate(rows[i]):
        if val.strip():
            print(f"  Col {col_idx:2d}: {val.strip()[:60]}")

print("\n--- Header candidate (Row 6 in non-empty rows or around there) ---")
# Let's find which row has columns like VIN, Nama, etc.
for i in range(len(rows)):
    row_str = " | ".join(rows[i])
    if "VIN" in row_str and "Nama" in row_str:
        print(f"Header row index: {i}")
        for col_idx, val in enumerate(rows[i]):
            print(f"  Col {col_idx:2d}: {val.strip()}")
        break
