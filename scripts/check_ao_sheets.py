import zipfile
import xml.etree.ElementTree as ET

with zipfile.ZipFile('data/ao_report.xlsx') as z:
    wb_xml = z.read('xl/workbook.xml')
    wb_root = ET.fromstring(wb_xml)
    ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    
    shared_strings = []
    if 'xl/sharedStrings.xml' in z.namelist():
        ss_root = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in ss_root.findall('.//main:si', ns):
            t_elems = si.findall('.//main:t', ns)
            shared_strings.append(''.join(t.text or '' for t in t_elems))

    rels_xml = z.read('xl/_rels/workbook.xml.rels')
    rels_root = ET.fromstring(rels_xml)
    r_ns = {'rel': 'http://schemas.openxmlformats.org/package/2006/relationships'}
    rid_map = {rel.attrib.get('Id'): rel.attrib.get('Target') for rel in rels_root.findall('.//rel:Relationship', r_ns)}

    for s in wb_root.findall('.//main:sheet', ns):
        s_name = s.attrib.get('name')
        rid = s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        target = rid_map.get(rid)
        sheet_path = 'xl/' + target if not target.startswith('xl/') else target
        
        # Count rows in sheet
        s_xml = z.read(sheet_path)
        s_root = ET.fromstring(s_xml)
        rows = s_root.findall('.//main:row', ns)
        print(f"Sheet '{s_name}' ({sheet_path}): {len(rows)} rows")
