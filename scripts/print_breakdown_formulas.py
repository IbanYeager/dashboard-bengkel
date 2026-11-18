import zipfile
import xml.etree.ElementTree as ET

filename = 'Dashboard AFS Kiaracondong-start 2024.xlsx'
with zipfile.ZipFile(filename, 'r') as z:
    wb_tree = ET.fromstring(z.read('xl/workbook.xml'))
    rels_tree = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels_tree.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')}
    
    target_path = None
    for s in wb_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet'):
        if s.attrib.get('name').strip().lower() == 'breakdown':
            rId = s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
            target_path = 'xl/' + rel_map[rId].lstrip('/')
            break
        
    print(f"Formulas in BREAKDOWN rows 14-23:")
    with z.open(target_path) as f:
        for event, elem in ET.iterparse(f, events=('end',)):
            if elem.tag.endswith('row'):
                r_idx = int(elem.attrib.get('r', 0))
                if 14 <= r_idx <= 23:
                    for c in elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                        ref = c.attrib.get('r')
                        f_elem = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}f')
                        if f_elem is not None and f_elem.text:
                            print(f"  {ref}: {f_elem.text}")
                elem.clear()
