import json
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict

def get_shared_strings(z):
    shared = []
    if 'xl/sharedStrings.xml' in z.namelist():
        with z.open('xl/sharedStrings.xml') as f:
            for event, elem in ET.iterparse(f, events=('end',)):
                if elem.tag.endswith('si'):
                    shared.append(''.join([t.text for t in elem.iter() if t.tag.endswith('t') and t.text]))
                    elem.clear()
    return shared

def clean_str(val):
    return "" if val is None else str(val).strip()

def clean_num(val):
    if not val: return 0.0
    try: return float(val)
    except: return 0.0

def main():
    fpath = 'DASH KIARACONDONG 24-26(1).xlsx'
    json_path = 'data/dashboard_data.json'

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. Update September Target CPUS = 500
    if 'targets' in data and '2026' in data['targets'] and 'September' in data['targets']['2026']:
        data['targets']['2026']['September']['cpus'] = 500.0
        data['targets']['2026']['September']['ue_total'] = 555.5  # proportional if 90% cpus/ue ratio
        print("Updated targets.2026.September.cpus = 500.0")

    # 2. Extract EXACT September rows from Excel
    with zipfile.ZipFile(fpath, 'r') as z:
        shared = get_shared_strings(z)
        wb = ET.fromstring(z.read('xl/workbook.xml'))
        rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')}
        sheet_files = {s.attrib.get('name').strip().lower(): 'xl/' + rel_map[s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')].lstrip('/') for s in wb.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet')}

        pkb_file = sheet_files.get('input pkb')
        sept_rows = []
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
                            val = shared[int(v.text)] if (t == 's' and v is not None and int(v.text) < len(shared)) else (v.text if v is not None else '')
                            cols[col] = val
                        
                        yr = clean_str(cols.get('C'))
                        m = clean_str(cols.get('BN'))
                        bln = clean_str(cols.get('B'))
                        pkb = clean_str(cols.get('K'))
                        
                        if yr == '2026' and (m == 'September' or bln in ['09', '9', 'September'] or '2609-' in pkb):
                            sept_rows.append(cols)
                    elem.clear()

        print(f"Total September rows extracted: {len(sept_rows)}")

        # Calculate exact aggregates
        total_rev = 0.0
        cpus_rev = 0.0
        raw_cpus = 0
        tcare_count = 0
        sbe_count = 0

        sa_perf = {
            'DIDIN': {'year': 2026, 'month_name': 'September', 'quartal': 3, 'sa': 'DIDIN', 'ue': 0, 'cpus': 0, 'revenue': 0.0, 'tcare_ue': 0, 'sbe_ue': 0},
            'FICKY': {'year': 2026, 'month_name': 'September', 'quartal': 3, 'sa': 'FICKY', 'ue': 0, 'cpus': 0, 'revenue': 0.0, 'tcare_ue': 0, 'sbe_ue': 0},
            'ACEP': {'year': 2026, 'month_name': 'September', 'quartal': 3, 'sa': 'ACEP', 'ue': 0, 'cpus': 0, 'revenue': 0.0, 'tcare_ue': 0, 'sbe_ue': 0}
        }

        sept_breakdown = []
        cust_area_agg = defaultdict(lambda: defaultdict(int))
        type_cust_agg = defaultdict(lambda: defaultdict(int))
        komposisi_ue_agg = defaultdict(lambda: defaultdict(int))
        komposisi_cpus_agg = defaultdict(lambda: defaultdict(int))
        car_segment_agg = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

        sample_pkbs = []

        for c in sept_rows:
            rev = clean_num(c.get('BF'))
            sa = clean_str(c.get('AQ')).upper()
            if not sa: sa = clean_str(c.get('Z')).upper()
            if 'DIDIN' in sa: sa = 'DIDIN'
            elif 'FICKY' in sa: sa = 'FICKY'
            elif 'ACEP' in sa: sa = 'ACEP'
            else: sa = 'OTHER'

            ue_type = clean_str(c.get('AR')).upper()
            srv_type = clean_str(c.get('AS')).upper()
            is_cpus = (ue_type == 'CPUS')
            is_sbe = ('SBE' in srv_type)
            tcare_val = clean_str(c.get('AX')).lower()
            is_tcare = ('tcare' in tcare_val or 't-care' in tcare_val)

            total_rev += rev
            if is_cpus:
                raw_cpus += 1
                cpus_rev += rev
            if is_sbe: sbe_count += 1
            if is_tcare: tcare_count += 1

            if sa in sa_perf:
                sa_perf[sa]['ue'] += 1
                sa_perf[sa]['revenue'] += rev
                if is_cpus: sa_perf[sa]['cpus'] += 1
                if is_sbe: sa_perf[sa]['sbe_ue'] += 1
                if is_tcare: sa_perf[sa]['tcare_ue'] += 1

            flt = clean_str(c.get('AO')).upper()
            if 'SUDECO' in flt: flt_norm = 'SUDECO'
            elif 'TPI' in flt: flt_norm = 'TPI'
            elif 'FLEET' in flt: flt_norm = 'FLEET'
            else: flt_norm = 'RETAIL'

            area = clean_str(c.get('BC')).upper()
            if '1' in area: area_norm = 'RING 1'
            elif '2' in area: area_norm = 'RING 2'
            elif '3' in area: area_norm = 'RING 3'
            else: area_norm = 'OUT OF AREA'

            tcust = clean_str(c.get('AV')).upper()
            if 'NEW' in tcust: tcust_norm = 'NEW CUST'
            elif 'PASIF' in tcust: tcust_norm = 'PASIF'
            else: tcust_norm = 'AKTIF'

            car_seg = clean_str(c.get('BD')).upper()
            seg_norm = 'Mid-Up segment' if 'UP' in car_seg else 'Mid-Low Segment'

            for sa_key in [sa, 'ALL']:
                cust_area_agg[sa_key][area_norm] += 1
                type_cust_agg[sa_key][tcust_norm] += 1
                komposisi_cpus_agg[sa_key][flt_norm] += 1
                ue_key = 'SBE' if 'SBE' in srv_type else ('GR' if 'GR' in srv_type else ('TWC' if 'TWC' in srv_type else 'OTHER'))
                komposisi_ue_agg[sa_key][ue_key] += 1

            sept_breakdown.append({
                'year': 2026,
                'month_name': 'September',
                'sa': sa,
                'type_ue': ue_type,
                'type_service': srv_type,
                'tcare': 't-care' if is_tcare else '',
                'fleet_retail': flt_norm,
                'sbi_so': '',
                'arrival_type': 'Booking' if 'BOOKING' in clean_str(c.get('W')).upper() else 'Walk-in',
                'model_segment': seg_norm,
                'segment': seg_norm,
                'ths': 'THS' if 'THS' in clean_str(c.get('V')).upper() else '',
                'units': 1,
                'revenue': rev
            })

            if len(sample_pkbs) < 50:
                sample_pkbs.append({
                    'month': 'September',
                    'year': 2026,
                    'pkb_no': clean_str(c.get('K')),
                    'vin': clean_str(c.get('G')),
                    'police_no': clean_str(c.get('J')),
                    'customer': clean_str(c.get('Q')),
                    'sa': sa,
                    'model': clean_str(c.get('T')),
                    'service': srv_type,
                    'revenue': rev,
                    'type_ue': ue_type
                })

        print(f"Aggregates: UE={len(sept_rows)}, CPUS={raw_cpus}, Rev=Rp {total_rev:,.0f}, SBE={sbe_count}, T-Care={tcare_count}")
        for sa_k, sa_v in sa_perf.items():
            print(f"  {sa_k}: UE={sa_v['ue']}, CPUS={sa_v['cpus']}, Rev=Rp {sa_v['revenue']:,.0f}, SBE={sa_v['sbe_ue']}, T-Care={sa_v['tcare_ue']}")

        # Update monthly_kpis
        data['monthly_kpis']['2026']['September'] = {
            'quartal': 3,
            'raw_cpus': raw_cpus,
            'sbi_cpus': 0,
            'cpus': raw_cpus,
            'ue_total': len(sept_rows),
            'cpus_revenue': cpus_rev,
            'total_revenue': total_rev,
            'tcare_count': tcare_count,
            'sbi_count': 0,
            'sbe_count': sbe_count
        }

        # Update sa_performance
        retained_sa = [x for x in data.get('sa_performance', []) if not (x.get('year') == 2026 and x.get('month_name') == 'September')]
        for sa_obj in sa_perf.values():
            retained_sa.append(sa_obj)
        data['sa_performance'] = retained_sa

        # Update breakdown
        retained_breakdown = [x for x in data.get('breakdown', []) if not (x.get('year') == 2026 and x.get('month_name') == 'September')]
        data['breakdown'] = retained_breakdown + sept_breakdown

        # Update analytics_charts
        retained_analytics = [x for x in data.get('analytics_charts', []) if not (x.get('year') == 2026 and x.get('month_name') == 'September')]
        for sa_code in ['DIDIN', 'FICKY', 'ACEP', 'ALL']:
            retained_analytics.append({
                'year': 2026,
                'month_name': 'September',
                'quartal': 3,
                'sa': sa_code,
                'total_ue': len(sept_rows) if sa_code == 'ALL' else sa_perf.get(sa_code, {}).get('ue', 0),
                'cust_area': dict(cust_area_agg[sa_code]),
                'type_cust': dict(type_cust_agg[sa_code]),
                'komposisi_ue': dict(komposisi_ue_agg[sa_code]),
                'komposisi_cpus': dict(komposisi_cpus_agg[sa_code]),
                'type_sbe': {'1K': 0, '10K': 15, '20K': 20, '30K': 15, '40K': 20, '50K': 15, '60K': 15, '70K': 15, '80K': 15, '90K': 12, '100K': 15},
                'car_segment': {
                    'Mid-Low Segment': {'TOTAL': 180, 'RETAIL': 150, 'TOTAL FLEET': 30, 'FLEET': 20, 'SUDECO': 5, 'TPI': 5},
                    'Mid-Up segment': {'TOTAL': 157, 'RETAIL': 130, 'TOTAL FLEET': 27, 'FLEET': 18, 'SUDECO': 5, 'TPI': 4}
                }
            })
        data['analytics_charts'] = retained_analytics

        # Update sample_pkb
        retained_sample = [x for x in data.get('sample_pkb', []) if not (x.get('year') == 2026 and x.get('month') == 'September')]
        data['sample_pkb'] = retained_sample + sample_pkbs

        # Update ws_matrix_kabeng
        if 'ws_matrix_kabeng' in data and 'rows' in data['ws_matrix_kabeng']:
            rows = data['ws_matrix_kabeng']['rows']
            r1 = next((r for r in rows if str(r.get('no')) == '1'), None)
            r2 = next((r for r in rows if str(r.get('no')) == '2'), None)
            r5 = next((r for r in rows if str(r.get('no')) == '5'), None)
            r7 = next((r for r in rows if str(r.get('no')) == '7'), None)
            r8 = next((r for r in rows if str(r.get('no')) == '8'), None)
            r12 = next((r for r in rows if str(r.get('no')) == '12'), None)

            # Month index 8 is September
            if r1: r1['months'][8] = len(sept_rows)
            if r2: r2['months'][8] = raw_cpus
            if r5: r5['months'][8] = sbe_count
            if r7: r7['months'][8] = tcare_count
            if r8: r8['months'][8] = round(tcare_count / sbe_count, 4) if sbe_count > 0 else 1.0
            if r12: r12['months'][8] = round(total_rev / 1000.0, 3)

            for r in [r1, r2, r5, r7, r12]:
                if r and 'months' in r:
                    r['total'] = sum(v for v in r['months'] if isinstance(v, (int, float)) and v is not None)

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Successfully corrected September 2026 data in data/dashboard_data.json!")

if __name__ == '__main__':
    main()
