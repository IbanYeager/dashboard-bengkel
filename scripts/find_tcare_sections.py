import zipfile
import xml.etree.ElementTree as ET

XLSX_PATH = r'c:\laragon\www\dashboard_bengkel\data\tcare_live.xlsx'

shared_strings = []
with zipfile.ZipFile(XLSX_PATH, 'r') as z:
    with z.open('xl/sharedStrings.xml') as f:
        for event, elem in ET.iterparse(f, events=('end',)):
            if elem.tag.endswith('si'):
                text = "".join([t.text for t in elem.iter() if t.tag.endswith('t') and t.text])
                shared_strings.append(text)
                elem.clear()

with zipfile.ZipFile(XLSX_PATH, 'r') as z:
    sheet_root = ET.fromstring(z.read('xl/worksheets/sheet2.xml'))

def col_str(c_idx):
    res = ''
    while c_idx > 0:
        c_idx, rem = divmod(c_idx - 1, 26)
        res = chr(ord('A') + rem) + res
    return res

grid = {}
for row_elem in sheet_root.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheetData/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
    r_num = int(row_elem.attrib['r'])
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

# Find all section headers or texts that look like titles
print("=== ALL LABELS / TITLES IN DASHBOARD SHEET ===")
rows = sorted(set(r for r, c in grid.keys()))
for r in rows:
    row_vals = [(col_str(c), grid[(r, c)]) for c in range(1, 60) if (r, c) in grid and grid[(r, c)]]
    if row_vals:
        # Check if row looks like header/title
        first_col, first_val = row_vals[0]
        if any(w in first_val.upper() for w in ['SUMMARY', 'MONITORING', 'T-CARE', 'T - CARE', 'RETENTION', 'PROGRAM', 'VEHICLE', 'CUSTOMER', 'RING', 'TOTAL', 'RETAIL', 'FLEET', 'SPV']):
            print(f"Row {r:3d}: " + " | ".join([f"{c}: {v}" for c, v in row_vals[:8]]))
