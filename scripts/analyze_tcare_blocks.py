import csv

with open(r'c:\laragon\www\dashboard_bengkel\data\tcare_dashboard_raw.csv', 'r', encoding='utf-8') as f:
    rows = list(csv.reader(f))

# Let's see rows 0 to 35 across all columns
print("=== BLOCK 1: Rows 0 to 30 ===")
for r_i in range(31):
    r = rows[r_i]
    non_empty = [(c_i, c.strip()) for c_i, c in enumerate(r) if c.strip()]
    if non_empty:
        print(f"Row {r_i:2d}: {non_empty}")

print("\n=== BLOCK 2: Rows 31 to 45 (Retention table) ===")
for r_i in range(31, 46):
    r = rows[r_i]
    non_empty = [(c_i, c.strip()) for c_i, c in enumerate(r) if c.strip()]
    if non_empty:
        print(f"Row {r_i:2d}: {non_empty}")

print("\n=== BLOCK 3: Rows 45 to 76 (Detailed breakdown table) ===")
# Let's inspect column headers for the detailed breakdown
# Check what columns exist in row 45 and row 46
print("Row 45:", [(c_i, c.strip()) for c_i, c in enumerate(rows[45]) if c.strip()])
print("Row 46:", [(c_i, c.strip()) for c_i, c in enumerate(rows[46]) if c.strip()])
print("Row 47:", [(c_i, c.strip()) for c_i, c in enumerate(rows[47]) if c.strip()])
