import zipfile
import xml.etree.ElementTree as ET

with zipfile.ZipFile('DASH KIARACONDONG 24-26.xlsx', 'r') as z:
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels}
    for s in wb.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet'):
        if s.attrib['name'] == 'INPUT PKB':
            r_id = s.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
            sheet_target = 'xl/' + rel_map[r_id]

            shared_strings = []
            if 'xl/sharedStrings.xml' in z.namelist():
                ss_tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
                for si in ss_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
                    shared_strings.append(''.join([node.text for node in si.iter() if node.text]))

            # Find last 10 rows
            rows_data = []
            sf = z.open(sheet_target)
            for event, elem in ET.iterparse(sf, events=('end',)):
                if elem.tag.endswith('row'):
                    r_num = int(elem.attrib['r'])
                    cells = {}
                    for c in elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                        ref = c.attrib['r']
                        col = ''.join([ch for ch in ref if ch.isalpha()])
                        t = c.attrib.get('t')
                        v_el = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                        v_txt = v_el.text if v_el is not None else ''
                        if t == 's' and v_txt:
                            v_txt = shared_strings[int(v_txt)]
                        cells[col] = v_txt
                    rows_data.append((r_num, cells))
                    if len(rows_data) > 10:
                        rows_data.pop(0)
                    elem.clear()

            print("Last rows in INPUT PKB:")
            for r_num, cells in rows_data:
                print(f"Row {r_num}: A(tgl)='{cells.get('A')}' B(bln)='{cells.get('B')}' C(thn)='{cells.get('C')}' BN(month)='{cells.get('BN')}' K(pkb)='{cells.get('K')}'")
