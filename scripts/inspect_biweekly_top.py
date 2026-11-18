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

with zipfile.ZipFile('DASH KIARACONDONG 24-26.xlsx', 'r') as z:
    wb_root = ET.fromstring(z.read('xl/workbook.xml'))
    rels_root = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels_root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')}
    sheet_files = {s.attrib.get('name'): 'xl/' + rel_map[s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')].lstrip('/') for s in wb_root.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet')}
    
    shared_strings = get_shared_strings(z)
    
    grid = {}
    with z.open(sheet_files['BIWEEKLY']) as sf:
        for event, elem in ET.iterparse(sf, events=('end',)):
            if elem.tag.endswith('row'):
                r = int(elem.attrib.get('r'))
                for c in elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                    ref = c.attrib.get('r')
                    col = ''.join([ch for ch in ref if ch.isalpha()])
                    t = c.attrib.get('t')
                    v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                    f = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}f')
                    val = ""
                    if v is not None and v.text:
                        val = shared_strings[int(v.text)] if t == 's' and int(v.text) < len(shared_strings) else v.text
                    f_txt = f.text if f is not None and f.text else ""
                    grid[(r, col)] = (val, f_txt)
                elem.clear()

    print("=== B1, B2 (MONTH, YEAR) ===")
    print(f"B1: {grid.get((1, 'B'))}")
    print(f"B2: {grid.get((2, 'B'))}")

    print("\n=== TYPE CUST (AE18:AG24) ===")
    for r in range(18, 25):
        print(f"Row {r}: " + " | ".join([f"{c}='{grid.get((r,c),('',''))[0]}' [f={grid.get((r,c),('',''))[1]}]" for c in ['AE','AF','AG']]))

    print("\n=== CPUS COMPOSITION (AL18:AR24) ===")
    for r in range(18, 24):
        print(f"Row {r}: " + " | ".join([f"{c}='{grid.get((r,c),('',''))[0]}' [f={grid.get((r,c),('',''))[1]}]" for c in ['AL','AM','AN','AO','AP','AQ','AR']]))

    print("\n=== KOMPOSISI UE (AL24:AR28) ===")
    for r in range(24, 29):
        print(f"Row {r}: " + " | ".join([f"{c}='{grid.get((r,c),('',''))[0]}' [f={grid.get((r,c),('',''))[1]}]" for c in ['AL','AM','AN','AO','AP','AQ','AR']]))
