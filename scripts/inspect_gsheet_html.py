import urllib.request
import re

url = 'https://docs.google.com/spreadsheets/d/1b60d-JO50LU4KyywuULokmDIU7z3Ts_1/edit?gid=943118321'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    resp = urllib.request.urlopen(req)
    html = resp.read().decode('utf-8', errors='ignore')
    
    # Search for sheetId / gid
    gids = re.findall(r'(\d{7,11})', html)
    print("Potential gids found:", set([g for g in gids if g in ['943118321'] or len(g) >= 8]) )
    
    # Search for known tab names
    for name in ['INPUT PKB', 'Daftar List SO', 'TARGET', 'Dash update', 'KPI TREE', 'BIWEEKLY']:
        if name.lower() in html.lower():
            print(f"Sheet name '{name}' found in HTML!")
            
    # Search for all occurrences of 943118321
    idx = html.find('943118321')
    found_count = 0
    while idx != -1:
        found_count += 1
        print(f"--- Occurrence {found_count} around pos {idx} ---")
        print(html[max(0, idx-80):min(len(html), idx+80)])
        idx = html.find('943118321', idx+1)
        if found_count >= 5:
            break
except Exception as e:
    print("Error:", e)
