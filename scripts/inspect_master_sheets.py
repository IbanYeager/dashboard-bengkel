import zipfile
import xml.etree.ElementTree as ET

filename = 'DASH KIARACONDONG 24-26.xlsx'
with zipfile.ZipFile(filename, 'r') as z:
    wb_tree = ET.fromstring(z.read('xl/workbook.xml'))
    rels_tree = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels_tree.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')}
    sheet_files = {s.attrib.get('name').strip().lower(): 'xl/' + rel_map[s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')].lstrip('/') for s in wb_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet')}

    ss_tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
    shared_strings = []
    for si in ss_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
        t = si.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
        if t is not None and t.text is not None:
            shared_strings.append(t.text)
        else:
            txt = ''.join([elem.text for elem in si.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t') if elem.text])
            shared_strings.append(txt)

    for s_name in ['db vin merdeka', 'master', 'master job']:
        path = sheet_files.get(s_name)
        if not path:
            continue
        print(f"\n--- Headers for {s_name} ({path}) ---")
        with z.open(path) as f:
            for event, elem in ET.iterparse(f, events=('end',)):
                if elem.tag.endswith('row'):
                    r = elem.attrib.get('r')
                    if r == '1':
                        cols = {}
                        for c in elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                            ref = c.attrib.get('r')
                            col = ''.join([ch for ch in ref if ch.isalpha()])
                            t = c.attrib.get('t')
                            v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                            val = shared_strings[int(v.text)] if (t == 's' and v is not None and v.text) else (v.text if v is not None else '')
                            cols[col] = val
                        for k in sorted(cols.keys(), key=lambda x: (len(x), x)):
                            print(f"  {k}: {cols[k]}")
                        break
                    elem.clear()
