import urllib.request
import re
import json

doc_id = '1LQYpCsXsU3o6N4cAMQH7Da44rXhSlksO'
url = f'https://docs.google.com/spreadsheets/d/{doc_id}/edit'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})

try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        
    print(f'HTML length: {len(html)}')
    
    # Extract sheet metadata
    # Google sheets bootstrap data often has [null, 0, "SheetName", ...]
    # Or in JSON like "name":"DASHBOARD AO","sheetId":1124551793
    sheets = []
    # Pattern 1
    p1 = re.findall(r'\[(\d+),0,"([^"]+)"', html)
    for gid, name in p1:
        sheets.append((name, gid))
        
    # Pattern 2
    p2 = re.findall(r'\\"name\\":\\"([^\\"]+)\\",.*?\\"sheetId\\":(\d+)', html)
    for name, gid in p2:
        if (name, gid) not in sheets:
            sheets.append((name, gid))
            
    # Pattern 3
    p3 = re.findall(r'"name":"([^"]+)",.*?"sheetId":(\d+)', html)
    for name, gid in p3:
        if (name, gid) not in sheets:
            sheets.append((name, gid))

    print(f'Found {len(sheets)} sheets:')
    for name, gid in sheets:
        print(f'  - {name} (gid: {gid})')

except Exception as e:
    print('Error:', e)
