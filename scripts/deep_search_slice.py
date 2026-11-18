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
    sheet_files = {s.attrib.get('name'): 'xl/' + rel_map[s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')].lstrip('/') for s in wb_root.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet')}
    
    shared_strings = get_shared_strings(z)
    
    # We want to check across all rows in INPUT PKB
    # Col A: TGL, Col B: BULAN, Col C: TAHUN, Col BN: MONTH, Col AQ: SA, Col BC: Ring Area, Col AV: Type Cust
    # Col AR: TYPE UE, Col AS: Type Service, Col AO: Fleet/Retail, Col H: LOOKUP JOB, Col BD: Model Segment
    
    rows = []
    with z.open(sheet_files['INPUT PKB']) as sf:
        for event, elem in ET.iterparse(sf, events=('end',)):
            if elem.tag.endswith('row'):
                r = elem.attrib.get('r')
                if r != '1':
                    c_dict = {}
                    for c in elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                        ref = c.attrib.get('r')
                        col = ''.join([ch for ch in ref if ch.isalpha()])
                        t = c.attrib.get('t')
                        v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                        val = ""
                        if v is not None and v.text:
                            val = shared_strings[int(v.text)] if t == 's' and int(v.text) < len(shared_strings) else v.text
                        c_dict[col] = val
                    
                    tgl_str = c_dict.get('A', '')
                    try:
                        tgl = int(float(tgl_str))
                    except:
                        tgl = 0
                    thn = c_dict.get('C', '').strip()
                    m_name = c_dict.get('BN', '').strip()
                    sa = c_dict.get('AQ', '').strip().upper()
                    ring = c_dict.get('BC', '').strip().upper()
                    cust = c_dict.get('AV', '').strip().upper()
                    type_ue = c_dict.get('AR', '').strip().upper()
                    service = c_dict.get('AS', '').strip().upper()
                    fleet = c_dict.get('AO', '').strip().upper()
                    sbe_type = c_dict.get('H', '').strip().upper()
                    model_seg = c_dict.get('BD', '').strip()
                    
                    rows.append({
                        'tgl': tgl, 'thn': thn, 'm': m_name, 'sa': sa,
                        'ring': ring, 'cust': cust, 'type_ue': type_ue,
                        'service': service, 'fleet': fleet, 'sbe': sbe_type,
                        'seg': model_seg
                    })
                elem.clear()

print(f"Total rows: {len(rows)}")

# Test various slices
for yr in ['2024', '2025', '2026']:
    for m in ['January','February','March','April','May','June','July','August','September','October','November','December']:
        # Full month
        m_rows = [r for r in rows if r['thn'] == yr and r['m'] == m]
        if not m_rows: continue
        
        # Test full, 1-15, 16-31
        slices = [
            ('Full', m_rows),
            ('Day 1-15', [r for r in m_rows if 1 <= r['tgl'] <= 15]),
            ('Day 1-10', [r for r in m_rows if 1 <= r['tgl'] <= 10]),
            ('Day 1-11', [r for r in m_rows if 1 <= r['tgl'] <= 11]),
            ('Day 1-12', [r for r in m_rows if 1 <= r['tgl'] <= 12]),
            ('Day 1-13', [r for r in m_rows if 1 <= r['tgl'] <= 13]),
            ('Day 1-14', [r for r in m_rows if 1 <= r['tgl'] <= 14]),
            ('Day 16-31', [r for r in m_rows if r['tgl'] >= 16])
        ]
        
        # Also test by SA
        for sl_name, sl_rows in slices:
            # Check Ring 1 in sl_rows
            r1 = sum(1 for r in sl_rows if 'RING 1' in r['ring'])
            r2 = sum(1 for r in sl_rows if 'RING 2' in r['ring'])
            r3 = sum(1 for r in sl_rows if 'RING 3' in r['ring'])
            out_area = sum(1 for r in sl_rows if 'OUT OF' in r['ring'])
            if r1 == 80:
                print(f"FOUND MATCH for RING 1=80! Year={yr}, Month={m}, Slice={sl_name}: R1={r1}, R2={r2}, R3={r3}, Out={out_area}")
            
            # Check SA filtered
            for sa_name in ['DIDIN', 'FICKY', 'ACEP']:
                sa_rows = [r for r in sl_rows if r['sa'] == sa_name]
                r1_sa = sum(1 for r in sa_rows if 'RING 1' in r['ring'])
                r2_sa = sum(1 for r in sa_rows if 'RING 2' in r['ring'])
                r3_sa = sum(1 for r in sa_rows if 'RING 3' in r['ring'])
                out_sa = sum(1 for r in sa_rows if 'OUT OF' in r['ring'])
                if r1_sa == 80:
                    print(f"FOUND MATCH for SA {sa_name}! Year={yr}, Month={m}, Slice={sl_name}: R1={r1_sa}, R2={r2_sa}, R3={r3_sa}, Out={out_sa}")
