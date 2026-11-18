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
    with z.open(sheet_files['KPI TREE']) as sf:
        for event, elem in ET.iterparse(sf, events=('end',)):
            if elem.tag.endswith('row'):
                r = int(elem.attrib.get('r'))
                if 62 <= r <= 68:
                    for c in elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                        ref = c.attrib.get('r')
                        col = ''.join([ch for ch in ref if ch.isalpha()])
                        t = c.attrib.get('t')
                        v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                        val = ""
                        if v is not None and v.text:
                            val = shared_strings[int(v.text)] if t == 's' and int(v.text) < len(shared_strings) else v.text
                        grid[(r, col)] = val
                elem.clear()

    # Columns H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z, AA, AB, AC, AD, AE
    cols = ['H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','AA','AB','AC','AD','AE']
    print("=== KPI TREE CPUS BY MONTH (2026 vs 2025) ===")
    for i in range(0, len(cols), 2):
        c_cur = cols[i]
        c_ly = cols[i+1]
        m_label = grid.get((62, c_cur), '')
        ly_label = grid.get((62, c_ly), '')
        cpus_cur = grid.get((67, c_cur), '')
        cpus_ly = grid.get((67, c_ly), '')
        target_cur = grid.get((68, c_cur), '')
        target_ly = grid.get((68, c_ly), '')
        print(f"{m_label} | {ly_label} -> CPUS 2026: {cpus_cur} | CPUS 2025: {cpus_ly}")
