import zipfile
import xml.etree.ElementTree as ET
import re

TEMP_FILE = r"c:\laragon\www\dashboard_bengkel\scripts\live_download_temp.xlsx"

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
    return "" if val is None else str(val).strip()

def clean_num(val):
    if val is None or val == "": return 0.0
    if isinstance(val, (int, float)): return float(val)
    s = str(val).strip()
    if not s or s in ['-', '#REF!', '#N/A', '#VALUE!', 'FALSE', 'TRUE']: return 0.0
    s = re.sub(r'^(?:Rp\.?|RP\.?|rp\.?)\s*', '', s, flags=re.IGNORECASE).strip()
    if '.' in s and ',' in s:
        if s.rfind('.') < s.rfind(','): s = s.replace('.', '').replace(',', '.')
        else: s = s.replace(',', '')
    elif '.' in s:
        dots = s.count('.')
        if dots > 1: s = s.replace('.', '')
        else:
            parts = s.split('.')
            if len(parts[1]) == 3 and len(parts[0]) <= 3: s = s.replace('.', '')
    elif ',' in s:
        commas = s.count(',')
        if commas > 1: s = s.replace(',', '')
        else:
            parts = s.split(',')
            if len(parts[1]) == 3 and len(parts[0]) <= 3: s = s.replace(',', '')
            else: s = s.replace(',', '.')
    s = re.sub(r'[^0-9.-]', '', s)
    try: return float(s)
    except: return 0.0

def resolve_month_name(bulan_raw, m_name_col=''):
    if m_name_col and str(m_name_col).strip():
        val = str(m_name_col).strip()
        for m in MONTH_NAMES:
            if m.lower() == val.lower():
                return m
    if not bulan_raw: return ""
    b_str = str(bulan_raw).strip().lower()
    if b_str in MONTH_MAP: return MONTH_MAP[b_str]
    try:
        b_num = int(float(b_str))
        if 1 <= b_num <= 12: return MONTH_NAMES[b_num - 1]
    except: pass
    if len(b_str) >= 3 and b_str[:3] in MONTH_MAP: return MONTH_MAP[b_str[:3]]
    return ""

with zipfile.ZipFile(TEMP_FILE, 'r') as z:
    shared_strings = []
    with z.open('xl/sharedStrings.xml') as f:
        for event, elem in ET.iterparse(f, events=('end',)):
            if elem.tag.endswith('si'):
                shared_strings.append("".join([t.text for t in elem.iter() if t.tag.endswith('t') and t.text]))
                elem.clear()

    wb_root = ET.fromstring(z.read('xl/workbook.xml'))
    rels_root = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels_root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')}
    sheet_files = {s.attrib.get('name').strip().lower(): 'xl/' + rel_map[s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')].lstrip('/') for s in wb_root.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet')}

    # Check TARGET for October 2026
    target_file = sheet_files.get('target')
    print("Checking TARGET sheet...")
    target_months = []
    with z.open(target_file) as f:
        for event, elem in ET.iterparse(f, events=('end',)):
            if elem.tag.endswith('row'):
                if elem.attrib.get('r') == '1':
                    for c in elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                        v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                        t = c.attrib.get('t')
                        val = shared_strings[int(v.text)] if (t == 's' and v is not None) else (v.text if v is not None else "")
                        if '2026' in str(val): target_months.append(val)
                elem.clear()
    print("2026 Targets found:", target_months)

    # Check PKB October 2026 rows
    pkb_file = sheet_files.get('input pkb')
    oct_pkb_count = 0
    oct_revenue = 0.0
    oct_sa_counts = {}
    with z.open(pkb_file) as f:
        for event, elem in ET.iterparse(f, events=('end',)):
            if elem.tag.endswith('row'):
                if elem.attrib.get('r') != '1':
                    cols = {}
                    for c in elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                        ref = c.attrib.get('r')
                        col = ''.join([ch for ch in ref if ch.isalpha()])
                        t = c.attrib.get('t')
                        v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                        val = shared_strings[int(v.text)] if (t == 's' and v is not None) else (v.text if v is not None else "")
                        cols[col] = val

                    tgl = int(clean_num(cols.get('A')))
                    bulan = clean_str(cols.get('B'))
                    tahun = int(clean_num(cols.get('C')))
                    m_name = resolve_month_name(bulan, cols.get('BN'))
                    if tahun == 2026 and m_name == 'October':
                        oct_pkb_count += 1
                        rev = clean_num(cols.get('BF'))
                        oct_revenue += rev
                        sa = clean_str(cols.get('AQ')).upper() or clean_str(cols.get('Z')).upper()
                        oct_sa_counts[sa] = oct_sa_counts.get(sa, 0) + 1
                elem.clear()

    print(f"\nOctober 2026 PKB extracted: {oct_pkb_count} rows, Total Revenue: Rp {oct_revenue:,.0f}")
    print(f"October 2026 SA counts: {oct_sa_counts}")
