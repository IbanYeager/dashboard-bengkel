import zipfile
import xml.etree.ElementTree as ET

def get_shared_strings(z):
    shared_strings = []
    if 'xl/sharedStrings.xml' in z.namelist():
        with z.open('xl/sharedStrings.xml') as f:
            for event, elem in ET.iterparse(f, events=('end',)):
                if elem.tag.endswith('si'):
                    text = ''.join([t.text for t in elem.iter() if t.tag.endswith('t') and t.text])
                    shared_strings.append(text)
                    elem.clear()
    return shared_strings

def dump_sheet_range(wb_name, sheet_name, max_r=50):
    print(f"\n==========================================")
    print(f"FILE: {wb_name}, SHEET: {sheet_name}")
    print(f"==========================================")
    with zipfile.ZipFile(wb_name, 'r') as z:
        wb_root = ET.fromstring(z.read('xl/workbook.xml'))
        rels_root = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels_root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')}
        sheet_files = {s.attrib.get('name'): 'xl/' + rel_map[s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')].lstrip('/') for s in wb_root.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet')}
        
        shared_strings = get_shared_strings(z)
        sheet_file = sheet_files.get(sheet_name)
        if not sheet_file:
            print("Sheet not found!")
            return

        with z.open(sheet_file) as sf:
            for event, elem in ET.iterparse(sf, events=('end',)):
                if elem.tag.endswith('row'):
                    r = int(elem.attrib.get('r'))
                    if r <= max_r:
                        row_cells = {}
                        for c in elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                            ref = c.attrib.get('r')
                            col = ''.join([ch for ch in ref if ch.isalpha()])
                            t = c.attrib.get('t')
                            v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                            f = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}f')
                            val = ""
                            if v is not None and v.text:
                                val = shared_strings[int(v.text)] if t == 's' and int(v.text) < len(shared_strings) else v.text
                            f_txt = f.text if f is not None and f.text else ""
                            if val != "" or f_txt != "":
                                row_cells[col] = (val, f_txt)
                        if row_cells:
                            print(f"Row {r:2d}: " + " | ".join([f"{col}: '{row_cells[col][0]}'" + (f" [f={row_cells[col][1]}]" if row_cells[col][1] else "") for col in sorted(row_cells.keys())[:12]]))
                    elem.clear()

dump_sheet_range('Dashboard AFS Kiaracondong-start 2024.xlsx', 'DASHBOARD CPUS', 30)
dump_sheet_range('Dashboard AFS Kiaracondong-start 2024.xlsx', 'DASHBOARD', 30)
dump_sheet_range('Dashboard AFS Kiaracondong-start 2024.xlsx', 'Bisnis perf trend Smt 1', 30)
