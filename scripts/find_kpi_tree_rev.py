import zipfile
import xml.etree.ElementTree as ET

filename = 'DASH KIARACONDONG 24-26.xlsx'
with zipfile.ZipFile(filename, 'r') as z:
    wb_tree = ET.fromstring(z.read('xl/workbook.xml'))
    rels_tree = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels_tree.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')}
    
    target_path = None
    for s in wb_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet'):
        if s.attrib.get('name').strip().lower() == 'kpi tree':
            rId = s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
            target_path = 'xl/' + rel_map[rId].lstrip('/')
            break

    ss_tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
    shared_strings = []
    for si in ss_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
        t = si.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
        if t is not None and t.text is not None:
            shared_strings.append(t.text)
        else:
            txt = ''.join([elem.text for elem in si.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t') if elem.text])
            shared_strings.append(txt)

    print(f"Finding Revenue in KPI TREE...")
    with z.open(target_path) as f:
        for event, elem in ET.iterparse(f, events=('end',)):
            if elem.tag.endswith('row'):
                r_idx = int(elem.attrib.get('r', 0))
                for c in elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                    ref = c.attrib.get('r')
                    f_elem = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}f')
                    v_elem = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                    t = c.attrib.get('t')
                    val = shared_strings[int(v_elem.text)] if (t == 's' and v_elem is not None and v_elem.text) else (v_elem.text if v_elem is not None else '')
                    if 'REVENUE' in str(val).upper() or (f_elem is not None and f_elem.text and 'SUMIFS' in f_elem.text and 'BF' in f_elem.text):
                        print(f"Row {r_idx} | Cell {ref}: val='{val}' | formula={f_elem.text if f_elem is not None else ''}")
                elem.clear()
