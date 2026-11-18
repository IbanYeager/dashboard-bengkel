import zipfile
import xml.etree.ElementTree as ET

def inspect_xlsx_sheet(xlsx_path, sheet_name_target):
    with zipfile.ZipFile(xlsx_path, 'r') as z:
        # 1. Read workbook.xml to find sheet rId
        wb_xml = z.read('xl/workbook.xml')
        wb_root = ET.fromstring(wb_xml)
        ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
              'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
        
        target_rid = None
        for s in wb_root.findall('main:sheets/main:sheet', ns):
            if s.attrib.get('name') == sheet_name_target:
                target_rid = s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                break
        
        if not target_rid:
            print(f"Sheet {sheet_name_target} not found in {xlsx_path}")
            return
        
        # 2. Read workbook.xml.rels to find target xml file
        rels_xml = z.read('xl/_rels/workbook.xml.rels')
        rels_root = ET.fromstring(rels_xml)
        target_file = None
        for r in rels_root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
            if r.attrib.get('Id') == target_rid:
                target_file = 'xl/' + r.attrib.get('Target')
                break
        
        print(f"Sheet '{sheet_name_target}' is in {target_file}")
        
        # 3. Read sharedStrings.xml if exists
        shared_strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            ss_xml = z.read('xl/sharedStrings.xml')
            ss_root = ET.fromstring(ss_xml)
            for si in ss_root.findall('main:si', ns):
                t = si.find('main:t', ns)
                if t is not None and t.text:
                    shared_strings.append(t.text)
                else:
                    # handle rich text <r><t>
                    text_parts = [t_el.text for t_el in si.findall('.//main:t', ns) if t_el.text]
                    shared_strings.append(''.join(text_parts))
        
        # 4. Read sheet xml
        sheet_xml = z.read(target_file)
        sheet_root = ET.fromstring(sheet_xml)
        
        rows = []
        for row in sheet_root.findall('main:sheetData/main:row', ns):
            row_idx = row.attrib.get('r')
            row_cells = {}
            for c in row.findall('main:c', ns):
                r_ref = c.attrib.get('r')
                t_type = c.attrib.get('t')
                v_el = c.find('main:v', ns)
                val = v_el.text if v_el is not None else ''
                if t_type == 's' and val.isdigit():
                    val = shared_strings[int(val)]
                row_cells[r_ref] = val
            rows.append((int(row_idx) if row_idx and row_idx.isdigit() else 0, row_cells))
            
        print(f"Total rows in {sheet_name_target}: {len(rows)}")
        for r_num, cells in rows[:40]:
            print(f"Row {r_num:3d}: {cells}")

inspect_xlsx_sheet('DASH KIARACONDONG 24-26.xlsx', 'TARGET')
