import zipfile
import xml.etree.ElementTree as ET

with zipfile.ZipFile('Dashboard AFS Kiaracondong-start 2024.xlsx', 'r') as z:
    wb_xml = z.read('xl/workbook.xml')
    wb_root = ET.fromstring(wb_xml)
    ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    
    target_rid = None
    for s in wb_root.findall('main:sheets/main:sheet', ns):
        if s.attrib.get('name') == 'TARGET':
            target_rid = s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
            break
            
    rels_xml = z.read('xl/_rels/workbook.xml.rels')
    rels_root = ET.fromstring(rels_xml)
    target_file = None
    for r in rels_root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
        if r.attrib.get('Id') == target_rid:
            target_file = 'xl/' + r.attrib.get('Target')
            break
            
    ss_xml = z.read('xl/sharedStrings.xml')
    ss_root = ET.fromstring(ss_xml)
    shared_strings = []
    for si in ss_root.findall('main:si', ns):
        text_parts = [t_el.text for t_el in si.findall('.//main:t', ns) if t_el.text]
        shared_strings.append(''.join(text_parts))
        
    sheet_xml = z.read(target_file)
    sheet_root = ET.fromstring(sheet_xml)
    
    print("=== ALL ROWS IN Dashboard AFS TARGET ===")
    for row in sheet_root.findall('main:sheetData/main:row', ns):
        r_idx = row.attrib.get('r', '')
        cells = {}
        for c in row.findall('main:c', ns):
            ref = c.attrib.get('r')
            t = c.attrib.get('t')
            v = c.find('main:v', ns)
            val = v.text if v is not None else ''
            if t == 's' and val.isdigit():
                val = shared_strings[int(val)]
            cells[ref] = val
        a = cells.get('A' + r_idx, '')
        b = cells.get('B' + r_idx, '')
        c_val = cells.get('C' + r_idx, '')
        d = cells.get('D' + r_idx, '')
        e = cells.get('E' + r_idx, '')
        if a or d or e:
            rev_m = float(e)/1e6 if e and e.replace('.','',1).isdigit() else 0
            print(f"Row {r_idx:>2}: {a:<15} | Year: {b:<5} | Month: {c_val:<10} | CPUS Target: {d:<6} | Rev Target: {e:<15} ({rev_m:.1f} Jt)")
