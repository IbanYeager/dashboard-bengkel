import zipfile
import xml.etree.ElementTree as ET
import re

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
        if sheet.attrib['name'] == 'DASHBOARD':
            r_id = sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
            t_path = 'xl/' + rel_map[r_id] if not rel_map[r_id].startswith('xl/') else rel_map[r_id]
            st = ET.fromstring(z.read(t_path))
            for r in st.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheetData/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
                r_num = int(r.attrib['r'])
                if r_num in range(12, 30):
                    cells = {}
                    for c in r.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                        ref = c.attrib['r']
                        col = re.match(r'([A-Z]+)', ref).group(1)
                        t = c.attrib.get('t')
                        v_el = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                        val = ''
                        if v_el is not None and v_el.text:
                            val = ss[int(v_el.text)] if t == 's' else v_el.text
                        cells[col] = val
                    row_vals = [f"{k}:{v}" for k, v in sorted(cells.items()) if v]
                    print(f"Row {r_num:2}: " + " | ".join(row_vals[:16]))
