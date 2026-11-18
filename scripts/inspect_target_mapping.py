import zipfile
import xml.etree.ElementTree as ET

def get_shared_strings(z):
    shared_strings = []
    if 'xl/sharedStrings.xml' in z.namelist():
        with z.open('xl/sharedStrings.xml') as f:
            for event, elem in ET.iterparse(f, events=('end',)):
                if elem.tag.endswith('si'):
                    text = ''.join([t.text for t in elem.iter() if t.tag.endswith('t') and t.text])
                    shared_strings.append(text)
                    elem.clear()
    return shared_strings

# Let's inspect TARGET sheet in DASH KIARACONDONG 24-26.xlsx
with zipfile.ZipFile('DASH KIARACONDONG 24-26.xlsx', 'r') as z:
    wb_root = ET.fromstring(z.read('xl/workbook.xml'))
    rels_root = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels_root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')}
    sheet_files = {s.attrib.get('name'): 'xl/' + rel_map[s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')].lstrip('/') for s in wb_root.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet')}
    
    shared_strings = get_shared_strings(z)
    
    print("=== TARGET SHEET IN DASH KIARACONDONG 24-26.xlsx ===")
    target_grid = {}
    with z.open(sheet_files['TARGET']) as sf:
        for event, elem in ET.iterparse(sf, events=('end',)):
            if elem.tag.endswith('row'):
                r = int(elem.attrib.get('r'))
                if r in [1, 2, 4, 5, 10, 12, 21, 22]:
                    for c in elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                        ref = c.attrib.get('r')
                        col = ''.join([ch for ch in ref if ch.isalpha()])
                        t = c.attrib.get('t')
                        v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                        val = ""
                        if v is not None and v.text:
                            val = shared_strings[int(v.text)] if t == 's' and int(v.text) < len(shared_strings) else v.text
                        target_grid[(r, col)] = val
                elem.clear()

    # Map month cols
    cols_sorted = sorted([c for (r, c) in target_grid if r == 1], key=lambda x: (len(x), x))
    for c in cols_sorted:
        m_label = target_grid.get((1, c), '')
        target_cpus = target_grid.get((5, c), '')
        sbi_cpus = target_grid.get((22, c), '')
        print(f"Col {c:2s}: Month={m_label:15s} | Target CPUS={target_cpus:6s} | SBI CPUS={sbi_cpus:5s}")
