import urllib.request
import csv
import io

SHEET_ID = '1b60d-JO50LU4KyywuULokmDIU7z3Ts_1'
GID = '457735933'
url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}'

print(f"Fetching SBI data from: {url}")
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
resp = urllib.request.urlopen(req, timeout=30)
content = resp.read().decode('utf-8', errors='ignore')

# save raw csv
with open(r'c:\laragon\www\dashboard_bengkel\data\sbi_raw.csv', 'w', encoding='utf-8') as f:
    f.write(content)

reader = list(csv.reader(io.StringIO(content)))
print(f"Total rows in SBI: {len(reader)}")
if len(reader) > 0:
    print(f"Row 0 (headers or title, {len(reader[0])} cols):")
    for idx, c in enumerate(reader[0]):
        print(f"  Col {idx}: {c}")

print("\nFirst 5 rows:")
for r_idx in range(min(5, len(reader))):
    print(f"Row {r_idx}: {reader[r_idx][:15]}")
