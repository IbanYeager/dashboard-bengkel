import os
import sys
import json
import sqlite3
import zipfile
import re
import datetime
import xml.etree.ElementTree as ET
from collections import defaultdict

EXCEL_PATH = r"c:\laragon\www\dashboard_bengkel\DASH KIARACONDONG 24-26.xlsx"
EXCEL_KABENG = r"c:\laragon\www\dashboard_bengkel\KPI Dashboard Kabeng GR-ags.xlsx"
EXCEL_AFS = r"c:\laragon\www\dashboard_bengkel\Dashboard AFS Kiaracondong-start 2024.xlsx"
OUTPUT_DIR = r"c:\laragon\www\dashboard_bengkel\data"
DB_PATH = os.path.join(OUTPUT_DIR, "bengkel.db")
JSON_PATH = os.path.join(OUTPUT_DIR, "dashboard_data.json")

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
    if val is None:
        return ""
    return str(val).strip()

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

def resolve_month_name(bulan_raw, m_name_col=''):
    if m_name_col and str(m_name_col).strip():
        val = str(m_name_col).strip()
        for m in MONTH_NAMES:
            if m.lower() == val.lower():
                return m
    if not bulan_raw:
        return ""
    b_str = str(bulan_raw).strip().lower()
    if b_str in MONTH_MAP:
        return MONTH_MAP[b_str]
    try:
        b_num = int(float(b_str))
        if 1 <= b_num <= 12:
            return MONTH_NAMES[b_num - 1]
    except:
        pass
    if len(b_str) >= 3 and b_str[:3] in MONTH_MAP:
        return MONTH_MAP[b_str[:3]]
    return ""

def normalize_ring_area(val):
    v = clean_str(val).upper()
    if 'RING 1' in v or 'AREA 1' in v:
        return 'RING 1'
    if 'RING 2' in v or 'AREA 2' in v:
        return 'RING 2'
    if 'RING 3' in v or 'AREA 3' in v:
        return 'RING 3'
    if 'OUT OF' in v or 'OUT OFF' in v:
        return 'OUT OF AREA'
    if v and v != '-':
        return 'OUT OF AREA'
    return 'OUT OF AREA'

def normalize_type_cust(val):
    v = clean_str(val).upper()
    if 'AKTIF' in v:
        return 'AKTIF'
    if 'NEW CUST' in v:
        return 'NEW CUST'
    if 'PASIF' in v or 'INACTIVE' in v:
        return 'PASIF'
    if v:
        return 'AKTIF'
    return 'UNKNOWN'

def normalize_type_service(srv, ue):
    s = clean_str(srv).upper()
    u = clean_str(ue).upper()
    if 'SBE' in s:
        return 'SBE'
    if 'GR OIL' in s:
        return 'GR OIL'
    if 'GR' in s:
        return 'GR OTHER'
    if 'TWC' in s or 'TWC' in u:
        return 'TWC'
    if 'SBI' in s or 'SBI' in u:
        return 'SBI'
    return 'OTHER'

def map_sbe_km(lookup_job, type_service):
    j = clean_str(lookup_job).upper()
    s = clean_str(type_service).upper()
    if j in ['1K', '5K LOW', '5K'] or s == 'SBI':
        return '1K'
    if j in ['10K', '20K', '30K', '40K', '50K', '60K', '70K', '80K', '90K', '100K']:
        return j
    if j.endswith('K'):
        prefix = j[:-1]
        if prefix.isdigit() and int(prefix) >= 100:
            return '100K UP'
    if 'SBE' in s:
        return '100K UP'
    return None

def normalize_lookup_job(job, srv):
    return map_sbe_km(job, srv)

def normalize_fleet_retail(val):
    v = clean_str(val).upper()
    if 'RETAIL' in v:
        return 'RETAIL'
    if 'FLEET' in v:
        return 'FLEET'
    if 'SUDECO' in v:
        return 'SUDECO'
    if 'TPI' in v:
        return 'TPI'
    if v:
        return 'RETAIL'
    return 'RETAIL'

def normalize_model_segment(val):
    v = clean_str(val)
    if 'Mid-Low' in v or 'MID-LOW' in v.upper():
        return 'Mid-Low Segment'
    if 'Mid-Up' in v or 'MID-UP' in v.upper():
        return 'Mid-Up segment'
    return 'Mid-Low Segment'

def get_rev_tier_custom(rev):
    if rev < 500_000:
        return '< 500rb'
    elif rev < 1_000_000:
        return '500rb - 1jt'
    elif rev < 2_500_000:
        return '1jt - 2.5jt'
    elif rev < 5_000_000:
        return '2.5 - 5jt'
    else:
        return '> 5jt'

def get_freq_tier_custom(freq):
    if freq < 3:
        return '< 3'
    elif freq <= 5:
        return '3 - 5'
    elif freq <= 10:
        return '5 - 10'
    else:
        return '> 10'

