import zipfile
import xml.etree.ElementTree as ET
import glob

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

def check_excel_file(fpath):
    print(f"\n==========================================")
    print(f"Checking {fpath}...")
    try:
        with zipfile.ZipFile(fpath, 'r') as z:
            shared_strings = get_shared_strings(z)
            wb_root = ET.fromstring(z.read('xl/workbook.xml'))
            rels_root = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
            rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels_root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')}
            sheet_files = {s.attrib.get('name').strip().lower(): 'xl/' + rel_map[s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')].lstrip('/') for s in wb_root.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet')}
            
            pkb_file = sheet_files.get('input pkb')
            if not pkb_file:
                print("No INPUT PKB sheet!")
                return
            
            # Let's read header row (r=1)
            headers = {}
            with z.open(pkb_file) as sf:
                for event, elem in ET.iterparse(sf, events=('end',)):
                    if elem.tag.endswith('row'):
                        r = int(elem.attrib.get('r'))
                        if r == 1:
                            for c in elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                                ref = c.attrib.get('r')
                                col = ''.join([ch for ch in ref if ch.isalpha()])
                                t = c.attrib.get('t')
                                v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                                val = ''
                                if v is not None and v.text:
                                    val = shared_strings[int(v.text)] if t == 's' and int(v.text) < len(shared_strings) else v.text
                                headers[col] = val
                            break
                        elem.clear()
            print("Headers in INPUT PKB:", {k: headers[k] for k in list(headers.keys())[:15]})
            
            # Check row count for September 2026
            sept_rows = []
            ue_counts = {}
            col_b_vals = set()
            col_c_vals = set()
            col_bn_vals = set()

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
                            
                            # Let's track date/year/month
                            if yr == '2026' or '2026' in str(cols.get('A', '')) or '2026' in str(cols.get('B', '')):
                                # check if september
                                if m.lower() == 'september' or bln in ['09', '9', 'September', 'september'] or 'sep' in m.lower():
                                    sept_rows.append(cols)
                                    ue = str(cols.get('AR', '')).strip().upper()
                                    ue_counts[ue] = ue_counts.get(ue, 0) + 1
                        elem.clear()
            
            print(f"Total September 2026 rows found: {len(sept_rows)}")
            print(f"UE column (AR) counts: {ue_counts}")
    except Exception as e:
        print("Error checking file:", e)

for f in ['DASH KIARACONDONG 24-26.xlsx', 'DASH KIARACONDONG 24-26(1).xlsx']:
    check_excel_file(f)
