import zipfile
import xml.etree.ElementTree as ET

with zipfile.ZipFile('data/ao_report.xlsx') as z:
    shared_strings = []
    ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    if 'xl/sharedStrings.xml' in z.namelist():
        ss_root = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in ss_root.findall('.//main:si', ns):
            t_elems = si.findall('.//main:t', ns)
            shared_strings.append("".join(t.text or "" for t in t_elems))

    s_root = ET.fromstring(z.read('xl/worksheets/sheet2.xml'))
    
    # Let's map cells by (row, col)
    # col letter to num
    def col2num(col_str):
        num = 0
        for ch in col_str:
            num = num * 26 + (ord(ch) - ord('A') + 1)
        return num
    def num2col(num):
        res = ""
        while num > 0:
            num, rem = divmod(num - 1, 26)
            res = chr(ord('A') + rem) + res
        return res

    import re
    grid = {}
    for row in s_root.findall('.//main:row', ns):
        r_num = int(row.attrib.get('r'))
        for c in row.findall('.//main:c', ns):
            coord = c.attrib.get('r')
            m = re.match(r'([A-Z]+)(\d+)', coord)
            if not m: continue
            col_str, row_str = m.groups()
            c_num = col2num(col_str)
            
            t_type = c.attrib.get('t', '')
            v_elem = c.find('main:v', ns)
            val = v_elem.text if v_elem is not None else ""
            if t_type == 's' and val:
                val = shared_strings[int(val)]
            if val:
                grid[(r_num, c_num)] = val

    print(f"Loaded {len(grid)} non-empty cells in Dashboard AO.")
    
    # Print grid representation for rows 1 to 70, columns A (1) to Z (26)
    print("\n--- VISUAL GRID ROWS 1-70 ---")
    for r in range(1, 71):
        row_cells = []
        for c in range(1, 27):
            v = grid.get((r, c), '')
            if v:
                row_cells.append(f"{num2col(c)}:{v}")
        if row_cells:
            print(f"Row {r:2d} | " + " | ".join(row_cells))
