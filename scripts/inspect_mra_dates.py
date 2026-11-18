import csv
from collections import Counter

csv_path = 'data/mra_raw_sheet.csv'
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    headers = next(reader)
    
    empty_bulan_dates = Counter()
    all_dates = Counter()
    for r in reader:
        bln = r[15].strip()
        due = r[13].strip()
        q = r[0].strip()
        if not bln:
            # check due date
            empty_bulan_dates[due[-14:] if len(due) > 14 else due] += 1
        all_dates[due[-14:] if len(due) > 14 else due] += 1

print("Empty bulan sample dates:", empty_bulan_dates.most_common(15))
print("\nAll dates sample:", all_dates.most_common(15))
