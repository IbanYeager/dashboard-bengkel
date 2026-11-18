import zipfile
import xml.etree.ElementTree as ET

filename = 'DASH KIARACONDONG 24-26.xlsx'

# Let's check a sample PKB / WO number that appears in both INPUT PKB and Daftar List SO
# In INPUT PKB: Col K is PKB No. Col BF is REVENUE.
# In Daftar List SO: Col P is WO (Work Order / PKB No). Col AO is Transaction Amount. Col AR is Total Transaction Amount.

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

    # Let's inspect formula of Col BF in INPUT PKB!
    pkb_path = sheet_files['input pkb']
    print(f"Inspecting formula of Col BF in {pkb_path}...")
    with z.open(pkb_path) as f:
        for event, elem in ET.iterparse(f, events=('end',)):
            if elem.tag.endswith('row'):
                r_idx = int(elem.attrib.get('r', 0))
                if 2 <= r_idx <= 6:
                    for c in elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                        ref = c.attrib.get('r')
                        if ref.startswith('BF'):
                            f_elem = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}f')
                            v_elem = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                            print(f"  Row {r_idx} BF: val={v_elem.text if v_elem is not None else ''} | formula={f_elem.text if f_elem is not None else ''}")
                elem.clear()
