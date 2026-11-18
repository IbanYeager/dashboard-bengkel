import zipfile
import xml.etree.ElementTree as ET

with zipfile.ZipFile('KPI Dashboard Kabeng GR-ags.xlsx') as z:
    shared_strings = []
    if 'xl/sharedStrings.xml' in z.namelist():
        ss_tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in ss_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
            t = ''.join([node.text for node in si.iter() if node.text])
            shared_strings.append(t)

    wb_tree = ET.fromstring(z.read('xl/workbook.xml'))
    rels_tree = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels_tree}

    for sheet in wb_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet'):
        s_name = sheet.attrib['name']
        r_id = sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
        target = 'xl/' + rel_map[r_id] if not rel_map[r_id].startswith('xl/') else rel_map[r_id]
        sheet_xml = z.read(target)
        s_tree = ET.fromstring(sheet_xml)
        
        found = []
        for row in s_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheetData/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
            r_num = row.attrib.get('r')
            for c in row.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                t = c.attrib.get('t')
                v_el = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                if v_el is not None and v_el.text:
                    val = v_el.text
                    if t == 's':
                        val = shared_strings[int(val)]
                    if any(k in str(val).lower() for k in ['kiara', 'kircon']):
                        found.append((c.attrib.get('r'), val))
        if found:
            print(f'Sheet "{s_name}" has matches ({len(found)}):', found[:10])
        else:
            print(f'Sheet "{s_name}": no kiara match')
