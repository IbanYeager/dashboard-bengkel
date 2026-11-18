import zipfile
import xml.etree.ElementTree as ET

with zipfile.ZipFile('data/ao_report.xlsx') as z:
    # 1. Parse xl/workbook.xml to find rId for 'Dashboard AO'
    wb_xml = z.read('xl/workbook.xml')
    wb_root = ET.fromstring(wb_xml)
    ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
          'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
    
    target_rid = None
    for s in wb_root.findall('.//main:sheet', ns):
        name = s.attrib.get('name')
        rid = s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        print(f"Sheet '{name}' -> {rid}")
        if name.lower() == 'dashboard ao':
            target_rid = rid
            
    print(f"\nTarget rid for 'Dashboard AO': {target_rid}")
    
    # 2. Parse xl/_rels/workbook.xml.rels to find target xml file
    rels_xml = z.read('xl/_rels/workbook.xml.rels')
    rels_root = ET.fromstring(rels_xml)
    r_ns = {'rel': 'http://schemas.openxmlformats.org/package/2006/relationships'}
    
    sheet_target = None
    for rel in rels_root.findall('.//rel:Relationship', r_ns):
        r_id = rel.attrib.get('Id')
        tgt = rel.attrib.get('Target')
        if r_id == target_rid:
            sheet_target = tgt
            print(f"Target file for {r_id}: xl/{tgt}")

    # 3. Read shared strings
    shared_strings = []
    if 'xl/sharedStrings.xml' in z.namelist():
        ss_xml = z.read('xl/sharedStrings.xml')
        ss_root = ET.fromstring(ss_xml)
        for si in ss_root.findall('.//main:si', ns):
            t_elems = si.findall('.//main:t', ns)
            text = "".join(t.text or "" for t in t_elems)
            shared_strings.append(text)
    print(f"Shared strings count: {len(shared_strings)}")
    
    # 4. Parse the target sheet XML
    sheet_path = 'xl/' + sheet_target if not sheet_target.startswith('xl/') else sheet_target
    print(f"Parsing sheet: {sheet_path}")
    s_xml = z.read(sheet_path)
    s_root = ET.fromstring(s_xml)
    
    # Collect cell values
    rows_data = {}
    for row in s_root.findall('.//main:row', ns):
        r_idx = int(row.attrib.get('r', 0))
        cells = {}
        for c in row.findall('.//main:c', ns):
            r_coord = c.attrib.get('r', '')
            t_type = c.attrib.get('t', '')
            v_elem = c.find('main:v', ns)
            val = v_elem.text if v_elem is not None else None
            
            # format shared string
            if t_type == 's' and val is not None:
                val = shared_strings[int(val)]
                
            cells[r_coord] = val
        if cells:
            rows_data[r_idx] = cells
            
    print(f"Total rows in Dashboard AO: {len(rows_data)}")
    for r in sorted(rows_data.keys())[:65]:
        row_str = " | ".join(f"{k}:{rows_data[r][k]}" for k in sorted(rows_data[r].keys()) if rows_data[r][k] is not None)
        print(f"R{r:2d}: {row_str}")
