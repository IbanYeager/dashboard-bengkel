import os
import json
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict

def get_shared_strings(z):
    shared_strings = []
    if 'xl/sharedStrings.xml' in z.namelist():
        print("Parsing sharedStrings.xml...")
        with z.open('xl/sharedStrings.xml') as f:
            for event, elem in ET.iterparse(f, events=('end',)):
                if elem.tag.endswith('si'):
                    text = ''.join([t.text for t in elem.iter() if t.tag.endswith('t') and t.text])
                    shared_strings.append(text)
                    elem.clear()
    return shared_strings

def clean_str(val):
    if val is None:
        return ""
    return str(val).strip()

def clean_num(val):
    if val is None or val == "":
        return 0.0
    try:
        return float(val)
    except:
        return 0.0

def normalize_ring_area(val):
    v = clean_str(val).upper()
    if 'RING 1' in v or 'AREA 1' in v: return 'RING 1'
    if 'RING 2' in v or 'AREA 2' in v: return 'RING 2'
    if 'RING 3' in v or 'AREA 3' in v: return 'RING 3'
    return 'OUT OF AREA'

def normalize_type_cust(val):
    v = clean_str(val).upper()
    if 'AKTIF' in v: return 'AKTIF'
    if 'NEW CUST' in v: return 'NEW CUST'
    if 'PASIF' in v or 'INACTIVE' in v: return 'PASIF'
    return 'AKTIF' if v else 'UNKNOWN'

def normalize_type_service(srv, ue):
    s = clean_str(srv).upper()
    u = clean_str(ue).upper()
    if 'SBE' in s: return 'SBE'
    if 'GR OIL' in s: return 'GR OIL'
    if 'GR' in s: return 'GR OTHER'
    if 'TWC' in s or 'TWC' in u: return 'TWC'
    if 'SBI' in s or 'SBI' in u: return 'SBI'
    return 'OTHER'

def map_sbe_km(lookup_job, type_service):
    j = clean_str(lookup_job).upper()
    s = clean_str(type_service).upper()
    if 'SBE' not in s and 'SBI' not in s and j not in ['1K', '5K LOW', '10K', '20K', '30K', '40K', '50K', '60K', '70K', '80K', '90K', '100K']:
        return None
    if j in ['1K', '5K LOW'] or s == 'SBI': return '1K'
    if j == '10K': return '10K'
    if j in ['20K', '30K', '40K', '50K', '60K', '70K', '80K', '90K', '100K']: return j
    if 'SBE' in s: return '100K UP'
    return None

def normalize_fleet_retail(val):
    v = clean_str(val).upper()
    if 'SUDECO' in v: return 'SUDECO'
    if 'TPI' in v: return 'TPI'
    if 'FLEET' in v: return 'FLEET'
    return 'RETAIL'

def normalize_model_segment(val):
    v = clean_str(val).upper()
    if 'UP' in v: return 'Mid-Up segment'
    return 'Mid-Low Segment'

def get_rev_tier(rev):
    if rev < 500000: return '< Rp.500K'
    if rev < 1000000: return 'Rp.500K s/d Rp.1Jt'
    if rev < 1500000: return 'Rp.1Jt s/d Rp.1,5Jt'
    if rev < 2000000: return 'Rp.1,5Jt s/d Rp.2Jt'
    return '> Rp.2Jt'

