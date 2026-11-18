import csv

with open(r'c:\laragon\www\dashboard_bengkel\data\tcare_dashboard_raw.csv', 'r', encoding='utf-8') as f:
    rows = list(csv.reader(f))

# Let's see all rows and their columns
for r_i, r in enumerate(rows):
    line_parts = []
    for c_i, val in enumerate(r):
        v = val.strip().replace('\n', ' ')
        if v:
            line_parts.append(f"C{c_i}: {v}")
    if line_parts:
        print(f"R{r_i:2d} | " + " | ".join(line_parts[:10]))
        if len(line_parts) > 10:
            print("     | " + " | ".join(line_parts[10:20]))
        if len(line_parts) > 20:
            print("     | " + " | ".join(line_parts[20:30]))
