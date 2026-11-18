import csv

with open(r'c:\laragon\www\dashboard_bengkel\data\tcare_dashboard_raw.csv', 'r', encoding='utf-8') as f:
    rows = list(csv.reader(f))

# Let's see the column headers for Row 45 (the big breakdown table headers)
print("=== Row 45 Headers ===")
for c_i, v in enumerate(rows[45]):
    if v.strip():
        print(f"Col {c_i:2d}: {v.strip()}")

# Also check Row 34 & Row 35
print("\n=== Row 34 Headers ===")
for c_i, v in enumerate(rows[34]):
    if v.strip():
        print(f"Col {c_i:2d}: {v.strip()}")

print("\n=== Row 35 Headers ===")
for c_i, v in enumerate(rows[35]):
    if v.strip():
        print(f"Col {c_i:2d}: {v.strip()}")

# Top summary blocks:
print("\n=== Top Summary (Rows 0 - 20) ===")
for r_i in range(21):
    non_b = [(c_i, c.strip()) for c_i, c in enumerate(rows[r_i]) if c.strip()]
    if non_b:
        print(f"R{r_i:2d}: {non_b}")
