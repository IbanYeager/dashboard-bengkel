import urllib.request
import re

url = 'https://docs.google.com/spreadsheets/d/1b60d-JO50LU4KyywuULokmDIU7z3Ts_1/htmlview'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
html = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', errors='ignore')
items = re.findall(r'items\.push\(\{name:\s*"([^"]+)",\s*pageUrl:[^}]+gid:\s*"([^"]+)"', html)
print("All tabs found in spreadsheet:")
for name, gid in items:
    print(f"  Name: {name:25} | GID: {gid}")
