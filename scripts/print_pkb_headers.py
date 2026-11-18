import zipfile
import xml.etree.ElementTree as ET

EXCEL_PATH = r"c:\laragon\www\dashboard_bengkel\DASH KIARACONDONG 24-26.xlsx"

with zipfile.ZipFile(EXCEL_PATH, 'r') as z:
    wb_root = ET.fromstring(z.read('xl/workbook.xml'))
    rels_root = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels_root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')}
    sheet_files = {}
    for s in wb_root.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet'):
        s_name = s.attrib.get('name').strip()
        rId = s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        sheet_files[s_name.lower()] = 'xl/' + rel_map[rId].lstrip('/')

    ss_tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
    shared_strings = []
    for si in ss_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
        t = si.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
        if t is not None and t.text is not None:
            shared_strings.append(t.text)
        else:
            txt = ''.join([elem.text for elem in si.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t') if elem.text])
            shared_strings.append(txt)

    pkb_file = sheet_files['input pkb']
    print(f"Reading row 1 from {pkb_file}...")
    headers = {}
    with z.open(pkb_file) as f:
        for event, elem in ET.iterparse(f, events=('end',)):
            if elem.tag.endswith('row'):
                r = elem.attrib.get('r')
                if r == '1':
                    for c in elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                        ref = c.attrib.get('r')
                        col = ''.join([ch for ch in ref if ch.isalpha()])
                        t = c.attrib.get('t')
                        v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                        val = shared_strings[int(v.text)] if (t == 's' and v is not None and v.text) else (v.text if v is not None else '')
                        headers[col] = val
                    break
                elem.clear()

print("Headers in INPUT PKB:")
for col, name in sorted(headers.items(), key=lambda x: (len(x[0]), x[0])):
    print(f"  Col {col}: {name}")
