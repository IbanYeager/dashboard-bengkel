import zipfile
import xml.etree.ElementTree as ET
import os

TEMP_FILE = r"c:\laragon\www\dashboard_bengkel\scripts\live_download_temp.xlsx"

if not os.path.exists(TEMP_FILE):
    print("Temp file does not exist yet.")
    exit(0)

print(f"Opening {TEMP_FILE} (size: {os.path.getsize(TEMP_FILE):,} bytes)...")

with zipfile.ZipFile(TEMP_FILE, 'r') as z:
    wb_root = ET.fromstring(z.read('xl/workbook.xml'))
    rels_root = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels_root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')}
    sheet_files = {}
    for s in wb_root.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet'):
        s_name = s.attrib.get('name').strip()
        rId = s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        sheet_files[s_name.lower()] = 'xl/' + rel_map[rId].lstrip('/')
    print("Sheets:", sheet_files)

    print("Loading shared strings...")
    shared_strings = []
    with z.open('xl/sharedStrings.xml') as f:
        for event, elem in ET.iterparse(f, events=('end',)):
            if elem.tag.endswith('si'):
                text = "".join([t.text for t in elem.iter() if t.tag.endswith('t') and t.text])
                shared_strings.append(text)
                elem.clear()
    print(f"Loaded {len(shared_strings)} shared strings.")

    # 1. Check Daftar List SO
    so_file = sheet_files.get('daftar list so')
    print("\nScanning Daftar List SO...")
    tire_didin_sep = []
    oct_so = []
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

                sa = str(cols.get('F', '')).strip().upper()
                cross = str(cols.get('L', '')).strip().upper()
                bln = str(cols.get('C', '')).strip()
                thn = str(cols.get('D', '')).strip()
                m_name = str(cols.get('M', '')).strip()
                desc = str(cols.get('S', '')).strip()

                if 'DIDIN' in sa and ('TIRE' in cross or 'TIRE' in desc.upper()):
                    tire_didin_sep.append((r_idx, cols))

                # Check Oct 2026
                if ('10' in bln or 'okt' in m_name.lower() or 'oct' in m_name.lower()) and '2026' in thn:
                    oct_so.append((r_idx, cols))

                elem.clear()

    print(f"Max row in Daftar List SO: {max_so}")
    print(f"Didin TIRE rows found in SO: {len(tire_didin_sep)}")
    for r_idx, c in tire_didin_sep:
        print(f"  Row {r_idx}: Tgl={c.get('B')} Bln={c.get('C')} Thn={c.get('D')} SA={c.get('F')} RevPKB={c.get('G')} Srv={c.get('H')} Cross={c.get('L')} Desc={c.get('S')} AD={c.get('AD')} AH={c.get('AH')} AO={c.get('AO')} AR={c.get('AR')}")

    print(f"October 2026 rows found in SO: {len(oct_so)}")
    if oct_so:
        print(f"  First Oct SO: {oct_so[0]}")
        print(f"  Last Oct SO: {oct_so[-1]}")

    # 2. Check INPUT PKB
    pkb_file = sheet_files.get('input pkb')
    print("\nScanning INPUT PKB...")
    oct_pkb = []
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

                bln = str(cols.get('B', '')).strip()
                thn = str(cols.get('C', '')).strip()
                m_col = str(cols.get('BN', '')).strip()

                if ('10' in bln or 'okt' in m_col.lower() or 'oct' in m_col.lower()) and '2026' in thn:
                    oct_pkb.append((r_idx, cols))

                elem.clear()

    print(f"Max row in INPUT PKB: {max_pkb}")
    print(f"October 2026 rows found in INPUT PKB: {len(oct_pkb)}")
    if oct_pkb:
        print(f"  First Oct PKB: Row {oct_pkb[0][0]}: Tgl={oct_pkb[0][1].get('A')} Bln={oct_pkb[0][1].get('B')} Thn={oct_pkb[0][1].get('C')} SA={oct_pkb[0][1].get('AQ') or oct_pkb[0][1].get('Z')} Rev={oct_pkb[0][1].get('BF')} PKB={oct_pkb[0][1].get('K')}")
        print(f"  Last Oct PKB: Row {oct_pkb[-1][0]}: Tgl={oct_pkb[-1][1].get('A')} Bln={oct_pkb[-1][1].get('B')} Thn={oct_pkb[-1][1].get('C')} SA={oct_pkb[-1][1].get('AQ') or oct_pkb[-1][1].get('Z')} Rev={oct_pkb[-1][1].get('BF')} PKB={oct_pkb[-1][1].get('K')}")
