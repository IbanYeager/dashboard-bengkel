import urllib.request
import re
import json

headers = {'User-Agent': 'Mozilla/5.0'}

sheets_to_check = [
    ('1b60d-JO50LU4KyywuULokmDIU7z3Ts_1', '1727895687', 'DASH KIARACONDONG 24-26'),
    ('1tYGRaZf39MONbZ8IvgX2EtPHGzsg9by3jRrHfoNE4pQ', '2008717837', 'Spreadsheet 2')
]

for sid, gid, label in sheets_to_check:
    print(f"\n==================== {label} ({sid}) ====================")
    url = f"https://docs.google.com/spreadsheets/d/{sid}/edit?gid={gid}"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            title = re.search(r'<title>(.*?)</title>', html)
            print("Title:", title.group(1) if title else "Unknown")
            
            # Look for sheet metadata in bootstrap data
            # Typically in var bootstrapData = ... or similar
            tab_matches = re.findall(r'\[\s*(\d+)\s*,\s*\"([^\"]+)\"', html)
            print("Tabs found (id, name):")
            seen = set()
            for tid, tname in tab_matches:
                if tname not in seen and len(tname) < 40 and not tname.startswith('http'):
                    seen.add(tname)
                    print(f"  GID {tid}: {tname}")
    except Exception as e:
        print("Error fetching:", e)
