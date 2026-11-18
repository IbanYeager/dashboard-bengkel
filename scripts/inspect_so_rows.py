import zipfile
import xml.etree.ElementTree as ET

wb_path = r"c:\laragon\www\dashboard_bengkel\DASH KIARACONDONG 24-26.xlsx"

with zipfile.ZipFile(wb_path, 'r') as z:
    wb_root = ET.fromstring(z.read('xl/workbook.xml'))
    rels_root = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels_root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')}
    sheet_files = {}
    for s in wb_root.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet'):
        s_name = s.attrib.get('name').strip()
        rId = s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        sheet_files[s_name.lower()] = 'xl/' + rel_map[rId].lstrip('/')

    print("Sheet files:", sheet_files)

    # Let's inspect shared strings count
    print("Reading shared strings sample...")
    shared_strings = []
    with z.open('xl/sharedStrings.xml') as f:
        for event, elem in ET.iterparse(f, events=('end',)):
            if elem.tag.endswith('si'):
                text = "".join([t.text for t in elem.iter() if t.tag.endswith('t') and t.text])
                shared_strings.append(text)
                elem.clear()
    print("Shared strings count:", len(shared_strings))

    # Check Daftar List SO rows around 145560 - 145580
    so_file = sheet_files.get('daftar list so')
    print("Inspecting SO file:", so_file)
    target_rows = set(range(145560, 145580))
    last_row_seen = 0
    max_row = 0
    didin_rows = []

    with z.open(so_file) as f:
        for event, elem in ET.iterparse(f, events=('end',)):
            if elem.tag.endswith('row'):
                r_idx = int(elem.attrib.get('r', 0))
                max_row = max(max_row, r_idx)
                if r_idx in target_rows:
                    cols = {}
                    for c in elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                        ref = c.attrib.get('r')
                        col = ''.join([ch for ch in ref if ch.isalpha()])
                        t = c.attrib.get('t')
                        v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                        val = ""
                        if v is not None and v.text is not None:
                            val = shared_strings[int(v.text)] if t == 's' else v.text
                        cols[col] = val
                    print(f"Row {r_idx}: B={cols.get('B')}, C={cols.get('C')}, D={cols.get('D')}, F={cols.get('F')}, G={cols.get('G')}, L={cols.get('L')}, AD={cols.get('AD')}, AH={cols.get('AH')}, AO={cols.get('AO')}, AR={cols.get('AR')}")
                    if r_idx == 145569:
                        print(f"ALL COLS FOR 145569: {cols}")
                elem.clear()

    print(f"Max row in Daftar List SO: {max_row}")

    # Also check max row in INPUT PKB
    pkb_file = sheet_files.get('input pkb')
    max_pkb_row = 0
    with z.open(pkb_file) as f:
        for event, elem in ET.iterparse(f, events=('end',)):
            if elem.tag.endswith('row'):
                r_idx = int(elem.attrib.get('r', 0))
                max_pkb_row = max(max_pkb_row, r_idx)
                elem.clear()
    print(f"Max row in INPUT PKB: {max_pkb_row}")
