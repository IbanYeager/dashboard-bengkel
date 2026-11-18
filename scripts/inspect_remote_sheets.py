import urllib.request
import re
import json

sheet_id = '1b60d-JO50LU4KyywuULokmDIU7z3Ts_1'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/edit'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"HTML Length: {len(html)}")
        
        # Look for sheet names in bootstrap data
        # Google Sheets embeds sheet metadata in client data
        names = re.findall(r'\[\d+,\d+,"([^"]+)",(?:null|\d+)', html)
        print("Candidate names:", set([n for n in names if len(n) < 35 and not n.startswith('http')]))
        
        # Look for gid mappings
        gid_matches = re.findall(r'gid=(\d+)', html)
        print("GIDs found:", set(gid_matches))
except Exception as e:
    print(f"Error fetching sheet: {e}")
