import urllib.request
import time
import zipfile
import xml.etree.ElementTree as ET

SHEET_ID = '1b60d-JO50LU4KyywuULokmDIU7z3Ts_1'
EXPORT_XLSX_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"
TEMP_FILE = r"c:\laragon\www\dashboard_bengkel\scripts\live_download_temp.xlsx"

print("Downloading live spreadsheet...")
req = urllib.request.Request(
    EXPORT_XLSX_URL,
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
)

t0 = time.time()
with urllib.request.urlopen(req, timeout=120) as resp:
    data = resp.read()
    print(f"Downloaded {len(data):,} bytes in {time.time()-t0:.1f}s")
    with open(TEMP_FILE, 'wb') as f:
        f.write(data)

print("Inspecting downloaded file...")
with zipfile.ZipFile(TEMP_FILE, 'r') as z:
    wb_root = ET.fromstring(z.read('xl/workbook.xml'))
    rels_root = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels_root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')}
    sheet_files = {}
    for s in wb_root.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet'):
        s_name = s.attrib.get('name').strip()
        rId = s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        sheet_files[s_name.lower()] = 'xl/' + rel_map[rId].lstrip('/')
    print("Sheets in live download:", sheet_files)

    # Load shared strings
    shared_strings = []
    with z.open('xl/sharedStrings.xml') as f:
        for event, elem in ET.iterparse(f, events=('end',)):
            if elem.tag.endswith('si'):
                text = "".join([t.text for t in elem.iter() if t.tag.endswith('t') and t.text])
                shared_strings.append(text)
                elem.clear()
    print(f"Shared strings count: {len(shared_strings)}")

    # Check Daftar List SO
    so_file = sheet_files.get('daftar list so')
    tire_rows = []
    oct_rows_so = []
    max_so = 0
    with z.open(so_file) as f:
        for event, elem in ET.iterparse(f, events=('end',)):
            if elem.tag.endswith('row'):
                r_idx = int(elem.attrib.get('r', 0))
                max_so = max(max_so, r_idx)
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
                
                # Check for TIRE in Sep 2026 or DIDIN
                cat = cols.get('L', '')
                sa = cols.get('F', '')
                thn = cols.get('D', '')
                bln = cols.get('C', '')
                if 'TIRE' in str(cat).upper() and 'DIDIN' in str(sa).upper():
                    tire_rows.append((r_idx, cols))
                if ('10' in str(bln) or 'okt' in str(cols.get('M', '')).lower()) and '2026' in str(thn):
                    oct_rows_so.append((r_idx, cols))
                elem.clear()

    print(f"Max SO row: {max_so}")
    print(f"DIDIN TIRE rows found: {len(tire_rows)}")
    for r_idx, c in tire_rows:
        print(f"Row {r_idx}: {c}")

    print(f"October 2026 SO rows found: {len(oct_rows_so)}")
    if oct_rows_so:
        print("Sample Oct SO row:", oct_rows_so[0])

    # Check INPUT PKB for October 2026
    pkb_file = sheet_files.get('input pkb')
    oct_rows_pkb = []
    max_pkb = 0
    with z.open(pkb_file) as f:
        for event, elem in ET.iterparse(f, events=('end',)):
            if elem.tag.endswith('row'):
                r_idx = int(elem.attrib.get('r', 0))
                max_pkb = max(max_pkb, r_idx)
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
                
                bln = cols.get('B', '')
                thn = cols.get('C', '')
                if ('10' in str(bln) or 'okt' in str(cols.get('BN', '')).lower() or 'oct' in str(cols.get('BN', '')).lower()) and '2026' in str(thn):
                    oct_rows_pkb.append((r_idx, cols))
                elem.clear()

    print(f"Max PKB row: {max_pkb}")
    print(f"October 2026 PKB rows found: {len(oct_rows_pkb)}")
    if oct_rows_pkb:
        print("Sample Oct PKB row:", oct_rows_pkb[0])
