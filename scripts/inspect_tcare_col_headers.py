import csv

with open(r'c:\laragon\www\dashboard_bengkel\data\tcare_dashboard_raw.csv', 'r', encoding='utf-8') as f:
    rows = list(csv.reader(f))

print("=== Columns across Rows 41 to 46 ===")
for r_i in range(41, 47):
    print(f"\n--- Row {r_i} ---")
    for c_i in range(min(55, len(rows[r_i]))):
        val = rows[r_i][c_i].strip().replace('\n', ' ')
        if val:
            print(f"Col {c_i:2d}: {val}")
