import urllib.request
import re

SHEET_ID = '1ZjHhEWivPdj9eACghYUV3fZ3bbieycUpXdytmEnfkIk'
url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/htmlview'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})

try:
    html = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', errors='ignore')
    items = re.findall(r'items\.push\(\{name:\s*"([^"]+)",\s*pageUrl:[^}]+gid:\s*"([^"]+)"', html)
    print("All tabs in this spreadsheet:")
    for name, gid in items:
        print(f"  Name: {name:30} | GID: {gid}")
    if not items:
        # Fallback check
        print("Regex didn't match, checking for gid in html...")
        matches = re.findall(r'gid[=:]"?(\d+)"?', html)
        print("Found GIDs:", set(matches))
except Exception as e:
    print("Error:", e)
