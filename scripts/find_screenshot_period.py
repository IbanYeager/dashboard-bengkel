import sqlite3
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
    
    # We want to check across all rows in INPUT PKB grouped by (tahun, month)
    # Count:
    # 1. Ring Area = RING 1, RING 2, RING 3, OUT OF AREA
    # 2. Type Cust = AKTIF, PASIF, NEW CUST
    # 3. CPUS = RETAIL, FLEET, SUDECO, TPI
    # 4. KOMPOSISI UE = SBE, GR, SBI, TWC
    # 5. CAR SEGMENT COMP
    
    records = []
    with z.open(sheet_files['INPUT PKB']) as sf:
        for event, elem in ET.iterparse(sf, events=('end',)):
            if elem.tag.endswith('row'):
                r = elem.attrib.get('r')
                if r != '1':
                    row_data = {}
                    for c in elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                        ref = c.attrib.get('r')
                        col = ''.join([ch for ch in ref if ch.isalpha()])
                        t = c.attrib.get('t')
                        v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                        val = ""
                        if v is not None and v.text:
                            val = shared_strings[int(v.text)] if t == 's' and int(v.text) < len(shared_strings) else v.text
                        row_data[col] = val
                    thn = row_data.get('C', '').strip()
                    m_name = row_data.get('BN', '').strip()
                    ring = row_data.get('BC', '').strip()
                    type_cust = row_data.get('AV', '').strip()
                    type_ue = row_data.get('AR', '').strip().upper()
                    fleet_ret = row_data.get('AO', '').strip().upper()
                    records.append((thn, m_name, ring, type_cust, type_ue, fleet_ret))
                elem.clear()

print(f"Total PKB records loaded: {len(records)}")

# Group by (thn, m_name)
from collections import defaultdict
grouped = defaultdict(list)
for r in records:
    grouped[(r[0], r[1])].append(r)

for (thn, m_name), rows in sorted(grouped.items()):
    ring_counts = defaultdict(int)
    cust_counts = defaultdict(int)
    for r in rows:
        ring_counts[r[2]] += 1
        cust_counts[r[3]] += 1
    
    # Check if this matches RING 1=80 or AKTIF=252 or similar
    if ring_counts['RING 1'] == 80 or cust_counts['AKTIF'] == 252:
        print(f"MATCH FOUND! Year={thn}, Month={m_name}")
        print(f"  Ring counts: {dict(ring_counts)}")
        print(f"  Cust counts: {dict(cust_counts)}")
    else:
        # Check if CPUS filtered
        ring_cpus = defaultdict(int)
        cust_cpus = defaultdict(int)
        for r in rows:
            if r[4] == 'CPUS':
                ring_cpus[r[2]] += 1
                cust_cpus[r[3]] += 1
        if ring_cpus['RING 1'] == 80 or cust_cpus['AKTIF'] == 252:
            print(f"MATCH FOUND IN CPUS! Year={thn}, Month={m_name}")
            print(f"  Ring CPUS: {dict(ring_cpus)}")
            print(f"  Cust CPUS: {dict(cust_cpus)}")
