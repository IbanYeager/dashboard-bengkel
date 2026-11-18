import zipfile
import xml.etree.ElementTree as ET

wb_path = 'data/tcare_live.xlsx'
with zipfile.ZipFile(wb_path, 'r') as z:
    sst = []
    if 'xl/sharedStrings.xml' in z.namelist():
        sst_tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in sst_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
            t = ''.join([node.text for node in si.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t') if node.text])
            sst.append(t)
            
    tree = ET.fromstring(z.read('xl/worksheets/sheet2.xml'))
    rows = {}
    for row in tree.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
        r_idx = int(row.attrib.get('r'))
        cells = []
        for c in row.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
            ref = c.attrib.get('r')
            t = c.attrib.get('t')
            v_el = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
            val = v_el.text if v_el is not None else None
            if t == 's' and val is not None:
                val = sst[int(val)]
            if val is not None:
                cells.append(f"{ref}:{val}")
        if cells:
            rows[r_idx] = cells
            
    for r in sorted(rows.keys()):
        # print first few cells or header-like rows
        line = " | ".join(rows[r])
        if len(line) > 120:
            line = line[:120] + "..."
        print(f"Row {r:3d}: {line}")
