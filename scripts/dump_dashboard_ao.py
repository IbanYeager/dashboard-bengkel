import zipfile
import xml.etree.ElementTree as ET

with zipfile.ZipFile('data/ao_report.xlsx') as z:
    wb_xml = z.read('xl/workbook.xml')
    wb_root = ET.fromstring(wb_xml)
    ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    
    # Read shared strings
    shared_strings = []
    if 'xl/sharedStrings.xml' in z.namelist():
        ss_xml = z.read('xl/sharedStrings.xml')
        ss_root = ET.fromstring(ss_xml)
        for si in ss_root.findall('.//main:si', ns):
            t_elems = si.findall('.//main:t', ns)
            text = "".join(t.text or "" for t in t_elems)
            shared_strings.append(text)
            
    # Sheet 2
    s_xml = z.read('xl/worksheets/sheet2.xml')
    s_root = ET.fromstring(s_xml)
    
    # Merged cells
    merges = []
    for mc in s_root.findall('.//main:mergeCell', ns):
        merges.append(mc.attrib.get('ref'))
    print(f"Total merged cell ranges: {len(merges)}")
    print("Sample merges:", merges[:20])

    # Rows
    rows_data = {}
    for row in s_root.findall('.//main:row', ns):
        r_idx = int(row.attrib.get('r', 0))
        cells = {}
        for c in row.findall('.//main:c', ns):
            r_coord = c.attrib.get('r', '')
            t_type = c.attrib.get('t', '')
            v_elem = c.find('main:v', ns)
            val = v_elem.text if v_elem is not None else None
            if t_type == 's' and val is not None:
                val = shared_strings[int(val)]
            cells[r_coord] = val
        if cells:
            rows_data[r_idx] = cells

    print(f"Max row: {max(rows_data.keys()) if rows_data else 0}")
    
    with open('data/dashboard_ao_dump.txt', 'w', encoding='utf-8') as out:
        for r in sorted(rows_data.keys()):
            row_str = " | ".join(f"{k}:{rows_data[r][k]}" for k in sorted(rows_data[r].keys()) if rows_data[r][k] is not None)
            out.write(f"R{r:2d}: {row_str}\n")
            
    print("Dumped all rows to data/dashboard_ao_dump.txt")
