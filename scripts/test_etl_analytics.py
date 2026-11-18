import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
import json

EXCEL_PATH = r"c:\laragon\www\dashboard_bengkel\DASH KIARACONDONG 24-26.xlsx"

MONTH_NAMES = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]

MONTH_MAP = {
    '01': 'January', '1': 'January', 'jan': 'January', 'january': 'January',
    '02': 'February', '2': 'February', 'feb': 'February', 'february': 'February',
    '03': 'March', '3': 'March', 'mar': 'March', 'march': 'March',
    '04': 'April', '4': 'April', 'apr': 'April', 'april': 'April',
    '05': 'May', '5': 'May', 'mei': 'May',
    '06': 'June', '6': 'June', 'jun': 'June', 'june': 'June',
    '07': 'July', '7': 'July', 'jul': 'July', 'july': 'July',
    '08': 'August', '8': 'August', 'agu': 'August', 'aug': 'August', 'august': 'August',
    '09': 'September', '9': 'September', 'sep': 'September', 'september': 'September',
    '10': 'October', 'okt': 'October', 'oct': 'October', 'october': 'October',
    '11': 'November', 'nov': 'November', 'november': 'November',
    '12': 'December', 'des': 'December', 'dec': 'December', 'december': 'December'
}

def clean_str(val):
    if val is None: return ""
    return str(val).strip()

def clean_num(val):
    if val is None or val == "": return 0.0
    try: return float(val)
    except: return 0.0

with zipfile.ZipFile(EXCEL_PATH, 'r') as z:
    wb_root = ET.fromstring(z.read('xl/workbook.xml'))
    rels_root = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels_root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')}
    sheet_files = {s.attrib.get('name').lower(): 'xl/' + rel_map[s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')].lstrip('/') for s in wb_root.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet')}
    
    shared_strings = []
    if 'xl/sharedStrings.xml' in z.namelist():
        with z.open('xl/sharedStrings.xml') as f:
            for event, elem in ET.iterparse(f, events=('end',)):
                if elem.tag.endswith('si'):
                    text = "".join([t.text for t in elem.iter() if t.tag.endswith('t') and t.text])
                    shared_strings.append(text)
                    elem.clear()

    # Parse TARGET sheet row 21-22 for SBI CPUS
    sbi_cpus_map = {} # (year, month_name) -> sbi_cpus
    target_sheet = sheet_files.get('target')
    if target_sheet:
        col_info = {}
        row22_data = {}
        with z.open(target_sheet) as f:
            for event, elem in ET.iterparse(f, events=('end',)):
                if elem.tag.endswith('row'):
                    r_idx = int(elem.attrib.get('r', 0))
                    if r_idx in [1, 22]:
                        r_data = {}
                        for c in elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                            ref = c.attrib.get('r')
                            col = ''.join([ch for ch in ref if ch.isalpha()])
                            t = c.attrib.get('t')
                            v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                            val = ""
                            if v is not None and v.text is not None:
                                val = shared_strings[int(v.text)] if t == 's' else v.text
                            r_data[col] = val
                        if r_idx == 1:
                            for col, val in r_data.items():
                                val_clean = val.strip()
                                for m_name in MONTH_NAMES:
                                    if val_clean.startswith(m_name):
                                        yr_str = val_clean[len(m_name):]
                                        if yr_str.isdigit():
                                            col_info[col] = (int(yr_str), m_name)
                                        break
                        elif r_idx == 22:
                            row22_data = r_data
                    elem.clear()
        for col, (yr, m_name) in col_info.items():
            sbi_val = clean_num(row22_data.get(col, 0))
            sbi_cpus_map[(yr, m_name)] = int(sbi_val)
    
    print("Loaded SBI CPUS map for 2026:", {k[1]: v for k, v in sbi_cpus_map.items() if k[0] == 2026})

    # Test BIWEEKLY July 2026 comparison from INPUT PKB
    pkb_sheet = sheet_files.get('input pkb')
    jul26_rows = []
    with z.open(pkb_sheet) as f:
        for event, elem in ET.iterparse(f, events=('end',)):
            if elem.tag.endswith('row'):
                r_idx = elem.attrib.get('r')
                if r_idx != '1':
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
                    
                    thn = int(clean_num(cols.get('C')))
                    bln = clean_str(cols.get('BN'))
                    if thn == 2026 and bln == 'July':
                        jul26_rows.append(cols)
                elem.clear()

print(f"Total July 2026 rows in INPUT PKB: {len(jul26_rows)}")

# Check CUST AREA in July 2026
ring_counts = Counter([clean_str(r.get('BC')).upper() for r in jul26_rows])
print("CUST AREA July 2026:", dict(ring_counts))

# Check TYPE CUST in July 2026
cust_counts = Counter([clean_str(r.get('AV')).upper() for r in jul26_rows])
print("TYPE CUST July 2026:", dict(cust_counts))

# Check CPUS in July 2026
cpus_rows = [r for r in jul26_rows if clean_str(r.get('AR')).upper() == 'CPUS']
fleet_counts = Counter([clean_str(r.get('AO')).upper() for r in cpus_rows])
print("CPUS Fleet/Retail July 2026 (Raw):", dict(fleet_counts))
print("CPUS + SBI 73 to Retail:", fleet_counts['RETAIL'] + sbi_cpus_map.get((2026, 'July'), 0))

# Check KOMPOSISI UE July 2026
srv_counts = Counter([clean_str(r.get('AS')).upper() for r in jul26_rows])
print("KOMPOSISI UE July 2026:", dict(srv_counts))

# Check TYPE SBE July 2026
sbe_rows = [r for r in jul26_rows if clean_str(r.get('AS')).upper() == 'SBE']
sbe_jobs = Counter([clean_str(r.get('H')).upper() for r in sbe_rows])
print("TYPE SBE July 2026 jobs:", dict(sbe_jobs))
