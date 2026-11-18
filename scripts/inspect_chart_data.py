import zipfile
import xml.etree.ElementTree as ET

wb_path = 'data/tcare_live.xlsx'
with zipfile.ZipFile(wb_path, 'r') as z:
    # Read shared strings
    sst = []
    if 'xl/sharedStrings.xml' in z.namelist():
        sst_tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in sst_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
            t = ''.join([node.text for node in si.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t') if node.text])
            sst.append(t)
    
    def get_sheet_cells(sheet_name):
        tree = ET.fromstring(z.read(sheet_name))
        cells = {}
        for row in tree.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
            r_idx = row.attrib.get('r')
            for c in row.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                ref = c.attrib.get('r')
                t = c.attrib.get('t')
                v_el = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                val = v_el.text if v_el is not None else None
                if t == 's' and val is not None:
                    val = sst[int(val)]
                cells[ref] = val
        return cells

    dash_cells = get_sheet_cells('xl/worksheets/sheet2.xml')
    rekap_cells = get_sheet_cells('xl/worksheets/sheet4.xml')

    print("--- CHART 2 DATA ---")
    print("D20:G20:", [dash_cells.get(f"{col}20") for col in ["D","E","F","G"]])
    for r in [21, 22, 23]:
        print(f"Row {r} (C={dash_cells.get(f'C{r}')}):", [dash_cells.get(f"{col}{r}") for col in ["D","E","F","G"]])

    print("\n--- CHART 1 & 8 (DEC BY AREA) ---")
    for r in range(10, 14):
        print(f"Row {r}: Y={dash_cells.get(f'Y{r}')}, Z={dash_cells.get(f'Z{r}')}, AA={dash_cells.get(f'AA{r}')}")

    print("\n--- CHART 3 & 9 (CUST TYPE) ---")
    for r in range(8, 10):
        print(f"Row {r}: Y={dash_cells.get(f'Y{r}')}, Z={dash_cells.get(f'Z{r}')}, AA={dash_cells.get(f'AA{r}')}")

    print("\n--- CHART 4 & 10 (VEHICLE TYPE) ---")
    for r in range(22, 25):
        print(f"Row {r}: Y={dash_cells.get(f'Y{r}')}, Z={dash_cells.get(f'Z{r}')}, AA={dash_cells.get(f'AA{r}')}")

    print("\n--- CHART 5 & 11 (PUNCTUAL) ---")
    for r in range(18, 20):
        print(f"Row {r}: Y={dash_cells.get(f'Y{r}')}, Z={dash_cells.get(f'Z{r}')}, AA={dash_cells.get(f'AA{r}')}")

    print("\n--- CHART 6 (LCGC) ---")
    for r in range(32, 36):
        print(f"Row {r}: H={dash_cells.get(f'H{r}')}, I={dash_cells.get(f'I{r}')}, J={dash_cells.get(f'J{r}')}, K={dash_cells.get(f'K{r}')}")

    print("\n--- CHART 7 (CAI OWN SALES) ---")
    print("Row 124 (Cat):", [dash_cells.get(f"{col}124") for col in ["B","C","D","E","F","G","H"]])
    print("Row 125 (Val):", [dash_cells.get(f"{col}125") for col in ["B","C","D","E","F","G","H"]])

    print("\n--- CHART 12 (REKAP 929-936) ---")
    print("Rekap 929:", [rekap_cells.get(f"{col}929") for col in ["A","B","C","D"]])
    for r in range(930, 937):
        print(f"Rekap {r}:", [rekap_cells.get(f"{col}{r}") for col in ["A","B","C","D"]])

    print("\n--- CHART 13 (REMARK FOLLOW UP) ---")
    for r in range(114, 126):
        if dash_cells.get(f"AI{r}") or dash_cells.get(f"AJ{r}"):
            print(f"Row {r}: AI={dash_cells.get(f'AI{r}')}, AJ={dash_cells.get(f'AJ{r}')}")
