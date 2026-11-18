import zipfile
import xml.etree.ElementTree as ET
import json
import re

XLSX_PATH = r'c:\laragon\www\dashboard_bengkel\data\tcare_live.xlsx'

shared_strings = []
print("Loading shared strings...")
with zipfile.ZipFile(XLSX_PATH, 'r') as z:
    with z.open('xl/sharedStrings.xml') as f:
        for event, elem in ET.iterparse(f, events=('end',)):
            if elem.tag.endswith('si'):
                text = "".join([t.text for t in elem.iter() if t.tag.endswith('t') and t.text])
                shared_strings.append(text)
                elem.clear()

print(f"Total shared strings: {len(shared_strings)}")

def parse_sheet_grid(sheet_file):
    with zipfile.ZipFile(XLSX_PATH, 'r') as z:
        sheet_root = ET.fromstring(z.read(sheet_file))
    grid = {}
    max_r = 0
    for row_elem in sheet_root.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheetData/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
        r_num = int(row_elem.attrib['r'])
        max_r = max(max_r, r_num)
        for c_elem in row_elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
            ref = c_elem.attrib['r']
            col_letters = ''.join(c for c in ref if c.isalpha())
            col_idx = 0
            for ch in col_letters:
                col_idx = col_idx * 26 + (ord(ch) - ord('A') + 1)
            t = c_elem.attrib.get('t')
            v_elem = c_elem.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
            val = ''
            if v_elem is not None and v_elem.text:
                if t == 's':
                    s_idx = int(v_elem.text)
                    val = shared_strings[s_idx] if s_idx < len(shared_strings) else ''
                else:
                    val = v_elem.text
            grid[(r_num, col_idx)] = val.strip()
    return grid, max_r

print("Parsing sheet2 (DASHBOARD)...")
dash_grid, dash_max_r = parse_sheet_grid('xl/worksheets/sheet2.xml')
print(f"DASHBOARD max row: {dash_max_r}")

print("Parsing sheet3 (RAW DATA T-CARE)...")
raw_grid, raw_max_r = parse_sheet_grid('xl/worksheets/sheet3.xml')
print(f"RAW DATA max row: {raw_max_r}")
