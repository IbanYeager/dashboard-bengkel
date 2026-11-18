import urllib.request
import urllib.parse
import re
import sys

sheet_id = '1b60d-JO50LU4KyywuULokmDIU7z3Ts_1'

known_sheets = ['INPUT PKB', 'Daftar List SO', 'TARGET', 'KPI TREE', 'BIWEEKLY', 'DB Vin Merdeka', 'MASTER', 'MASTER JOB', 'Dash update']
found = {}

for s in known_sheets:
    encoded_s = urllib.parse.quote(s)
    test_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={encoded_s}'
    try:
        req = urllib.request.Request(test_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as r:
            first_line = r.readline().decode('utf-8', errors='ignore')
            if first_line and 'html' not in first_line.lower():
                print(f"SUCCESS: Sheet '{s}' -> Accessible! Sample: {first_line[:60].strip()}")
                found[s] = test_url
            else:
                print(f"Sheet '{s}' returned HTML")
    except Exception as e:
        print(f"Sheet '{s}' -> Error: {e}")
    sys.stdout.flush()

print("\nAccessible Sheets:", list(found.keys()))
