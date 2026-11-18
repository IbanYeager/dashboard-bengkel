import zipfile
import xml.etree.ElementTree as ET

with zipfile.ZipFile('DASH KIARACONDONG 24-26(1).xlsx', 'r') as z:
    # get shared strings
    shared_strings = []
    if 'xl/sharedStrings.xml' in z.namelist():
        with z.open('xl/sharedStrings.xml') as f:
            for event, elem in ET.iterparse(f, events=('end',)):
                if elem.tag.endswith('si'):
                    text = ''.join([t.text for t in elem.iter() if t.tag.endswith('t') and t.text])
                    shared_strings.append(text)
                    elem.clear()
    
    wb_root = ET.fromstring(z.read('xl/workbook.xml'))
    rels_root = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels_root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')}
    sheet_files = {s.attrib.get('name').strip().lower(): 'xl/' + rel_map[s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')].lstrip('/') for s in wb_root.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet')}
    
    pkb_file = sheet_files.get('input pkb')
    print("PKB file in Excel:", pkb_file)
    
    sept_rows = []
    with z.open(pkb_file) as sf:
        for event, elem in ET.iterparse(sf, events=('end',)):
            if elem.tag.endswith('row'):
                r = int(elem.attrib.get('r'))
                if r > 1:
                    cols = {}
                    for c in elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                        ref = c.attrib.get('r')
                        col = ''.join([ch for ch in ref if ch.isalpha()])
                        t = c.attrib.get('t')
                        v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                        val = ''
                        if v is not None and v.text:
                            val = shared_strings[int(v.text)] if t == 's' and int(v.text) < len(shared_strings) else v.text
                        cols[col] = val
                    
                    yr = cols.get('C', '')
                    m = cols.get('BN', '')
                    bln = cols.get('B', '')
                    if yr == '2026' and (m == 'September' or bln in ['09', '9', 'September']):
                        sept_rows.append((r, cols))
                elem.clear()

    print(f"Total September rows in Excel: {len(sept_rows)}")
    tot_rev = sum(float(c.get('BF', 0) or 0) for r, c in sept_rows)
    print(f"Total Revenue in Excel for September: Rp {tot_rev:,.0f}")
    sample = sept_rows[0][1]
    print("Sample Excel row:")
    print(f"  PKB: {sample.get('K')}, SA: {sample.get('AQ')}, UE: {sample.get('AR')}, Rev BF: {sample.get('BF')}")