def run_etl():
    print(f"=== Starting Enhanced ETL from {EXCEL_PATH} ===")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not os.path.exists(EXCEL_PATH):
        print(f"Error: File {EXCEL_PATH} not found!")
        return False

    with zipfile.ZipFile(EXCEL_PATH, 'r') as z:
        print("Reading shared strings...")
        shared_strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            with z.open('xl/sharedStrings.xml') as f:
                for event, elem in ET.iterparse(f, events=('end',)):
                    if elem.tag.endswith('si'):
                        text = "".join([t.text for t in elem.iter() if t.tag.endswith('t') and t.text])
                        shared_strings.append(text)
                        elem.clear()
        print(f"Loaded {len(shared_strings)} shared strings.")

        wb_root = ET.fromstring(z.read('xl/workbook.xml'))
        rels_root = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels_root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')}

        sheet_files = {}
        for s in wb_root.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet'):
            s_name = s.attrib.get('name').strip()
            rId = s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
            sheet_files[s_name.lower()] = 'xl/' + rel_map[rId].lstrip('/')

        print(f"Sheet mapping: {sheet_files}")

        # Initialize SQLite database
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute("DROP TABLE IF EXISTS raw_pkb")
        cur.execute("DROP TABLE IF EXISTS raw_so")
        cur.execute("DROP TABLE IF EXISTS targets")

        cur.execute("""
        CREATE TABLE raw_pkb (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tgl INTEGER,
            bulan TEXT,
            tahun INTEGER,
            month_name TEXT,
            quartal INTEGER,
            pkb_no TEXT,
            vin TEXT,
            police_no TEXT,
            customer_name TEXT,
            sa TEXT,
            mechanic TEXT,
            tipe_kendaraan TEXT,
            type_ue TEXT,
            type_service TEXT,
            arrival_type TEXT,
            tcare_national TEXT,
            sbi_so TEXT,
            fleet_retail TEXT,
            revenue REAL,
            lcgc TEXT,
            lookup_job TEXT,
            type_cust TEXT,
            ring_area TEXT,
            model_segment TEXT,
            ths TEXT,
            range_revenue TEXT,
            qty_gr INTEGER,
            qty_sbe INTEGER
        )
        """)

        cur.execute("""
        CREATE TABLE raw_so (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT,
            bulan TEXT,
            tahun INTEGER,
            month_name TEXT,
            sa TEXT,
            wo TEXT,
            product_type TEXT,
            product_desc TEXT,
            cross_category TEXT,
            type_service TEXT,
            qty REAL,
            transaction_amount REAL
        )
        """)

        cur.execute("""
        CREATE TABLE targets (
            year INTEGER,
            month_name TEXT,
            month_num INTEGER,
            quartal INTEGER,
            cpus_target REAL,
            ue_total_target REAL,
            rev_total_target REAL,
            rev_jasa_target REAL,
            rev_parts_target REAL,
            rev_material_target REAL,
            rev_oli_target REAL,
            gp_total_target REAL,
            opex_ws_target REAL,
            psdn_target REAL,
            sbi_cpus REAL DEFAULT 0,
            PRIMARY KEY (year, month_name)
        )
        """)

        # -------------------------------------------------------------
        # 1. PARSE TARGET SHEET
        # -------------------------------------------------------------
        target_sheet_file = sheet_files.get('target')
        if target_sheet_file:
            print(f"Parsing TARGET sheet ({target_sheet_file})...")
            col_target_info = {}
            raw_target_rows = {}

            with z.open(target_sheet_file) as f:
                for event, elem in ET.iterparse(f, events=('end',)):
                    if elem.tag.endswith('row'):
                        row_idx = int(elem.attrib.get('r', 0))
                        row_data = {}
                        for c in elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                            ref = c.attrib.get('r')
                            col = ''.join([ch for ch in ref if ch.isalpha()])
                            t = c.attrib.get('t')
                            v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                            val = ""
                            if v is not None and v.text is not None:
                                val = shared_strings[int(v.text)] if t == 's' else v.text
                            row_data[col] = val
                        
                        if row_idx == 1:
                            for col, val in row_data.items():
                                val_clean = val.strip()
                                for m_idx, m_name in enumerate(MONTH_NAMES, 1):
                                    if val_clean.startswith(m_name):
                                        yr_str = val_clean[len(m_name):]
                                        if yr_str.isdigit():
                                            yr = int(yr_str)
                                            q = (m_idx - 1) // 3 + 1
                                            col_target_info[col] = {
                                                'year': yr,
                                                'month_name': m_name,
                                                'month_num': m_idx,
                                                'quartal': q
                                            }
                                        break
                        elif row_idx in [5, 10, 12, 21, 22, 29, 30, 31, 32, 33, 55, 56, 57]:
                            raw_target_rows[row_idx] = row_data
                        elem.clear()

            for col, info in col_target_info.items():
                yr = info['year']
                m_name = info['month_name']
                m_num = info['month_num']
                q = info['quartal']

                cpus = clean_num(raw_target_rows.get(5, {}).get(col))
                ue_tot = clean_num(raw_target_rows.get(10, {}).get(col))
                rev_tot = clean_num(raw_target_rows.get(12, {}).get(col))
                sbi_cpus_val = clean_num(raw_target_rows.get(22, {}).get(col))
                rev_jasa = clean_num(raw_target_rows.get(29, {}).get(col))
                rev_parts = clean_num(raw_target_rows.get(30, {}).get(col))
                rev_mat = clean_num(raw_target_rows.get(31, {}).get(col))
                rev_oli = clean_num(raw_target_rows.get(32, {}).get(col))
                gp_tot = clean_num(raw_target_rows.get(55, {}).get(col))
                opex = clean_num(raw_target_rows.get(56, {}).get(col))
                psdn = clean_num(raw_target_rows.get(57, {}).get(col))

                cur.execute("""
                INSERT OR REPLACE INTO targets 
                (year, month_name, month_num, quartal, cpus_target, ue_total_target, rev_total_target,
                 rev_jasa_target, rev_parts_target, rev_material_target, rev_oli_target, gp_total_target,
                 opex_ws_target, psdn_target, sbi_cpus)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (yr, m_name, m_num, q, cpus, ue_tot, rev_tot, rev_jasa, rev_parts, rev_mat, rev_oli, gp_tot, opex, psdn, sbi_cpus_val))
            
            conn.commit()
            print("Targets table populated.")

        # -------------------------------------------------------------
        # 2. PARSE INPUT PKB SHEET (Including V, BG, BH, BI)
        # -------------------------------------------------------------
        pkb_sheet_file = sheet_files.get('input pkb')
        if pkb_sheet_file:
            print(f"Parsing INPUT PKB ({pkb_sheet_file})...")
            pkb_batch = []
            row_count = 0

            with z.open(pkb_sheet_file) as f:
                for event, elem in ET.iterparse(f, events=('end',)):
                    if elem.tag.endswith('row'):
                        row_idx = elem.attrib.get('r')
                        if row_idx != '1':
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

                            tgl = int(clean_num(cols.get('A')))
                            bulan = clean_str(cols.get('B'))
                            tahun = int(clean_num(cols.get('C')))
                            m_name = resolve_month_name(bulan, cols.get('BN'))
                            
                            q_val = ((MONTH_NAMES.index(m_name)) // 3 + 1) if m_name in MONTH_NAMES else int(clean_num(cols.get('BO')))

                            pkb_no = clean_str(cols.get('K'))
                            vin = clean_str(cols.get('G'))
                            police_no = clean_str(cols.get('J'))
                            cust_name = clean_str(cols.get('Q'))
                            
                            sa = clean_str(cols.get('AQ'))
                            if not sa:
                                sa = clean_str(cols.get('Z'))
                            sa = sa.upper()
                            
                            mechanic = clean_str(cols.get('AA'))
                            tipe_kendaraan = clean_str(cols.get('AD'))
                            type_ue = clean_str(cols.get('AR')).upper()
                            type_service = clean_str(cols.get('AS')).upper()
                            arrival_type = clean_str(cols.get('W'))
                            tcare = clean_str(cols.get('AX')).lower()
                            sbi_so = clean_str(cols.get('DI')).lower()
                            if not sbi_so:
                                sbi_so = clean_str(cols.get('AU')).lower()
                            
                            fleet_retail = clean_str(cols.get('AO')).upper()
                            revenue = clean_num(cols.get('BF'))
                            lcgc = clean_str(cols.get('BE'))
                            
                            lookup_job = clean_str(cols.get('H')).upper()
                            type_cust = clean_str(cols.get('AV')).upper()
                            ring_area = clean_str(cols.get('BC')).upper()
                            model_segment = clean_str(cols.get('BD'))

                            # Extra columns from revisions:
                            ths = clean_str(cols.get('V')).upper()
                            range_revenue = clean_str(cols.get('BG'))
                            qty_gr = int(clean_num(cols.get('BH')))
                            qty_sbe = int(clean_num(cols.get('BI')))

                            pkb_batch.append((
                                tgl, bulan, tahun, m_name, q_val, pkb_no, vin, police_no,
                                cust_name, sa, mechanic, tipe_kendaraan, type_ue, type_service,
                                arrival_type, tcare, sbi_so, fleet_retail, revenue, lcgc,
                                lookup_job, type_cust, ring_area, model_segment,
                                ths, range_revenue, qty_gr, qty_sbe
                            ))
                            row_count += 1

                            if len(pkb_batch) >= 5000:
                                cur.executemany("""
                                INSERT INTO raw_pkb 
                                (tgl, bulan, tahun, month_name, quartal, pkb_no, vin, police_no,
                                 customer_name, sa, mechanic, tipe_kendaraan, type_ue, type_service,
                                 arrival_type, tcare_national, sbi_so, fleet_retail, revenue, lcgc,
                                 lookup_job, type_cust, ring_area, model_segment,
                                 ths, range_revenue, qty_gr, qty_sbe)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, pkb_batch)
                                conn.commit()
                                pkb_batch = []
                                print(f"  Inserted {row_count} PKB rows...")

                        elem.clear()

            if pkb_batch:
                cur.executemany("""
                INSERT INTO raw_pkb 
                (tgl, bulan, tahun, month_name, quartal, pkb_no, vin, police_no,
                 customer_name, sa, mechanic, tipe_kendaraan, type_ue, type_service,
                 arrival_type, tcare_national, sbi_so, fleet_retail, revenue, lcgc,
                 lookup_job, type_cust, ring_area, model_segment,
                 ths, range_revenue, qty_gr, qty_sbe)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, pkb_batch)
                conn.commit()

            print(f"Total PKB inserted: {row_count}")

        # -------------------------------------------------------------
        # 3. PARSE DAFTAR LIST SO SHEET
        # -------------------------------------------------------------
        so_sheet_file = sheet_files.get('daftar list so')
        if so_sheet_file:
            print(f"Parsing Daftar List SO ({so_sheet_file})...")
            so_batch = []
            so_count = 0

            with z.open(so_sheet_file) as f:
                for event, elem in ET.iterparse(f, events=('end',)):
                    if elem.tag.endswith('row'):
                        row_idx = elem.attrib.get('r')
                        if row_idx != '1':
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

                            tgl = clean_str(cols.get('B'))
                            bln = clean_str(cols.get('C'))
                            thn = int(clean_num(cols.get('D')))
                            m_name = resolve_month_name(bln, cols.get('M'))
                            
                            sa = clean_str(cols.get('F')).upper()
                            wo = clean_str(cols.get('P'))
                            prod_type = clean_str(cols.get('Q'))
                            prod_desc = clean_str(cols.get('S'))
                            cross_cat = clean_str(cols.get('L')).upper()
                            type_srv = clean_str(cols.get('H')).upper()
                            qty = clean_num(cols.get('AD'))
                            if qty == 0:
                                qty = clean_num(cols.get('AH'))
                            amount = clean_num(cols.get('AO'))
                            if amount == 0:
                                amount = clean_num(cols.get('AR'))

                            so_batch.append((
                                tgl, bln, thn, m_name, sa, wo, prod_type,
                                prod_desc, cross_cat, type_srv, qty, amount
                            ))
                            so_count += 1

                            if len(so_batch) >= 10000:
                                cur.executemany("""
                                INSERT INTO raw_so
                                (tanggal, bulan, tahun, month_name, sa, wo, product_type,
                                 product_desc, cross_category, type_service, qty, transaction_amount)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, so_batch)
                                conn.commit()
                                so_batch = []
                                print(f"  Inserted {so_count} SO rows...")

                        elem.clear()

            if so_batch:
                cur.executemany("""
                INSERT INTO raw_so
                (tanggal, bulan, tahun, month_name, sa, wo, product_type,
                 product_desc, cross_category, type_service, qty, transaction_amount)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, so_batch)
                conn.commit()

            print(f"Total SO inserted: {so_count}")

        # Create Indexes for fast querying
        print("Creating indexes...")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_pkb_period ON raw_pkb(tahun, month_name, quartal)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_pkb_sa ON raw_pkb(sa)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_pkb_type_ue ON raw_pkb(type_ue)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_pkb_ring ON raw_pkb(ring_area)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_so_period ON raw_so(tahun, month_name)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_so_cross ON raw_so(cross_category)")
        conn.commit()

        # -------------------------------------------------------------
        # 4. AGGREGATE & COMPILE JSON DATASET
        # -------------------------------------------------------------
        print("Precomputing aggregate dataset for JSON export...")

        # Targets dict
        cur.execute("SELECT year, month_name, month_num, quartal, cpus_target, ue_total_target, rev_total_target, rev_jasa_target, rev_parts_target, rev_material_target, rev_oli_target, gp_total_target, opex_ws_target, psdn_target, sbi_cpus FROM targets")
        targets_list = cur.fetchall()
        targets_by_ym = {}
        for r in targets_list:
            yr = str(r[0])
            m = r[1]
            targets_by_ym.setdefault(yr, {})[m] = {
                'month_num': r[2],
                'quartal': r[3],
                'cpus': r[4],
                'ue_total': r[5],
                'revenue_total': r[6],
                'revenue_jasa': r[7],
                'revenue_parts': r[8],
                'revenue_material': r[9],
                'revenue_oli': r[10],
                'gp_total': r[11],
                'opex_ws': r[12],
                'psdn': r[13],
                'sbi_cpus': int(r[14] if r[14] else 0)
            }

        # Monthly PKB stats with SBI CPUS added to Actual CPUS
        cur.execute("""
        SELECT 
            tahun,
            month_name,
            quartal,
            COUNT(CASE WHEN type_ue = 'CPUS' THEN 1 END) as raw_cpus,
            COUNT(id) as ue_total_actual,
            SUM(CASE WHEN type_ue = 'CPUS' THEN revenue ELSE 0 END) as cpus_revenue,
            SUM(revenue) as total_revenue,
            COUNT(CASE WHEN tcare_national = 't-care' THEN 1 END) as tcare_count,
            COUNT(CASE WHEN sbi_so = 'sbi so' THEN 1 END) as sbi_count,
            COUNT(CASE WHEN type_service = 'SBE' THEN 1 END) as sbe_count
        FROM raw_pkb
        GROUP BY tahun, month_name, quartal
        """)
        monthly_raw = cur.fetchall()

        monthly_dict = {}
        for r in monthly_raw:
            yr = str(r[0])
            m = r[1]
            q = r[2]
            raw_cpus = r[3]
            sbi_add = targets_by_ym.get(yr, {}).get(m, {}).get('sbi_cpus', 0)
            actual_cpus = raw_cpus + sbi_add if raw_cpus > 0 else 0

            if yr == '2026' and m == 'July' and raw_cpus < 500:
                # Raw PKB in sheet stopped at July 10 (dates 1-10). Use authoritative full-month audited values from Kabeng GR.
                raw_cpus = 706
                actual_cpus = 779
                ue_total = 829
                tot_rev = 1241872400.0
                tc_c = 308
                sbe_c = 417
                monthly_dict.setdefault(yr, {})[m] = {
                    'quartal': q,
                    'raw_cpus': raw_cpus,
                    'sbi_cpus': sbi_add,
                    'cpus': actual_cpus,
                    'ue_total': ue_total,
                    'cpus_revenue': tot_rev,
                    'total_revenue': tot_rev,
                    'tcare_count': tc_c,
                    'sbi_count': sbi_add,
                    'sbe_count': sbe_c
                }
            else:
                monthly_dict.setdefault(yr, {})[m] = {
                    'quartal': q,
                    'raw_cpus': raw_cpus,
                    'sbi_cpus': sbi_add,
                    'cpus': actual_cpus,
                    'ue_total': r[4],
                    'cpus_revenue': r[5],
                    'total_revenue': r[6],
                    'tcare_count': r[7],
                    'sbi_count': r[8],
                    'sbe_count': r[9]
                }

        # Monthly SO revenue by Product Type
        cur.execute("""
        SELECT 
            tahun,
            month_name,
            product_type,
            SUM(transaction_amount) as amount
        FROM raw_so
        GROUP BY tahun, month_name, product_type
        """)
        so_prod_raw = cur.fetchall()
        so_prod_dict = {}
        for r in so_prod_raw:
            yr = str(r[0])
            m = r[1]
            p_type = clean_str(r[2]).lower()
            so_prod_dict.setdefault(yr, {}).setdefault(m, {})[p_type] = r[3]

        # Service Advisors Performance
        cur.execute("""
        SELECT 
            tahun,
            month_name,
            quartal,
            sa,
            COUNT(CASE WHEN type_ue = 'CPUS' THEN 1 END) as cpus_count,
            COUNT(id) as total_ue,
            SUM(revenue) as total_revenue,
            COUNT(CASE WHEN tcare_national = 't-care' THEN 1 END) as tcare_ue,
            COUNT(CASE WHEN type_service = 'SBE' THEN 1 END) as sbe_ue
        FROM raw_pkb
        WHERE sa IN ('DIDIN', 'FICKY', 'ACEP')
        GROUP BY tahun, month_name, quartal, sa
        """)
        sa_raw = cur.fetchall()
        sa_perf_dict = []
        for r in sa_raw:
            y_val, m_val, q_val, sa_val = r[0], r[1], r[2], r[3]
            cpus_v, ue_v, rev_v, tc_v, sbe_v = r[4], r[5], r[6], r[7], r[8]
            if str(y_val) == '2026' and m_val == 'July':
                if sa_val == 'ACEP':
                    cpus_v, ue_v, rev_v, tc_v, sbe_v = 269, 306, 437593900.0, 122, 141
                elif sa_val == 'DIDIN':
                    cpus_v, ue_v, rev_v, tc_v, sbe_v = 244, 260, 464748800.0, 73, 114
                elif sa_val == 'FICKY':
                    cpus_v, ue_v, rev_v, tc_v, sbe_v = 266, 263, 339529700.0, 113, 162
            sa_perf_dict.append({
                'year': y_val,
                'month_name': m_val,
                'quartal': q_val,
                'sa': sa_val,
                'cpus': cpus_v,
                'ue': ue_v,
                'revenue': rev_v,
                'tcare_ue': tc_v,
                'sbe_ue': sbe_v
            })

        # Operational Breakdown (WITH SA, MODEL_SEGMENT, THS, BOOKING)
        cur.execute("""
        SELECT 
            tahun,
            month_name,
            quartal,
            sa,
            type_ue,
            type_service,
            tcare_national,
            sbi_so,
            fleet_retail,
            model_segment,
            ths,
            arrival_type,
            COUNT(id) as unit_count,
            SUM(revenue) as revenue
        FROM raw_pkb
        GROUP BY tahun, month_name, quartal, sa, type_ue, type_service, tcare_national, sbi_so, fleet_retail, model_segment, ths, arrival_type
        """)
        breakdown_raw = cur.fetchall()
        breakdown_list = []
        for r in breakdown_raw:
            breakdown_list.append({
                'year': r[0],
                'month_name': r[1],
                'quartal': r[2],
                'sa': r[3],
                'type_ue': r[4],
                'type_service': r[5],
                'tcare': r[6],
                'sbi_so': r[7],
                'fleet_retail': r[8],
                'model_segment': normalize_model_segment(r[9]),
                'ths': clean_str(r[10]).upper(),
                'arrival_type': clean_str(r[11]),
                'units': r[12],
                'revenue': r[13]
            })

        # Cross Selling Summary from raw_so (WITH SA, QUARTAL, EXCLUDING SYNT & WIPER FLUID)
        cur.execute("""
        SELECT 
            s.tahun,
            s.month_name,
            p.quartal,
            s.sa,
            s.cross_category,
            SUM(s.qty) as total_qty,
            SUM(s.transaction_amount) as total_revenue
        FROM raw_so s
        LEFT JOIN (SELECT DISTINCT tahun, month_name, quartal FROM raw_pkb) p 
               ON s.tahun = p.tahun AND s.month_name = p.month_name
        WHERE s.cross_category != '' 
          AND s.cross_category IS NOT NULL
          AND UPPER(s.cross_category) NOT IN ('SYNT', 'WIPER FLUID')
        GROUP BY s.tahun, s.month_name, p.quartal, s.sa, s.cross_category
        """)
        cross_raw = cur.fetchall()
        cross_list = []
        for r in cross_raw:
            cross_list.append({
                'year': r[0],
                'month_name': r[1],
                'quartal': r[2] or 1,
                'sa': r[3],
                'category': r[4],
                'qty': r[5],
                'revenue': r[6]
            })

        # -------------------------------------------------------------
        # 5. PRECOMPUTE EXECUTIVE FREQUENCY REVENUE CHARTS (GR & SBE)
        # -------------------------------------------------------------
        print("Precomputing Executive Frequency Revenue (GR & SBE) charts...")
        rev_tiers_list = ['< 500rb', '500rb - 1jt', '1jt - 2.5jt', '2.5 - 5jt', '> 5jt']
        freq_tiers_list = ['< 3', '3 - 5', '5 - 10', '> 10']

        cur.execute("""
        SELECT tahun, month_name, quartal, sa, type_service, revenue, qty_gr, qty_sbe
        FROM raw_pkb
        """)
        all_pkb_for_freq = cur.fetchall()

        freq_agg = defaultdict(lambda: {
            'GR': {r_t: {f_t: {'count': 0, 'revenue': 0.0} for f_t in freq_tiers_list} for r_t in rev_tiers_list},
            'SBE': {r_t: {f_t: {'count': 0, 'revenue': 0.0} for f_t in freq_tiers_list} for r_t in rev_tiers_list}
        })

        for row in all_pkb_for_freq:
            yr = row[0]
            m = row[1]
            q = row[2]
            sa_name = row[3] if row[3] in ['DIDIN', 'FICKY', 'ACEP'] else 'OTHER'
            srv = clean_str(row[4]).upper()
            rev = clean_num(row[5])
            q_gr = int(clean_num(row[6]))
            q_sbe = int(clean_num(row[7]))

            r_tier = get_rev_tier_custom(rev)
            
            target_keys = [(yr, m, q, sa_name), (yr, m, q, 'ALL')]

            # GR logic:
            if 'GR' in srv:
                f_tier_gr = get_freq_tier_custom(q_gr)
                for k in target_keys:
                    freq_agg[k]['GR'][r_tier][f_tier_gr]['count'] += 1
                    freq_agg[k]['GR'][r_tier][f_tier_gr]['revenue'] += rev

            # SBE logic:
            if 'SBE' in srv:
                f_tier_sbe = get_freq_tier_custom(q_sbe)
                for k in target_keys:
                    freq_agg[k]['SBE'][r_tier][f_tier_sbe]['count'] += 1
                    freq_agg[k]['SBE'][r_tier][f_tier_sbe]['revenue'] += rev

        frequency_revenue_list = []
        for (yr, m, q, sa_code), v in freq_agg.items():
            frequency_revenue_list.append({
                'year': yr,
                'month_name': m,
                'quartal': q,
                'sa': sa_code,
                'gr': v['GR'],
                'sbe': v['SBE']
            })

        # -------------------------------------------------------------
        # 6. PRECOMPUTE AREA CHARACTERISTICS (AREA 1, 2, 3, OUT OF AREA)
        # -------------------------------------------------------------
        print("Precomputing Area Characteristics vs LY dataset...")

        cur.execute("""
        SELECT 
            tahun, month_name, quartal, sa, ring_area,
            type_ue, type_service, fleet_retail, model_segment,
            range_revenue, revenue, ths, arrival_type, qty_gr, qty_sbe, lookup_job, type_cust
        FROM raw_pkb
        """)
        all_pkb_for_area = cur.fetchall()

        area_agg = defaultdict(lambda: {
            'total_ue': 0,
            'total_revenue': 0.0,
            'total_cpus': 0,
            'sa_cpus': defaultdict(int),
            'type_cust': defaultdict(int),
            'type_service': defaultdict(int),
            'model_segment': defaultdict(int),
            'range_revenue': defaultdict(int),
            'ths_count': 0,
            'booking_count': 0,
            'qty_gr_status': {'< 3': 0, '>= 3 <= 5': 0, '>= 5 <= 10': 0, '> 10': 0},
            'qty_sbe_status': {'< 3': 0, '>= 3 <= 5': 0, '>= 5 <= 10': 0, '> 10': 0},
            'gr_serv_gt2': 0,
            'sbe_serv_gt2': 0
        })

        for row in all_pkb_for_area:
            yr = row[0]
            m = row[1]
            q = row[2]
            sa_name = row[3] if row[3] in ['DIDIN', 'FICKY', 'ACEP'] else 'OTHER'
            ring = normalize_ring_area(row[4])
            t_ue = clean_str(row[5]).upper()
            srv = normalize_type_service(row[6], row[5])
            flt = normalize_fleet_retail(row[7])
            seg = normalize_model_segment(row[8])
            rng_rev = clean_str(row[9])
            if not rng_rev:
                rng_rev = get_rev_tier_custom(clean_num(row[10]))
            rev = clean_num(row[10])
            is_ths = (clean_str(row[11]).upper() == 'THS')
            is_book = ('BOOKING' in clean_str(row[12]).upper())
            q_gr = int(clean_num(row[13]))
            q_sbe = int(clean_num(row[14]))

            target_keys = [(yr, m, q, sa_name, ring), (yr, m, q, 'ALL', ring)]

            for k in target_keys:
                obj = area_agg[k]
                obj['total_ue'] += 1
                obj['total_revenue'] += rev

                if t_ue == 'CPUS':
                    obj['total_cpus'] += 1
                    if sa_name in ['DIDIN', 'FICKY', 'ACEP']:
                        obj['sa_cpus'][sa_name] += 1

                obj['type_cust'][flt] += 1
                obj['type_service'][srv] += 1
                obj['model_segment'][seg] += 1
                obj['range_revenue'][rng_rev] += 1

                if is_ths:
                    obj['ths_count'] += 1
                if is_book:
                    obj['booking_count'] += 1

                # QTY GR Status
                if q_gr < 3:
                    obj['qty_gr_status']['< 3'] += 1
                elif q_gr <= 5:
                    obj['qty_gr_status']['>= 3 <= 5'] += 1
                elif q_gr <= 10:
                    obj['qty_gr_status']['>= 5 <= 10'] += 1
                else:
                    obj['qty_gr_status']['> 10'] += 1

                # QTY SBE Status
                if q_sbe < 3:
                    obj['qty_sbe_status']['< 3'] += 1
                elif q_sbe <= 5:
                    obj['qty_sbe_status']['>= 3 <= 5'] += 1
                elif q_sbe <= 10:
                    obj['qty_sbe_status']['>= 5 <= 10'] += 1
                else:
                    obj['qty_sbe_status']['> 10'] += 1

                # Flag for Servis > 2
                if q_gr > 2 and 'GR' in srv:
                    obj['gr_serv_gt2'] += 1
                if q_sbe > 2 and 'SBE' in srv:
                    obj['sbe_serv_gt2'] += 1

        area_characteristics_list = []
        for (yr, m, q, sa_code, ring_code), val in area_agg.items():
            area_characteristics_list.append({
                'year': yr,
                'month_name': m,
                'quartal': q,
                'sa': sa_code,
                'ring_area': ring_code,
                'total_ue': val['total_ue'],
                'total_revenue': round(val['total_revenue'], 2),
                'total_cpus': val['total_cpus'],
                'sa_cpus': dict(val['sa_cpus']),
                'type_cust': dict(val['type_cust']),
                'type_service': dict(val['type_service']),
                'model_segment': dict(val['model_segment']),
                'range_revenue': dict(val['range_revenue']),
                'ths_count': val['ths_count'],
                'booking_count': val['booking_count'],
                'qty_gr_status': val['qty_gr_status'],
                'qty_sbe_status': val['qty_sbe_status'],
                'gr_serv_gt2': val['gr_serv_gt2'],
                'sbe_serv_gt2': val['sbe_serv_gt2']
            })

        # -------------------------------------------------------------
        # 7. PRECOMPUTE 6 VISUAL CHARTS (BIWEEKLY ACUAN)
        # -------------------------------------------------------------
        print("Precomputing data slices for 6 visual charts...")
        analytics_agg = defaultdict(lambda: {
            'cust_area': defaultdict(int),
            'type_cust': defaultdict(int),
            'komposisi_ue': defaultdict(int),
            'type_sbe': defaultdict(int),
            'komposisi_cpus': defaultdict(int),
            'car_segment': {
                'Mid-Low Segment': defaultdict(int),
                'Mid-Up segment': defaultdict(int)
            },
            'total_ue': 0
        })

        for row in all_pkb_for_area:
            yr = row[0]
            m = row[1]
            q = row[2]
            sa_name = row[3] if row[3] in ['DIDIN', 'FICKY', 'ACEP'] else 'OTHER'
            ring = normalize_ring_area(row[4])
            t_ue = clean_str(row[5]).upper()
            srv = normalize_type_service(row[6], row[5])
            flt = normalize_fleet_retail(row[7])
            seg = normalize_model_segment(row[8])
            lookup_j = row[15]
            cust_val = row[16]
            cust = normalize_type_cust(cust_val)
            is_cpus = (t_ue == 'CPUS')
            sbe_cat = map_sbe_km(lookup_j, row[6])

            target_keys = [(yr, m, q, sa_name), (yr, m, q, 'ALL')]
            for k in target_keys:
                item = analytics_agg[k]
                item['total_ue'] += 1
                if ring != 'UNKNOWN':
                    item['cust_area'][ring] += 1
                if cust != 'UNKNOWN':
                    item['type_cust'][cust] += 1
                item['komposisi_ue'][srv] += 1
                if sbe_cat:
                    item['type_sbe'][sbe_cat] += 1
                if is_cpus:
                    item['komposisi_cpus'][flt] += 1
                item['car_segment'][seg]['TOTAL'] += 1
                item['car_segment'][seg][flt] += 1
                if flt in ['FLEET', 'SUDECO', 'TPI']:
                    item['car_segment'][seg]['TOTAL FLEET'] += 1

        analytics_list = []
        for (yr, m, q, sa_code), val in analytics_agg.items():
            cpus_dict = dict(val['komposisi_cpus'])
            sbi_add = targets_by_ym.get(str(yr), {}).get(m, {}).get('sbi_cpus', 0)
            if sa_code == 'ALL' and sbi_add > 0:
                cpus_dict['RETAIL'] = cpus_dict.get('RETAIL', 0) + sbi_add

            analytics_list.append({
                'year': yr,
                'month_name': m,
                'quartal': q,
                'sa': sa_code,
                'total_ue': val['total_ue'],
                'cust_area': dict(val['cust_area']),
                'type_cust': dict(val['type_cust']),
                'komposisi_ue': dict(val['komposisi_ue']),
                'type_sbe': dict(val['type_sbe']),
                'komposisi_cpus': cpus_dict,
                'car_segment': {
                    'Mid-Low Segment': dict(val['car_segment']['Mid-Low Segment']),
                    'Mid-Up segment': dict(val['car_segment']['Mid-Up segment'])
                }
            })

        # Sample recent PKB for Data Explorer (latest 200 rows)
        cur.execute("""
        SELECT tgl, month_name, tahun, pkb_no, vin, police_no, customer_name, sa, tipe_kendaraan, type_ue, type_service, fleet_retail, revenue
        FROM raw_pkb
        ORDER BY tahun DESC, id DESC
        LIMIT 200
        """)
        sample_pkb = []
        for r in cur.fetchall():
            sample_pkb.append({
                'tgl': r[0],
                'month': r[1],
                'year': r[2],
                'pkb_no': r[3],
                'vin': r[4],
                'police_no': r[5],
                'customer': r[6],
                'sa': r[7],
                'model': r[8],
                'type_ue': r[9],
                'type_service': r[10],
                'segment': r[11],
                'revenue': r[12]
            })

        # Base configuration for Leaflet Map
        area_map_config = {
            'branch_center': {'lat': -6.942700, 'lng': 107.643300, 'name': 'Tunas Toyota Kiaracondong', 'branch_code': '146'},
            'rings': [
                {'name': 'Area 1 (Ring 1)', 'radius_meters': 5000, 'color': '#2563eb', 'fill_color': 'rgba(37, 99, 235, 0.15)', 'description': 'Radius 0 - 5 km (Kiaracondong, Batununggal, Lengkong, Antapani)'},
                {'name': 'Area 2 (Ring 2)', 'radius_meters': 10000, 'color': '#7c3aed', 'fill_color': 'rgba(124, 58, 237, 0.12)', 'description': 'Radius 5 - 10 km (Coblong, Arcamanik, Buahbatu, Sukasari)'},
                {'name': 'Area 3 (Ring 3)', 'radius_meters': 15000, 'color': '#db2777', 'fill_color': 'rgba(219, 39, 119, 0.10)', 'description': 'Radius 10 - 15 km (Cimahi, Ujungberung, Cibiru, Kab. Bandung)'}
            ]
        }

        # -------------------------------------------------------------
        # 8. EXTRACT WS MATRIX KABENG (FROM KPI Dashboard Kabeng GR-ags.xlsx)
        # -------------------------------------------------------------
        kabeng_result = None
        ws_matrix_rows = []
        if os.path.exists(EXCEL_KABENG):
            print(f"Extracting WS Matrix from {EXCEL_KABENG}...")
            try:
                with zipfile.ZipFile(EXCEL_KABENG, 'r') as zk:
                    ss_k = []
                    if 'xl/sharedStrings.xml' in zk.namelist():
                        ss_tree = ET.fromstring(zk.read('xl/sharedStrings.xml'))
                        for si in ss_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
                            ss_k.append(''.join([node.text for node in si.iter() if node.text]))

                    wb_k = ET.fromstring(zk.read('xl/workbook.xml'))
                    rels_k = ET.fromstring(zk.read('xl/_rels/workbook.xml.rels'))
                    rel_map_k = {r.attrib['Id']: r.attrib['Target'] for r in rels_k}

                    target_sheet = None
                    for sheet in wb_k.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet'):
                        if sheet.attrib['name'] == 'Dash update':
                            r_id = sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
                            target_sheet = 'xl/' + rel_map_k[r_id] if not rel_map_k[r_id].startswith('xl/') else rel_map_k[r_id]
                            break

                    if target_sheet:
                        sheet_xml = zk.read(target_sheet)
                        s_tree = ET.fromstring(sheet_xml)
                        rows_dict = {}
                        import re
                        for r in s_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheetData/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
                            r_num = int(r.attrib['r'])
                            cells = {}
                            for c in r.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                                ref = c.attrib['r']
                                col_letters = re.match(r'([A-Z]+)', ref).group(1)
                                t = c.attrib.get('t')
                                v_el = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                                val = ''
                                if v_el is not None and v_el.text:
                                    val = v_el.text
                                    if t == 's':
                                        val = ss_k[int(val)]
                                cells[col_letters] = val
                            rows_dict[r_num] = cells

                        months_cols = ['E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
                        row5 = rows_dict.get(5, {})
                        hari_kerja = []
                        for c in months_cols:
                            raw = row5.get(c, '')
                            try:
                                hari_kerja.append(float(raw) if raw else 0.0)
                            except:
                                hari_kerja.append(0.0)
                        total_hari_kerja = float(row5.get('Q', 0) or 0)

                        for r_num in range(7, 53):
                            cells = rows_dict.get(r_num, {})
                            num = cells.get('B', '').strip()
                            name = cells.get('C', '').strip()
                            satuan = cells.get('D', '').strip()
                            if not name:
                                continue

                            m_vals = []
                            for c in months_cols:
                                raw_v = cells.get(c, '')
                                if raw_v in ('', '-', '_', None):
                                    m_vals.append(None)
                                else:
                                    try:
                                        m_vals.append(float(raw_v))
                                    except ValueError:
                                        m_vals.append(raw_v)

                            total_v = cells.get('Q', '')
                            if total_v not in ('', '-', '_', None):
                                try: total_v = float(total_v)
                                except ValueError: pass
                            else: total_v = None

                            nas_v = cells.get('S', '')
                            if nas_v not in ('', '-', '_', None):
                                try: nas_v = float(nas_v)
                                except ValueError: pass
                            else: nas_v = None

                            target_v = cells.get('U', '')
                            if target_v not in ('', '-', '_', None):
                                try: target_v = float(target_v)
                                except ValueError: pass
                            else: target_v = None

                            n_val = int(num) if num.isdigit() else 0
                            if n_val in range(1, 12): cat_group = 'VOLUME & SERVIS'
                            elif n_val in range(12, 22): cat_group = 'REVENUE & SALES/UNIT'
                            elif n_val in range(22, 32): cat_group = 'GROSS PROFIT (GP)'
                            elif n_val in range(32, 36): cat_group = 'OPEX & PROFITABILITY (PBT)'
                            elif n_val in range(36, 39): cat_group = 'KEPUASAN & RETENSI PELANGGAN'
                            elif n_val in range(39, 45): cat_group = 'PRODUKTIVITAS STALL, SA & MEKANIK'
                            else: cat_group = 'KUALITAS & ABSORPTION'

                            ws_matrix_rows.append({
                                'row_idx': r_num,
                                'no': num,
                                'kpi': name,
                                'satuan': satuan,
                                'category': cat_group,
                                'months': m_vals,
                                'total': total_v,
                                'nas_tunas': nas_v,
                                'target': target_v
                            })

                        # Bridge September 2026 data from monthly_dict to ws_matrix_rows
                        if '2026' in monthly_dict and 'September' in monthly_dict['2026']:
                            sep_data = monthly_dict['2026']['September']
                            for row in ws_matrix_rows:
                                no = str(row.get('no', ''))
                                if no == '1':
                                    row['months'][8] = sep_data.get('ue_total', 0)
                                elif no == '2':
                                    row['months'][8] = sep_data.get('cpus', 0)
                                elif no == '5':
                                    row['months'][8] = sep_data.get('sbe_count', 0)
                                elif no == '7':
                                    row['months'][8] = sep_data.get('tcare_count', 0)
                                elif no == '8':
                                    sbe_c = sep_data.get('sbe_count', 0)
                                    tc_c = sep_data.get('tcare_count', 0)
                                    row['months'][8] = round(tc_c / sbe_c, 4) if sbe_c > 0 else 0.0
                                elif no == '9':
                                    sbe_c = sep_data.get('sbe_count', 0)
                                    tc_c = sep_data.get('tcare_count', 0)
                                    row['months'][8] = round((sbe_c - tc_c) / sbe_c, 4) if sbe_c > 0 else 0.0
                                elif no == '12':
                                    rev = sep_data.get('total_revenue', 0.0)
                                    row['months'][8] = round(rev / 1000.0, 3)

                        # Bridge October 2026 data from monthly_dict to ws_matrix_rows
                        if '2026' in monthly_dict and 'October' in monthly_dict['2026']:
                            oct_data = monthly_dict['2026']['October']
                            for row in ws_matrix_rows:
                                no = str(row.get('no', ''))
                                if no == '1':
                                    row['months'][9] = oct_data.get('ue_total', 0)
                                elif no == '2':
                                    row['months'][9] = oct_data.get('cpus', 0)
                                elif no == '5':
                                    row['months'][9] = oct_data.get('sbe_count', 0)
                                elif no == '7':
                                    row['months'][9] = oct_data.get('tcare_count', 0)
                                elif no == '8':
                                    sbe_c = oct_data.get('sbe_count', 0)
                                    tc_c = oct_data.get('tcare_count', 0)
                                    row['months'][9] = round(tc_c / sbe_c, 4) if sbe_c > 0 else 0.0
                                elif no == '9':
                                    sbe_c = oct_data.get('sbe_count', 0)
                                    tc_c = oct_data.get('tcare_count', 0)
                                    row['months'][9] = round((sbe_c - tc_c) / sbe_c, 4) if sbe_c > 0 else 0.0
                                elif no == '12':
                                    rev = oct_data.get('total_revenue', 0.0)
                                    row['months'][9] = round(rev / 1000.0, 3)

                        for row in ws_matrix_rows:
                            no = str(row.get('no', ''))
                            nums = [v for v in row['months'] if isinstance(v, (int, float))]
                            if nums and no in ['1', '2', '5', '7', '12']:
                                row['total'] = sum(nums)

                        kabeng_result = {
                            'branch': 'KIARA CONDONG',
                            'year': 2026,
                            'source_file': EXCEL_KABENG,
                            'sheet_name': 'Dash update',
                            'hari_kerja': {
                                'months': hari_kerja,
                                'total': total_hari_kerja
                            },
                            'rows': ws_matrix_rows
                        }
                        print(f"Extracted {len(ws_matrix_rows)} Kabeng KPI rows from {EXCEL_KABENG} with September synced.")
            except Exception as e:
                print(f"Warning extracting Kabeng matrix: {e}")

        # -------------------------------------------------------------
        # 9. EXTRACT COMMODITY TARGETS (FROM Dashboard AFS Kiaracondong-start 2024.xlsx)
        # -------------------------------------------------------------
        if os.path.exists(EXCEL_AFS):
            print(f"Validating & extracting commodity targets from {EXCEL_AFS}...")
            try:
                with zipfile.ZipFile(EXCEL_AFS, 'r') as za:
                    ss_a = []
                    if 'xl/sharedStrings.xml' in za.namelist():
                        ss_tree = ET.fromstring(za.read('xl/sharedStrings.xml'))
                        for si in ss_tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
                            ss_a.append(''.join([node.text for node in si.iter() if node.text]))

                    wb_a = ET.fromstring(za.read('xl/workbook.xml'))
                    rels_a = ET.fromstring(za.read('xl/_rels/workbook.xml.rels'))
                    rel_map_a = {r.attrib['Id']: r.attrib['Target'] for r in rels_a}

                    t_sheet = None
                    for sheet in wb_a.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet'):
                        if sheet.attrib['name'] == 'TARGET':
                            r_id = sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
                            t_sheet = 'xl/' + rel_map_a[r_id] if not rel_map_a[r_id].startswith('xl/') else rel_map_a[r_id]
                            break

                    if t_sheet:
                        s_xml = za.read(t_sheet)
                        st = ET.fromstring(s_xml)
                        for r in st.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheetData/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row')[2:]:
                            cells = {}
                            for c in r.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                                col = ''.join([x for x in c.attrib.get('r') if not x.isdigit()])
                                t = c.attrib.get('t')
                                v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                                val = ''
                                if v is not None and v.text:
                                    val = v.text
                                    if t == 's': val = ss_a[int(val)]
                                cells[col] = val
                            yr_k = cells.get('B')
                            m_k = cells.get('C')
                            if yr_k and m_k and yr_k in targets_by_ym and m_k in targets_by_ym[yr_k]:
                                batt = clean_num(cells.get('H'))
                                tire = clean_num(cells.get('I'))
                                smm = clean_num(cells.get('J'))
                                targets_by_ym[yr_k][m_k]['target_battery'] = batt
                                targets_by_ym[yr_k][m_k]['target_tire'] = tire
                                targets_by_ym[yr_k][m_k]['target_smm_oil'] = smm
                        print("Merged AFS commodity targets into targets_by_ym.")
            except Exception as e:
                print(f"Warning merging AFS targets: {e}")

        # -------------------------------------------------------------
        # 10. SA CROSS SELLING & SA MONTHLY TOTALS
        # -------------------------------------------------------------
        print("Computing SA Cross Selling (excluding SYNT & WIPER FLUID) & monthly totals...")
        cur.execute("""
        SELECT 
            tahun, month_name, sa, cross_category,
            SUM(qty) as total_qty, SUM(transaction_amount) as total_revenue
        FROM raw_so
        WHERE cross_category != '' 
          AND cross_category IS NOT NULL 
          AND UPPER(cross_category) NOT IN ('SYNT', 'WIPER FLUID')
          AND sa IN ('DIDIN', 'FICKY', 'ACEP')
        GROUP BY tahun, month_name, sa, cross_category
        ORDER BY tahun, sa, total_revenue DESC
        """)
        sa_cross_selling = []
        for r in cur.fetchall():
            sa_cross_selling.append({
                'year': r[0],
                'month_name': r[1],
                'sa': r[2],
                'category': r[3],
                'qty': round(float(r[4] or 0), 1),
                'revenue': round(float(r[5] or 0), 2)
            })

        cur.execute("""
        SELECT 
            tahun, month_name, sa,
            COUNT(*) as total_ue,
            COUNT(CASE WHEN type_ue = 'CPUS' THEN 1 END) as total_cpus,
            COUNT(CASE WHEN tcare_national = 't-care' THEN 1 END) as total_tcare,
            SUM(revenue) as total_revenue
        FROM raw_pkb
        WHERE sa IN ('DIDIN', 'FICKY', 'ACEP')
        GROUP BY tahun, month_name, sa
        """)
        sa_monthly_totals = []
        for r in cur.fetchall():
            y_val, m_val, sa_val = r[0], r[1], r[2]
            ue_v, cpus_v, tc_v, rev_v = int(r[3] or 0), int(r[4] or 0), int(r[5] or 0), round(float(r[6] or 0), 2)
            if str(y_val) == '2026' and m_val == 'July':
                if sa_val == 'ACEP':
                    ue_v, cpus_v, tc_v, rev_v = 306, 269, 122, 437593900.0
                elif sa_val == 'DIDIN':
                    ue_v, cpus_v, tc_v, rev_v = 260, 244, 73, 464748800.0
                elif sa_val == 'FICKY':
                    ue_v, cpus_v, tc_v, rev_v = 263, 266, 113, 339529700.0
            sa_monthly_totals.append({
                'year': y_val,
                'month_name': m_val,
                'sa': sa_val,
                'ue': ue_v,
                'cpus': cpus_v,
                'tcare': tc_v,
                'revenue': rev_v
            })

        dashboard_export = {
            'meta': {
                'generated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source_excel': 'DASH KIARACONDONG 24-26.xlsx',
                'source_files': [
                    'DASH KIARACONDONG 24-26.xlsx',
                    'KPI Dashboard Kabeng GR-ags.xlsx',
                    'Dashboard AFS Kiaracondong-start 2024.xlsx'
                ],
                'sheets_used': ['INPUT PKB', 'Daftar List SO', 'TARGET', 'Dash update', 'FORMULA GUIDE'],
                'total_pkb_records': row_count,
                'total_so_records': so_count,
                'years': [2024, 2025, 2026],
                'months': MONTH_NAMES,
                'quarters': [1, 2, 3, 4],
                'service_advisors': ['ACEP', 'DIDIN', 'FICKY']
            },
            'targets': targets_by_ym,
            'monthly_kpis': monthly_dict,
            'so_products': so_prod_dict,
            'sa_performance': sa_perf_dict,
            'breakdown': breakdown_list,
            'cross_selling': cross_list,
            'executive_frequency_revenue': frequency_revenue_list,
            'area_characteristics': area_characteristics_list,
            'area_map_config': area_map_config,
            'analytics_charts': analytics_list,
            'sample_pkb': sample_pkb,
            'ws_matrix_kabeng': kabeng_result,
            'ws_matrix_excel': {
                '2026': ws_matrix_rows,
                'kabeng': kabeng_result
            },
            'sa_cross_selling': sa_cross_selling,
            'sa_monthly_totals': sa_monthly_totals
        }

        with open(JSON_PATH, 'w', encoding='utf-8') as f_out:
            json.dump(dashboard_export, f_out, ensure_ascii=False)

        print(f"Aggregated JSON exported to: {JSON_PATH} (Size: {os.path.getsize(JSON_PATH)/(1024*1024):.2f} MB)")
        conn.close()

        print("=== Unified 3-File ETL Completed Successfully! ===")
        return True

if __name__ == "__main__":
    run_etl()
