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

def clean_str(val):
    return str(val).strip() if val is not None else ""

def clean_num(val):
    try:
        return float(val) if val is not None and val != "" else 0.0
    except:
        return 0.0

fpath = 'DASH KIARACONDONG 24-26(1).xlsx'
db_path = 'data/bengkel.db'

print(f"Reading September PKB rows from {fpath} for SQLite...")
with zipfile.ZipFile(fpath, 'r') as z:
    shared_strings = get_shared_strings(z)
    wb_root = ET.fromstring(z.read('xl/workbook.xml'))
    rels_root = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels_root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')}
    sheet_files = {s.attrib.get('name').strip().lower(): 'xl/' + rel_map[s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')].lstrip('/') for s in wb_root.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet')}
    
    pkb_file = sheet_files.get('input pkb')
    rows_to_insert = []
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
                    
                    yr = clean_str(cols.get('C'))
                    m = clean_str(cols.get('BN'))
                    bln = clean_str(cols.get('B'))
                    if yr == '2026' and (m == 'September' or bln in ['09', '9', 'September']):
                        tgl = int(clean_num(cols.get('A')))
                        pkb_no = clean_str(cols.get('K'))
                        vin = clean_str(cols.get('G'))
                        police_no = clean_str(cols.get('J'))
                        cust_name = clean_str(cols.get('Q'))
                        sa = clean_str(cols.get('AQ') or cols.get('Z')).upper()
                        mechanic = clean_str(cols.get('AA'))
                        tipe_kendaraan = clean_str(cols.get('AD'))
                        type_ue = clean_str(cols.get('AR')).upper()
                        type_service = clean_str(cols.get('AS')).upper()
                        arrival = clean_str(cols.get('W'))
                        tcare = clean_str(cols.get('AX')).lower()
                        sbi_so = clean_str(cols.get('DI') or cols.get('AU')).lower()
                        fleet_retail = clean_str(cols.get('AO')).upper()
                        revenue = clean_num(cols.get('BF'))
                        lcgc = clean_str(cols.get('BE'))
                        lookup_job = clean_str(cols.get('H')).upper()
                        type_cust = clean_str(cols.get('AV')).upper()
                        ring_area = clean_str(cols.get('BC')).upper()
                        model_segment = clean_str(cols.get('BD'))
                        ths = clean_str(cols.get('V')).upper()
                        range_rev = clean_str(cols.get('BG'))
                        qty_gr = int(clean_num(cols.get('BH')))
                        qty_sbe = int(clean_num(cols.get('BI')))

                        rows_to_insert.append((
                            tgl, '09', 2026, 'September', 3, pkb_no, vin, police_no,
                            cust_name, sa, mechanic, tipe_kendaraan, type_ue, type_service,
                            arrival, tcare, sbi_so, fleet_retail, revenue, lcgc,
                            lookup_job, type_cust, ring_area, model_segment, ths,
                            range_rev, qty_gr, qty_sbe
                        ))
                elem.clear()

print(f"Inserting {len(rows_to_insert)} September rows into SQLite {db_path}...")
conn = sqlite3.connect(db_path)
cur = conn.cursor()
# Delete any existing September 2026 rows first
cur.execute("DELETE FROM raw_pkb WHERE tahun = 2026 AND (month_name = 'September' OR bulan = '09')")
cur.executemany("""
INSERT INTO raw_pkb 
(tgl, bulan, tahun, month_name, quartal, pkb_no, vin, police_no,
 customer_name, sa, mechanic, tipe_kendaraan, type_ue, type_service,
 arrival_type, tcare_national, sbi_so, fleet_retail, revenue, lcgc,
 lookup_job, type_cust, ring_area, model_segment, ths,
 range_revenue, qty_gr, qty_sbe)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", rows_to_insert)
conn.commit()

cur.execute("SELECT count(*) FROM raw_pkb WHERE tahun = 2026 AND month_name = 'September'")
print(f"Total September 2026 rows in SQLite raw_pkb: {cur.fetchone()[0]}")
conn.close()
print("SQLite sync complete!")
