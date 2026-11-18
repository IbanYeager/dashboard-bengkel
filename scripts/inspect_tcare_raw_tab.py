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
    # sheet3 is RAW DATA T-CARE
    sheet_root = ET.fromstring(z.read('xl/worksheets/sheet3.xml'))

def col_str(c_idx):
    res = ''
    while c_idx > 0:
        c_idx, rem = divmod(c_idx - 1, 26)
        res = chr(ord('A') + rem) + res
    return res

grid = {}
row_count = 0
for row_elem in sheet_root.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheetData/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
    r_num = int(row_elem.attrib['r'])
    row_count = max(row_count, r_num)
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

print(f"Total rows in RAW DATA T-CARE: {row_count}")

# Print headers (row 1 or 2)
for r in range(1, min(5, row_count + 1)):
    items = [(col_str(c), grid.get((r, c))) for c in range(1, 40) if (r, c) in grid and grid.get((r, c))]
    if items:
        print(f"Row {r}: {items}")

# Sample row 3
items = [(col_str(c), grid.get((3, c))) for c in range(1, 40) if (3, c) in grid and grid.get((3, c))]
print("Row 3 sample:", items[:12])
