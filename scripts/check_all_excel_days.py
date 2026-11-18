import zipfile
import xml.etree.ElementTree as ET
import glob

def inspect_file(fpath):
    print("="*50)
    print(f"Checking {fpath}...")
    try:
        with zipfile.ZipFile(fpath, 'r') as z:
            shared_strings = []
            if 'xl/sharedStrings.xml' in z.namelist():
                with z.open('xl/sharedStrings.xml') as f:
                    for event, elem in ET.iterparse(f, events=('end',)):
                        if elem.tag.endswith('si'):
                            shared_strings.append(''.join([t.text for t in elem.iter() if t.tag.endswith('t') and t.text]))
                            elem.clear()
            
            wb = ET.fromstring(z.read('xl/workbook.xml'))
            rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
            rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')}
            sheets = {s.attrib.get('name').strip().lower(): 'xl/' + rel_map[s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')].lstrip('/') for s in wb.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet')}
            
            pkb_file = sheets.get('input pkb')
            if not pkb_file:
                print("No input pkb sheet")
                return

            days = set()
            count = 0
            cpus = 0
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
                            
                            yr = str(cols.get('C', '')).strip()
                            m = str(cols.get('BN', '')).strip()
                            bln = str(cols.get('B', '')).strip()
                            if yr == '2026' and (m == 'September' or bln in ['09', '9', 'September']):
                                count += 1
                                tgl = cols.get('A')
                                if tgl:
                                    try: days.add(int(float(tgl)))
                                    except: pass
                                if str(cols.get('AR', '')).strip().upper() == 'CPUS':
                                    cpus += 1
                        elem.clear()
            print(f"Total Sep 2026 rows: {count}, CPUS: {cpus}, Days: {sorted(list(days))}")
    except Exception as e:
        print("Error:", e)

for f in ['DASH KIARACONDONG 24-26(1).xlsx', 'DASH KIARACONDONG 24-26.xlsx', 'DASH KIARACONDONG 24-26.backup.xlsx', 'DASH KIARACONDONG 24-26.before_sep30_sync.xlsx']:
    inspect_file(f)
