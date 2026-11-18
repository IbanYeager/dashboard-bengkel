import csv
import json
from collections import Counter

with open(r'c:\laragon\www\dashboard_bengkel\data\sbi_raw.csv', 'r', encoding='utf-8') as f:
    raw_rows = list(csv.reader(f))

# Let's filter non-empty rows
non_empty = [r for r in raw_rows if any(cell.strip() for cell in r)]
print(f"Total non-empty rows: {len(non_empty)}")

# Find header row
header_idx = None
for idx, r in enumerate(non_empty):
    r_str = " | ".join(r)
    if "VIN" in r_str and "Nama" in r_str and "Model" in r_str:
        header_idx = idx
        break

print(f"Header row index in non_empty: {header_idx}")
headers = [c.strip().replace('\n', ' ') for c in non_empty[header_idx]]
print(f"Number of headers: {len(headers)}")
for i, h in enumerate(headers):
    print(f"  Col {i:2d}: {h}")

# Data rows are non_empty[header_idx + 1:]
data_rows = non_empty[header_idx + 1:]
print(f"\nTotal data rows: {len(data_rows)}")

# Let's check distributions of some columns
years = Counter()
months = Counter()
cai_status = Counter()
models = Counter()
car_types = Counter()
cust_types = Counter()
sa_persons = Counter()
ss_persons = Counter()
tcare_status = Counter()
ring_areas = Counter()
notes_fu = Counter()
potency_sales = Counter()
judgements = Counter()

for r in data_rows:
    # pad row if shorter
    while len(r) < len(headers):
        r.append('')
    cai = r[0].strip()
    month = r[2].strip()
    year = r[4].strip()
    cust_type = r[11].strip()
    model = r[15].strip()
    sales = r[17].strip()
    ss = r[21].strip()
    car_type = r[22].strip()
    fu_by = r[24].strip()
    notes = r[26].strip()
    potency = r[31].strip()
    tcare = r[34].strip()
    ring = r[36].strip()
    judgement = r[46].strip()

    cai_status[cai] += 1
    months[month] += 1
    years[year] += 1
    cust_types[cust_type] += 1
    models[model] += 1
    car_types[car_type] += 1
    sa_persons[sales] += 1
    ss_persons[ss] += 1
    tcare_status[tcare] += 1
    ring_areas[ring] += 1
    notes_fu[notes] += 1
    potency_sales[potency] += 1
    judgements[judgement] += 1

print("\n--- CAI Status ---", cai_status)
print("\n--- Years ---", years)
print("\n--- Months ---", months)
print("\n--- Customer Types ---", cust_types)
print("\n--- Car Types ---", car_types)
print("\n--- T-Care Status ---", tcare_status)
print("\n--- Ring Areas ---", ring_areas)
print("\n--- Judgements Top 10 ---", judgements.most_common(10))
print("\n--- Notes FU Top 10 ---", notes_fu.most_common(10))
print("\n--- Potency Sales Top 10 ---", potency_sales.most_common(10))
print("\n--- SS Persons Top 10 ---", ss_persons.most_common(10))
