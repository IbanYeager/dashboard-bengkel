import urllib.request
import re

url = 'https://docs.google.com/spreadsheets/d/1b60d-JO50LU4KyywuULokmDIU7z3Ts_1/htmlview'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        html = r.read().decode('utf-8', errors='ignore')
        # Find sheet names
        buttons = re.findall(r'<li id="sheet-button-([^"]+)"[^>]*><a[^>]*>([^<]+)</a>', html)
        print("Sheets in database kc:", buttons)
        
        # Look for Attacklist or MRA or GIDs
        gids = re.findall(r'gid=(\d+)', html)
        print("Unique GIDs found:", set(gids))
except Exception as e:
    print('Error:', e)
