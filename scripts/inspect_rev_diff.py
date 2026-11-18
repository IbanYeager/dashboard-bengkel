import zipfile
import xml.etree.ElementTree as ET
import csv
import re

def clean_num(val):
    if val is None or val == "":
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    if not s or s in ['-', '#REF!', '#N/A', '#VALUE!', 'FALSE', 'TRUE']:
        return 0.0
    s = re.sub(r'^(?:Rp\.?|RP\.?|rp\.?)\s*', '', s, flags=re.IGNORECASE).strip()
    if '.' in s and ',' in s:
        if s.rfind('.') < s.rfind(','):
            s = s.replace('.', '').replace(',', '.')
        else:
            s = s.replace(',', '')
    elif '.' in s:
        dots = s.count('.')
        if dots > 1:
            s = s.replace('.', '')
        else:
            parts = s.split('.')
            if len(parts[1]) == 3 and len(parts[0]) <= 3:
                s = s.replace('.', '')
    elif ',' in s:
        commas = s.count(',')
        if commas > 1:
            s = s.replace(',', '')
        else:
            parts = s.split(',')
            if len(parts[1]) == 3 and len(parts[0]) <= 3:
                s = s.replace(',', '')
            else:
                s = s.replace(',', '.')

    s = re.sub(r'[^0-9.-]', '', s)
    try:
        return float(s)
    except:
        return 0.0

# 1. Read local Excel
EXCEL_PATH = r"c:\laragon\www\dashboard_bengkel\DASH KIARACONDONG 24-26.xlsx"
local_pkb_rev = {}
with zipfile.ZipFile(EXCEL_PATH, 'r') as z:
    shared_strings = []
    if 'xl/sharedStrings.xml' in z.namelist():
        with z.open('xl/sharedStrings.xml') as f:
            for event, elem in ET.iterparse(f, events=('end',)):
                if elem.tag.endswith('si'):
                    text = "".join([t.text for t in elem.iter() if t.tag.endswith('t') and t.text])
                    shared_strings.append(text)
                    elem.clear()

    wb_root = ET.fromstring(z.read('xl/workbook.xml'))
    rels_root = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels_root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')}
    sheet_files = {}
    for s in wb_root.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet'):
        sheet_files[s.attrib.get('name').strip().lower()] = 'xl/' + rel_map[s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')].lstrip('/')

    pkb_file = sheet_files['input pkb']
    with z.open(pkb_file) as f:
        for event, elem in ET.iterparse(f, events=('end',)):
            if elem.tag.endswith('row'):
                cols = {}
                for c in elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                    ref = c.attrib.get('r')
                    col = ''.join([ch for ch in ref if ch.isalpha()])
                    t = c.attrib.get('t')
                    v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                    val = ""
                    if v is not None and v.text is not None:
                        val = shared_strings[int(v.text)] if t == 's' else v.text
                    cols[col] = val
                
                pkb = cols.get('K', '').strip()
                thn = cols.get('C', '').strip()
                bln = cols.get('B', '').strip()
                rev = clean_num(cols.get('BF', 0))
                if not rev:
                    rev = clean_num(cols.get('BE', 0))
                if pkb and thn == '2026':
                    local_pkb_rev[pkb] = (bln, rev, cols.get('BF'), cols.get('BE'))
                elem.clear()

print(f"Total 2026 PKBs in local Excel: {len(local_pkb_rev)}")

# 2. Read live CSV
live_pkb_rev = {}
with open(r'data\live_input_pkb.csv', 'r', encoding='utf-8', errors='ignore') as f:
    reader = csv.reader(f)
    next(reader)
    for r in reader:
        if len(r) > 57 and r[2].strip() == '2026':
            pkb = r[10].strip()
            bln = r[1].strip()
            rev = clean_num(r[57])
            if pkb:
                live_pkb_rev[pkb] = (bln, rev, r[57])

print(f"Total 2026 PKBs in live CSV: {len(live_pkb_rev)}")

# Compare September
diff_pkbs = []
for pkb, (b, r_loc, bf, be) in local_pkb_rev.items():
    if b in ['9', '09']:
        if pkb in live_pkb_rev:
            r_live = live_pkb_rev[pkb][1]
            if abs(r_loc - r_live) > 1:
                diff_pkbs.append((pkb, r_loc, r_live, bf, live_pkb_rev[pkb][2]))
        else:
            diff_pkbs.append((pkb, r_loc, 'MISSING IN LIVE', bf, '-'))

print(f"September PKBs with revenue diff: {len(diff_pkbs)}")
for item in diff_pkbs[:10]:
    print(item)
