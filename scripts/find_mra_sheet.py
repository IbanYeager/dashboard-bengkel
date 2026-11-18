import zipfile
import xml.etree.ElementTree as ET

fname = 'DASH KIARACONDONG 24-26.xlsx'
with zipfile.ZipFile(fname) as z:
    # 1. Load sharedStrings
    ss_xml = z.read('xl/sharedStrings.xml')
    root_ss = ET.fromstring(ss_xml)
    strings = []
    for si in root_ss.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
        t = si.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
        if t is not None and t.text:
            strings.append(t.text)
        else:
            # check r/t
            r_ts = si.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
            strings.append(''.join([rt.text for rt in r_ts if rt.text]))

    print(f"Total shared strings: {len(strings)}")
    ranih_indices = [i for i, s in enumerate(strings) if 'ranih' in s.lower() or s.strip() == 'NURI']
    print(f"Indices for RANIH/NURI: {ranih_indices[:10]}")
    for idx in ranih_indices[:5]:
        print(f"  String {idx}: '{strings[idx]}'")

    # 2. Find sheets in workbook
    wb_xml = z.read('xl/workbook.xml')
    root_wb = ET.fromstring(wb_xml)
    sheets = {}
    for s in root_wb.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet'):
        sheets[s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')] = s.attrib.get('name')

    # 3. Read rels
    rels_xml = z.read('xl/_rels/workbook.xml.rels')
    root_rels = ET.fromstring(rels_xml)
    rel_map = {}
    for r in root_rels.findall('.//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
        rel_map[r.attrib.get('Id')] = r.attrib.get('Target')

    print("\nSheets mapping:")
    for rId, sname in sheets.items():
        target = rel_map.get(rId)
        print(f"  {sname} -> {target}")
        # Search target sheet for ranih_indices
        sheet_path = 'xl/' + target if not target.startswith('xl/') else target
        sheet_xml = z.read(sheet_path)
        # Check if any ranih_indices is in sheet_xml
        for idx in ranih_indices:
            idx_pattern = f'<v>{idx}</v>'.encode('utf-8')
            if idx_pattern in sheet_xml:
                print(f"    *** MATCH in sheet '{sname}' for string index {idx} ('{strings[idx]}')!")
                break

