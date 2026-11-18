import zipfile
import xml.etree.ElementTree as ET
import re

def col2num(col):
    num = 0
    for c in col:
        num = num * 26 + (ord(c) - ord('A')) + 1
    return num

with zipfile.ZipFile('KPI Dashboard Kabeng GR-ags.xlsx') as z:
    shared_strings = []
    if 'xl/sharedStrings.xml' in z.namelist():
        ss_tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in ss_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
            t = ''.join([node.text for node in si.iter() if node.text])
            shared_strings.append(t)

    wb_tree = ET.fromstring(z.read('xl/workbook.xml'))
    rels_tree = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels_tree}

    target_sheet = None
    for sheet in wb_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet'):
        if sheet.attrib['name'] == 'Dash update':
            r_id = sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
            target_sheet = 'xl/' + rel_map[r_id] if not rel_map[r_id].startswith('xl/') else rel_map[r_id]
            break

    sheet_xml = z.read(target_sheet)
    s_tree = ET.fromstring(sheet_xml)

    rows = []
    for r in s_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheetData/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
        r_num = int(r.attrib['r'])
        cells = {}
        for c in r.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
            ref = c.attrib['r']
            m = re.match(r'([A-Z]+)(\d+)', ref)
            col_letters = m.group(1)
            t = c.attrib.get('t')
            v_el = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
            val = ''
            if v_el is not None and v_el.text:
                val = v_el.text
                if t == 's':
                    val = shared_strings[int(val)]
            cells[col_letters] = val
        rows.append((r_num, cells))

    print(f"Total rows in Dash update: {len(rows)}")
    for r_num, cells in rows[:60]:
        line = " | ".join([f"{k}:{cells[k]}" for k in sorted(cells.keys(), key=col2num) if cells[k] != ''])
        if line:
            print(f"R{r_num}: {line}")