def main():
    fpath = 'DASH KIARACONDONG 24-26(1).xlsx'
    json_path = 'data/dashboard_data.json'
    
    print(f"Loading existing dashboard data from {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        dashboard_data = json.load(f)

    # 1. Inspect existing 2026 data
    existing_months_2026 = list(dashboard_data.get('monthly_kpis', {}).get('2026', {}).keys())
    print(f"Existing 2026 months in dashboard: {existing_months_2026}")

    # 2. Extract shared strings and sheets
    print(f"Opening {fpath}...")
    with zipfile.ZipFile(fpath, 'r') as z:
        shared_strings = get_shared_strings(z)
        print(f"Total shared strings: {len(shared_strings)}")
        
        wb_root = ET.fromstring(z.read('xl/workbook.xml'))
        rels_root = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels_root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')}
        sheet_files = {s.attrib.get('name').strip().lower(): 'xl/' + rel_map[s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')].lstrip('/') for s in wb_root.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet')}

        # -------------------------------------------------------------
        # Extract September PKB rows
        # -------------------------------------------------------------
        pkb_file = sheet_files.get('input pkb')
        if not pkb_file:
            print("Error: INPUT PKB sheet not found!")
            return

        print(f"Extracting September PKB rows from {pkb_file}...")
        sept_pkb_rows = []
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
                            sept_pkb_rows.append(cols)
                    elem.clear()

        print(f"Extracted {len(sept_pkb_rows)} September PKB rows.")
        if not sept_pkb_rows:
            print("No September rows found.")
            return

        # -------------------------------------------------------------
        # Aggregate September 2026 PKB data
        # -------------------------------------------------------------
        total_rev = 0.0
        cpus_rev = 0.0
        raw_cpus = 0
        tcare_count = 0
        sbi_count = 0
        sbe_count = 0

        sa_perf_map = {}
        for sa_name in ['DIDIN', 'FICKY', 'ACEP']:
            sa_perf_map[sa_name] = {
                'year': 2026, 'month_name': 'September', 'quartal': 3,
                'sa': sa_name, 'ue': 0, 'cpus': 0, 'revenue': 0.0,
                'tcare_ue': 0, 'sbe_ue': 0
            }

        new_breakdown = []
        analytics_agg = {}
        area_agg = {}

        for cols in sept_pkb_rows:
            pkb_no = clean_str(cols.get('K'))
            vin = clean_str(cols.get('G'))
            police_no = clean_str(cols.get('J'))
            cust_name = clean_str(cols.get('Q'))
            
            sa = clean_str(cols.get('AQ'))
            if not sa: sa = clean_str(cols.get('Z'))
            sa = sa.upper()

            ue = clean_str(cols.get('AR')).upper()
            srv = clean_str(cols.get('AS')).upper()
            srv_norm = normalize_type_service(srv, ue)
            tcare = clean_str(cols.get('AX')).lower()
            flt = normalize_fleet_retail(cols.get('AO'))
            rev = clean_num(cols.get('BF'))
            lookup_job = clean_str(cols.get('H')).upper()
            sbe_cat = map_sbe_km(lookup_job, srv)
            type_cust = normalize_type_cust(cols.get('AV'))
            ring_area = normalize_ring_area(cols.get('BC'))
            seg = normalize_model_segment(cols.get('BD'))
            arrival = clean_str(cols.get('W')).upper()
            is_booking = 'BOOKING' in arrival
            ths = clean_str(cols.get('V')).upper()
            is_ths = 'THS' in ths
            sbi_so = clean_str(cols.get('DI')).lower()
            if not sbi_so: sbi_so = clean_str(cols.get('AU')).lower()

            is_cpus = (ue == 'CPUS')
            is_tcare = ('tcare' in tcare or 't-care' in tcare)
            is_sbe = (srv_norm == 'SBE' or 'SBE' in srv)

            total_rev += rev
            if is_cpus:
                raw_cpus += 1
                cpus_rev += rev
            if is_tcare: tcare_count += 1
            if is_sbe: sbe_count += 1
            if 'sbi so' in sbi_so or srv == 'SBI': sbi_count += 1

            # SA Performance
            if sa in sa_perf_map:
                sa_perf_map[sa]['ue'] += 1
                sa_perf_map[sa]['revenue'] += rev
                if is_cpus: sa_perf_map[sa]['cpus'] += 1
                if is_tcare: sa_perf_map[sa]['tcare_ue'] += 1
                if is_sbe: sa_perf_map[sa]['sbe_ue'] += 1

            # Breakdown
            new_breakdown.append({
                'year': 2026,
                'month_name': 'September',
                'sa': sa,
                'type_ue': ue,
                'type_service': srv_norm,
                'tcare': 't-care' if is_tcare else tcare,
                'fleet_retail': flt,
                'sbi_so': sbi_so,
                'arrival_type': 'BOOKING' if is_booking else arrival,
                'model_segment': seg,
                'segment': seg,
                'ths': 'THS' if is_ths else '',
                'units': 1,
                'revenue': rev
            })

            # Analytics Aggregation
            target_sa_keys = [sa if sa in ['DIDIN', 'FICKY', 'ACEP'] else 'OTHER', 'ALL']
            for sa_code in target_sa_keys:
                agg_key = f"2026-September-3-{sa_code}"
                if agg_key not in analytics_agg:
                    analytics_agg[agg_key] = {
                        'year': 2026, 'month_name': 'September', 'quartal': 3, 'sa': sa_code, 'total_ue': 0,
                        'cust_area': { 'RING 1': 0, 'RING 2': 0, 'RING 3': 0, 'OUT OF AREA': 0 },
                        'type_cust': { 'AKTIF': 0, 'PASIF': 0, 'NEW CUST': 0 },
                        'komposisi_ue': { 'SBE': 0, 'GR': 0, 'GR OIL': 0, 'TWC': 0, 'SBI': 0 },
                        'type_sbe': {
                            '1K': 0, '10K': 0, '20K': 0, '30K': 0, '40K': 0, '50K': 0,
                            '60K': 0, '70K': 0, '80K': 0, '90K': 0, '100K': 0, '100K UP': 0
                        },
                        'komposisi_cpus': { 'RETAIL': 0, 'FLEET': 0, 'SUDECO': 0, 'TPI': 0 },
                        'car_segment': {
                            'Mid-Low Segment': { 'TOTAL': 0, 'RETAIL': 0, 'TOTAL FLEET': 0, 'FLEET': 0, 'SUDECO': 0, 'TPI': 0 },
                            'Mid-Up segment': { 'TOTAL': 0, 'RETAIL': 0, 'TOTAL FLEET': 0, 'FLEET': 0, 'SUDECO': 0, 'TPI': 0 }
                        }
                    }
                a_obj = analytics_agg[agg_key]
                a_obj['total_ue'] += 1
                if ring_area in a_obj['cust_area']: a_obj['cust_area'][ring_area] += 1
                if type_cust in a_obj['type_cust']: a_obj['type_cust'][type_cust] += 1
                comp_key = 'GR' if srv_norm == 'GR OTHER' else srv_norm
                if comp_key in a_obj['komposisi_ue']: a_obj['komposisi_ue'][comp_key] += 1
                if sbe_cat and sbe_cat in a_obj['type_sbe']: a_obj['type_sbe'][sbe_cat] += 1
                if is_cpus and flt in a_obj['komposisi_cpus']: a_obj['komposisi_cpus'][flt] += 1
                if seg in a_obj['car_segment']:
                    a_obj['car_segment'][seg]['TOTAL'] += 1
                    if flt in a_obj['car_segment'][seg]: a_obj['car_segment'][seg][flt] += 1
                    if flt in ['FLEET', 'SUDECO', 'TPI']: a_obj['car_segment'][seg]['TOTAL FLEET'] += 1

            # Area Aggregation
            for sa_code in target_sa_keys:
                area_key = f"2026-September-3-{sa_code}-{ring_area}"
                if area_key not in area_agg:
                    area_agg[area_key] = {
                        'year': 2026, 'month_name': 'September', 'quartal': 3, 'sa': sa_code, 'ring_area': ring_area,
                        'total_ue': 0, 'total_revenue': 0.0, 'total_cpus': 0,
                        'sa_cpus': { 'DIDIN': 0, 'FICKY': 0, 'ACEP': 0 },
                        'type_cust': { 'RETAIL': 0, 'FLEET': 0, 'SUDECO': 0, 'TPI': 0 },
                        'type_service': { 'SBE': 0, 'GR OTHER': 0, 'GR OIL': 0, 'TWC': 0, 'SBI': 0 },
                        'model_segment': { 'Mid-Up segment': 0, 'Mid-Low Segment': 0 },
                        'range_revenue': { '< Rp.500K': 0, 'Rp.500K s/d Rp.1Jt': 0, 'Rp.1Jt s/d Rp.1,5Jt': 0, 'Rp.1,5Jt s/d Rp.2Jt': 0, '> Rp.2Jt': 0 },
                        'ths_count': 0, 'booking_count': 0,
                        'qty_gr_status': { '< 3': 0, '>= 3 <= 5': 0, '>= 5 <= 10': 0, '> 10': 0 },
                        'qty_sbe_status': { '< 3': 0, '>= 3 <= 5': 0, '>= 5 <= 10': 0, '> 10': 0 }
                    }
                ar_obj = area_agg[area_key]
                ar_obj['total_ue'] += 1
                ar_obj['total_revenue'] += rev
                if is_cpus:
                    ar_obj['total_cpus'] += 1
                    if sa in ar_obj['sa_cpus']: ar_obj['sa_cpus'][sa] += 1
                if flt in ar_obj['type_cust']: ar_obj['type_cust'][flt] += 1
                if srv_norm in ar_obj['type_service']: ar_obj['type_service'][srv_norm] += 1
                if seg in ar_obj['model_segment']: ar_obj['model_segment'][seg] += 1
                r_tier = get_rev_tier(rev)
                if r_tier in ar_obj['range_revenue']: ar_obj['range_revenue'][r_tier] += 1
                if is_ths: ar_obj['ths_count'] += 1
                if is_booking: ar_obj['booking_count'] += 1

        # -------------------------------------------------------------
        # Extract September SO rows
        # -------------------------------------------------------------
        so_file = sheet_files.get('daftar list so')
        sept_so_rows = []
        new_sa_cross = []
        new_ws_cross = defaultdict(lambda: { 'year': 2026, 'month_name': 'September', 'category': '', 'qty': 0, 'revenue': 0.0 })

        if so_file:
            print(f"Extracting September SO rows from {so_file}...")
            with z.open(so_file) as sf:
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
                            bln = clean_str(cols.get('B'))
                            if yr == '2026' and bln in ['09', '9', 'September']:
                                sept_so_rows.append(cols)
                                sa = clean_str(cols.get('AQ') or cols.get('Z')).upper()
                                cat = clean_str(cols.get('AD') or cols.get('H') or 'LAINNYA').upper()
                                qty = clean_num(cols.get('BF') or 1)
                                amt = clean_num(cols.get('BG') or cols.get('BF'))
                                if sa in ['DIDIN', 'FICKY', 'ACEP'] and cat:
                                    new_sa_cross.append({
                                        'year': 2026, 'month_name': 'September', 'sa': sa,
                                        'category': cat, 'qty': qty, 'revenue': amt
                                    })
                                ws_key = f"2026-September-{cat}"
                                new_ws_cross[ws_key]['category'] = cat
                                new_ws_cross[ws_key]['qty'] += qty
                                new_ws_cross[ws_key]['revenue'] += amt
                        elem.clear()

        print(f"Extracted {len(sept_so_rows)} September SO rows.")

    # -------------------------------------------------------------
    # 3. NON-DESTRUCTIVELY MERGE INTO DASHBOARD_DATA
    # -------------------------------------------------------------
    # (A) Monthly KPIs: Only add September, preserve Jan-Aug!
    sbi_add = dashboard_data.get('targets', {}).get('2026', {}).get('September', {}).get('sbi_cpus', 0)
    dashboard_data['monthly_kpis']['2026']['September'] = {
        'quartal': 3,
        'raw_cpus': raw_cpus,
        'sbi_cpus': sbi_add,
        'cpus': raw_cpus + sbi_add,
        'ue_total': len(sept_pkb_rows),
        'cpus_revenue': cpus_rev,
        'total_revenue': total_rev,
        'tcare_count': tcare_count,
        'sbi_count': sbi_count,
        'sbe_count': sbe_count
    }
    print("Updated monthly_kpis['2026']['September']:", dashboard_data['monthly_kpis']['2026']['September'])

    # (B) SA Performance: Filter out any existing 2026 September, append new
    retained_sa_perf = [x for x in dashboard_data.get('sa_performance', []) if not (x.get('year') == 2026 and x.get('month_name') == 'September')]
    dashboard_data['sa_performance'] = retained_sa_perf + list(sa_perf_map.values())

    # (C) Breakdown: Filter out 2026 September, append new
    retained_breakdown = [x for x in dashboard_data.get('breakdown', []) if not (x.get('year') == 2026 and x.get('month_name') == 'September')]
    dashboard_data['breakdown'] = retained_breakdown + new_breakdown

    # (D) Analytics Charts: Filter out 2026 September, append new
    retained_analytics = [x for x in dashboard_data.get('analytics_charts', []) if not (x.get('year') == 2026 and x.get('month_name') == 'September')]
    dashboard_data['analytics_charts'] = retained_analytics + list(analytics_agg.values())

    # (E) Area Characteristics: Filter out 2026 September, append new
    retained_area = [x for x in dashboard_data.get('area_characteristics', []) if not (x.get('year') == 2026 and x.get('month_name') == 'September')]
    dashboard_data['area_characteristics'] = retained_area + list(area_agg.values())

    # (F) SO Cross-Selling
    if new_sa_cross:
        retained_sa_cross = [x for x in dashboard_data.get('sa_cross_selling', []) if not (x.get('year') == 2026 and x.get('month_name') == 'September')]
        dashboard_data['sa_cross_selling'] = retained_sa_cross + new_sa_cross

    if new_ws_cross:
        retained_ws_cross = [x for x in dashboard_data.get('cross_selling', []) if not (x.get('year') == 2026 and x.get('month_name') == 'September')]
        dashboard_data['cross_selling'] = retained_ws_cross + list(new_ws_cross.values())

    # (G) Bridge to ws_matrix_kabeng
    if 'ws_matrix_kabeng' in dashboard_data and 'rows' in dashboard_data['ws_matrix_kabeng']:
        rows = dashboard_data['ws_matrix_kabeng']['rows']
        r1 = next((r for r in rows if str(r.get('no')) == '1'), None)
        r2 = next((r for r in rows if str(r.get('no')) == '2'), None)
        r5 = next((r for r in rows if str(r.get('no')) == '5'), None)
        r7 = next((r for r in rows if str(r.get('no')) == '7'), None)
        r8 = next((r for r in rows if str(r.get('no')) == '8'), None)
        r9 = next((r for r in rows if str(r.get('no')) == '9'), None)
        r12 = next((r for r in rows if str(r.get('no')) == '12'), None)

        # Index 8 is September
        if r1: r1['months'][8] = len(sept_pkb_rows)
        if r2: r2['months'][8] = raw_cpus + sbi_add
        if r5: r5['months'][8] = sbe_count
        if r7: r7['months'][8] = tcare_count
        if r8: r8['months'][8] = round(tcare_count / sbe_count, 4) if sbe_count > 0 else None
        if r9: r9['months'][8] = round((sbe_count - tcare_count) / sbe_count, 4) if sbe_count > 0 else None
        if r12: r12['months'][8] = round(total_rev / 1000.0, 3)

        for r in [r1, r2, r5, r7, r12]:
            if r and 'months' in r:
                r['total'] = sum(v for v in r['months'] if isinstance(v, (int, float)) and v is not None)

    # -------------------------------------------------------------
    # 4. WRITE TO DISK
    # -------------------------------------------------------------
    print("Writing updated data to data/dashboard_data.json...")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, ensure_ascii=False, indent=2)

    print("Successfully updated September 2026 data in data/dashboard_data.json!")
    print("Previous months (Jan-Aug 2026, 2025, 2024) are completely preserved.")

if __name__ == '__main__':
    main()
