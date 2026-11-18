import zipfile
import xml.etree.ElementTree as ET

EXCEL_AFS = 'Dashboard AFS Kiaracondong-start 2024.xlsx'
with zipfile.ZipFile(EXCEL_AFS, 'r') as z:
    ss = []
    if 'xl/sharedStrings.xml' in z.namelist():
        tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
            t = ''.join([n.text for n in si.iter() if n.text])
            ss.append(t)
            
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels}
    
    for sheet in wb.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet'):
        s_name = sheet.attrib['name']
        if any(k in s_name.upper() for k in ['SA', 'CPUS', 'BREAKDOWN', 'DASHBOARD']):
            r_id = sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
            target = rel_map[r_id]
            t_path = 'xl/' + target if not target.startswith('xl/') else target
            print(f"Sheet: {s_name:25} -> {t_path}")
            # Read first 50 rows
            st = ET.fromstring(z.read(t_path))
            rows = st.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheetData/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row')
            print(f"  Rows count: {len(rows)}")
            # Search for 2026 or July or 829 or 779 in text
            found_july = []
            for r in rows[:35]:
                for c in r.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                    v_el = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                    t = c.attrib.get('t')
                    if v_el is not None and v_el.text:
                        val = ss[int(v_el.text)] if t == 's' else v_el.text
                        if any(term in str(val).lower() for term in ['juli', 'july', '829', '779', '1241872']):
                            found_july.append((c.attrib['r'], val))
            if found_july:
                print(f"  Found July references in {s_name}: {found_july[:5]}")
