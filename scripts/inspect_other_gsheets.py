import urllib.request
import urllib.parse
import csv
import io

sheet_id = '1b60d-JO50LU4KyywuULokmDIU7z3Ts_1'

for s_name in ['Dash update', 'KPI TREE', 'BIWEEKLY', 'TARGET']:
    enc = urllib.parse.quote(s_name)
    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={enc}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode('utf-8', errors='replace')
            lines = content.splitlines()
            print(f"=== Sheet '{s_name}' (Total lines: {len(lines)}) ===")
            for i in range(min(10, len(lines))):
                if lines[i].strip():
                    print(f"  {lines[i][:120]}")
    except Exception as e:
        print(f"Sheet '{s_name}' error: {e}")
