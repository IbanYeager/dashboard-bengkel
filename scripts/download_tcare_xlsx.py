import urllib.request
import zipfile
import xml.etree.ElementTree as ET
import os

SHEET_ID = '1ZjHhEWivPdj9eACghYUV3fZ3bbieycUpXdytmEnfkIk'
url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx'
dest_path = r'c:\laragon\www\dashboard_bengkel\data\tcare_live.xlsx'

print("Downloading XLSX of T-Care sheet...")
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=60) as resp:
    data = resp.read()
    with open(dest_path, 'wb') as f:
        f.write(data)
print(f"Downloaded {len(data):,} bytes successfully!")

# Inspect workbook
with zipfile.ZipFile(dest_path, 'r') as z:
    wb_root = ET.fromstring(z.read('xl/workbook.xml'))
    rels_root = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels_root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')}
    sheet_files = {}
    for s in wb_root.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet'):
        s_name = s.attrib.get('name').strip()
        rId = s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        sheet_files[s_name] = 'xl/' + rel_map[rId].lstrip('/')
    print("Sheets in workbook:")
    for name, path in sheet_files.items():
        print(f"  {name:25}: {path}")
