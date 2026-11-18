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
            print('INPUT PKB sheet target:', sheet_target)

            shared_strings = []
            if 'xl/sharedStrings.xml' in z.namelist():
                ss_tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
                for si in ss_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
                    shared_strings.append(''.join([node.text for node in si.iter() if node.text]))

            sf = z.open(sheet_target)
            for event, elem in ET.iterparse(sf, events=('end',)):
                if elem.tag.endswith('row'):
                    r_num = int(elem.attrib['r'])
                    if 2 <= r_num <= 5:
                        cells = {}
                        for c in elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                            ref = c.attrib['r']
                            col = ''.join([ch for ch in ref if ch.isalpha()])
                            t = c.attrib.get('t')
                            f_el = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}f')
                            v_el = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                            f_txt = f_el.text if f_el is not None else None
                            v_txt = v_el.text if v_el is not None else ''
                            if t == 's' and v_txt:
                                v_txt = shared_strings[int(v_txt)]
                            cells[col] = (v_txt, f_txt)
                        print(f"Row {r_num}: A={cells.get('A')} B={cells.get('B')} C={cells.get('C')} M={cells.get('M')} BN={cells.get('BN')} BO={cells.get('BO')}")
                    if r_num > 5:
                        break
                    elem.clear()
