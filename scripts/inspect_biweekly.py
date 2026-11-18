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

with zipfile.ZipFile('DASH KIARACONDONG 24-26.xlsx', 'r') as z:
    wb_root = ET.fromstring(z.read('xl/workbook.xml'))
    rels_root = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels_root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')}
    
    sheet_files = {}
    for s in wb_root.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet'):
        sheet_files[s.attrib.get('name')] = 'xl/' + rel_map[s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')].lstrip('/')
    
    shared_strings = get_shared_strings(z)
    
    with z.open(sheet_files.get('BIWEEKLY')) as sf:
        for event, elem in ET.iterparse(sf, events=('end',)):
            if elem.tag.endswith('row'):
                r = int(elem.attrib.get('r'))
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
                    row_cells[col] = (val, f_txt)
                
                # Check top control cells
                if r in [1, 2, 3, 4, 5]:
                    print(f"Row {r}: {[(k, row_cells[k][0], row_cells[k][1]) for k in row_cells if k in ['A','B','C','D','E','F','G']]}")
                
                # Check target ranges for the charts
                # TYPE CUST: AE20:AF23
                # CPUS: AL21, AM19:AP19, AM21:AP21
                # KOMPOSISI UE: AM25:AQ25, AM26:AQ26
                # TYPE SBE: AE35:AP37
                # CUST AREA: AE39:AF43
                # CAR SEGMENT: AO63:AW66
                if (19 <= r <= 28) or (34 <= r <= 44) or (62 <= r <= 67):
                    cols_to_show = [k for k in row_cells if k >= 'AE' and k <= 'AZ']
                    if cols_to_show:
                        print(f"Row {r}: {[(k, row_cells[k][0], row_cells[k][1]) for k in cols_to_show]}")
                elem.clear()
