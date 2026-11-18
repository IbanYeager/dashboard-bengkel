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

fpath = 'DASH KIARACONDONG 24-26(1).xlsx'
print(f"Opening {fpath}...")
with zipfile.ZipFile(fpath, 'r') as z:
    shared_strings = get_shared_strings(z)
    print(f"Loaded {len(shared_strings)} shared strings.")
    wb_root = ET.fromstring(z.read('xl/workbook.xml'))
    rels_root = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels_root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')}
    sheet_files = {s.attrib.get('name'): 'xl/' + rel_map[s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')].lstrip('/') for s in wb_root.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet')}
    
    with z.open(sheet_files['INPUT PKB']) as sf:
        sept_rows = []
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
                    if cols.get('C') == '2026' and (cols.get('BN') == 'September' or cols.get('B') in ['09', '9', 'September']):
                        sept_rows.append(cols)
                elem.clear()

        print(f"Total September rows found: {len(sept_rows)}")
        if sept_rows:
            sample = sept_rows[0]
            print("Sample September row:")
            for k in ['A', 'B', 'C', 'G', 'J', 'K', 'M', 'Q', 'AQ', 'AR', 'AS', 'AX', 'BF', 'BN']:
                print(f"  Col {k}: {sample.get(k)}")

            total_rev = sum(float(r.get('BF', 0) or 0) for r in sept_rows)
            ue_count = len(sept_rows)
            cpus_count = sum(1 for r in sept_rows if str(r.get('AR', '')).upper() == 'CPUS')
            tcare_count = sum(1 for r in sept_rows if 'tcare' in str(r.get('AX', '')).lower() or 't-care' in str(r.get('AX', '')).lower())
            sbe_count = sum(1 for r in sept_rows if 'SBE' in str(r.get('AS', '')).upper())

            print("\nSeptember 2026 Aggregates:")
            print(f"  UE Total: {ue_count}")
            print(f"  CPUS: {cpus_count}")
            print(f"  Revenue Total: Rp {total_rev:,.0f}")
            print(f"  T-Care Count: {tcare_count}")
            print(f"  SBE Count: {sbe_count}")
            if sbe_count > 0:
                print(f"  T-Care / SBE Rate: {tcare_count / sbe_count * 100:.1f}%")
