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

    shared_strings = []
    with z.open('xl/sharedStrings.xml') as f:
        for event, elem in ET.iterparse(f, events=('end',)):
            if elem.tag.endswith('si'):
                text = "".join([t.text for t in elem.iter() if t.tag.endswith('t') and t.text])
                shared_strings.append(text)
                elem.clear()

    so_file = sheet_files.get('daftar list so')
    with z.open(so_file) as f:
        for event, elem in ET.iterparse(f, events=('end',)):
            if elem.tag.endswith('row'):
                if elem.attrib.get('r') == '1':
                    headers = {}
                    for c in elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                        ref = c.attrib.get('r')
                        col = ''.join([ch for ch in ref if ch.isalpha()])
                        t = c.attrib.get('t')
                        v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                        val = ""
                        if v is not None and v.text is not None:
                            val = shared_strings[int(v.text)] if t == 's' else v.text
                        headers[col] = val
                    for col in sorted(headers.keys(), key=lambda x: (len(x), x)):
                        print(f"{col:4}: {headers[col]}")
                    break
