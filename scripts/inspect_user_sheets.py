import urllib.request
import re
import json

def inspect_spreadsheet(doc_id):
    url = f"https://docs.google.com/spreadsheets/d/{doc_id}/htmlview"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            
        # Find sheet names and gids in htmlview
        # Usually found in items like: {name: "...", gid: "..."} or id="sheet-button-..."
        sheets = re.findall(r'id="sheet-button-([0-9]+)"[^>]*><a[^>]*>([^<]+)</a>', html)
        if not sheets:
            sheets = re.findall(r'gid=([0-9]+)[^>]*>([^<]+)</a>', html)
        print(f"Spreadsheet {doc_id}:")
        for gid, name in sheets:
            print(f"  GID: {gid} | Name: {name.strip()}")
        if not sheets:
            # Try to search for sheet names in script tags
            matches = re.findall(r'name:\s*"([^"]+)",\s*pageUrl:[^,]+,\s*gid:\s*"([0-9]+)"', html)
            for name, gid in matches:
                print(f"  GID: {gid} | Name: {name.strip()}")
    except Exception as e:
        print(f"Error inspecting {doc_id}: {e}")

print("=== SPREADSHEET 1 (BOOKING) ===")
inspect_spreadsheet("1tYGRaZf39MONbZ8IvgX2EtPHGzsg9by3jRrHfoNE4pQ")

print("\n=== SPREADSHEET 2 (THE REST) ===")
inspect_spreadsheet("1b60d-JO50LU4KyywuULokmDIU7z3Ts_1")
