with open('scripts/inspect_remote_sheets.py', 'r') as f:
    pass

import urllib.request
import re

url = 'https://docs.google.com/spreadsheets/d/1b60d-JO50LU4KyywuULokmDIU7z3Ts_1/htmlview'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        # Find all id="sheet-button-*"
        buttons = re.findall(r'<li id="sheet-button-(\d+)"[^>]*><a[^>]*>([^<]+)</a>', html)
        print("HTMLView Sheet Buttons (GID, Name):", buttons)
except Exception as e:
    print(e)
