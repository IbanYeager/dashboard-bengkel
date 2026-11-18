import zipfile
import xml.etree.ElementTree as ET
import re

XLSX_PATH = r'c:\laragon\www\dashboard_bengkel\data\tcare_live.xlsx'

print("Loading shared strings...")
shared_strings = []
with zipfile.ZipFile(XLSX_PATH, 'r') as z:
    with z.open('xl/sharedStrings.xml') as f:
        for event, elem in ET.iterparse(f, events=('end',)):
            if elem.tag.endswith('si'):
                text = "".join([t.text for t in elem.iter() if t.tag.endswith('t') and t.text])
                shared_strings.append(text)
                elem.clear()

print(f"Total shared strings: {len(shared_strings)}")

# Parse sheet2.xml (DASHBOARD)
with zipfile.ZipFile(XLSX_PATH, 'r') as z:
    sheet_root = ET.fromstring(z.read('xl/worksheets/sheet2.xml'))

# Merged cells
merge_cells = []
for mc in sheet_root.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}mergeCells/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}mergeCell'):
    merge_cells.append(mc.attrib.get('ref'))

print(f"Total merged cells: {len(merge_cells)}")
print("Sample merged cells:", merge_cells[:20])

def cell_ref_to_coord(ref):
    col = ''.join(c for c in ref if c.isalpha())
    row = int(''.join(c for c in ref if c.isdigit()))
    col_idx = 0
    for ch in col:
        col_idx = col_idx * 26 + (ord(ch) - ord('A') + 1)
    return row, col_idx, col

grid = {}
max_row = 0
max_col = 0

for row_elem in sheet_root.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheetData/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
    r_num = int(row_elem.attrib['r'])
    max_row = max(max_row, r_num)
    for c_elem in row_elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
        ref = c_elem.attrib['r']
        r, col_num, col_letters = cell_ref_to_coord(ref)
        max_col = max(max_col, col_num)
        t = c_elem.attrib.get('t')
        v_elem = c_elem.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
        f_elem = c_elem.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}f')
        val = ''
        if v_elem is not None and v_elem.text:
            if t == 's':
                s_idx = int(v_elem.text)
                val = shared_strings[s_idx] if s_idx < len(shared_strings) else ''
            else:
                val = v_elem.text
        formula = f_elem.text if f_elem is not None else ''
        grid[(r, col_num)] = {
            'ref': ref,
            'val': val,
            'formula': formula
        }

print(f"Grid dimensions: rows 1 to {max_row}, cols 1 to {max_col}")

# Print the layout block by block
# Let's inspect rows 1 to 78
for r in range(1, max_row + 1):
    row_cells = []
    for c in range(1, max_col + 1):
        cell = grid.get((r, c))
        if cell and cell['val'].strip():
            row_cells.append(f"{cell['ref']}: {cell['val'].strip()[:35]}")
    if row_cells:
        print(f"R{r:2d} | " + " | ".join(row_cells[:8]))
        if len(row_cells) > 8:
            print("    | " + " | ".join(row_cells[8:16]))
        if len(row_cells) > 16:
            print("    | " + " | ".join(row_cells[16:24]))
