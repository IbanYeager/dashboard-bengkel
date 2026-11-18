import urllib.request
import re

url = 'https://docs.google.com/spreadsheets/d/1b60d-JO50LU4KyywuULokmDIU7z3Ts_1/edit'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    html = urllib.request.urlopen(req).read().decode('utf-8')
    matches = re.findall(r'name\\":\\"([^\\"]+)\\",\\"sheetId\\":([0-9]+)', html)
    print("Matches 1:", matches)
    if not matches:
        matches = re.findall(r'"name":"([^"]+)","sheetId":([0-9]+)', html)
        print("Matches 2:", matches)
    if not matches:
        # find all "gid": ...
        gids = re.findall(r'"gid":\s*"?([0-9]+)"?', html)
        print("All gids:", set(gids))
except Exception as e:
    print("Error:", e)
