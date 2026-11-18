import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
import json

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

def main():
    fpath = 'DASH KIARACONDONG 24-26.xlsx'
    print(f"Reading ATTACKLIST from {fpath}...")
    with zipfile.ZipFile(fpath, 'r') as z:
        shared = get_shared_strings(z)
        wb = ET.fromstring(z.read('xl/workbook.xml'))
        rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        rel_map = {r.attrib['Id']: r.attrib['Target'] for r in rels.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')}
        sheet_files = {s.attrib.get('name'): 'xl/' + rel_map[s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')].lstrip('/') for s in wb.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet')}

        serial_month_map = {
            '46048': 'Jan', '46079': 'Feb', '46107': 'Mar',
            '46138': 'Apr', 'mei': 'Mei', 'may': 'Mei',
            '46199': 'Jun', '46229': 'Jul', 'agu': 'Agt', 'aug': 'Agt',
            '46266': 'Sep', 'jan': 'Jan', 'feb': 'Feb', 'mar': 'Mar', 'apr': 'Apr', 'jun': 'Jun', 'jul': 'Jul', 'sep': 'Sep'
        }

        ring_monthly = defaultdict(lambda: defaultdict(lambda: {'cust_fu': 0, 'connected': 0}))
        fleet_monthly = defaultdict(lambda: defaultdict(lambda: {'cust_fu': 0, 'connected': 0}))

        row_idx = 0
        for event, elem in ET.iterparse(z.open(sheet_files['ATTACKLIST'])):
            if elem.tag.endswith('row'):
                row_idx += 1
                if row_idx > 1:
                    cols = {}
                    for c in elem.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                        ref = c.attrib.get('r')
                        col = ''.join([ch for ch in ref if ch.isalpha()])
                        t = c.attrib.get('t')
                        v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                        val = shared[int(v.text)] if (t == 's' and v is not None and int(v.text) < len(shared)) else (v.text if v is not None else '')
                        cols[col] = val

                    is_cust_fu = ('cust fu' in clean_str(cols.get('B')).lower() or True)
                    is_connected = ('connected' in clean_str(cols.get('C')).lower())

                    # Identify month from Col P (Bulan) or Col AN (Tgl FU)
                    p_raw = clean_str(cols.get('P')).lower()
                    m_key = None
                    for k, v in serial_month_map.items():
                        if k in p_raw:
                            m_key = v
                            break

                    if not m_key:
                        an_raw = clean_str(cols.get('AN')).lower()
                        for k, v in serial_month_map.items():
                            if k in an_raw:
                                m_key = v
                                break

                    if not m_key:
                        continue

                    # Ring Area from Col AB
                    area_raw = clean_str(cols.get('AB')).upper()
                    if '1' in area_raw: area = 'Ring 1'
                    elif '2' in area_raw: area = 'Ring 2'
                    elif '3' in area_raw: area = 'Ring 3'
                    else: area = 'Out of Area'

                    # Fleet / Retail from Col AC
                    flt_raw = clean_str(cols.get('AC')).upper()
                    if 'FLEET' in flt_raw or 'SUDECO' in flt_raw or 'TPI' in flt_raw:
                        flt = 'Fleet'
                    else:
                        flt = 'Retail'

                    ring_monthly[m_key][area]['cust_fu'] += 1
                    if is_connected: ring_monthly[m_key][area]['connected'] += 1

                    fleet_monthly[m_key][flt]['cust_fu'] += 1
                    if is_connected: fleet_monthly[m_key][flt]['connected'] += 1

                elem.clear()

        print("Finished parsing ATTACKLIST rows!")
        months_order = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agt', 'Sep']
        for m in months_order:
            print(f"Month {m}:")
            for a in ['Ring 1', 'Ring 2', 'Ring 3', 'Out of Area']:
                c_fu = ring_monthly[m][a]['cust_fu']
                c_con = ring_monthly[m][a]['connected']
                pct = (c_con / c_fu * 100) if c_fu > 0 else 0
                print(f"  {a:11s}: Cust FU={c_fu:4d}, Connected={c_con:4d} ({pct:.1f}%)")
            for f in ['Retail', 'Fleet']:
                c_fu = fleet_monthly[m][f]['cust_fu']
                c_con = fleet_monthly[m][f]['connected']
                pct = (c_con / c_fu * 100) if c_fu > 0 else 0
                print(f"  {f:11s}: Cust FU={c_fu:4d}, Connected={c_con:4d} ({pct:.1f}%)")

        with open('data/funnelling_data.json', 'r', encoding='utf-8') as fj:
            funnel_json = json.load(fj)

        funnel_json['monthly_ring_area_trend'] = ring_monthly
        funnel_json['monthly_fleet_retail_trend'] = fleet_monthly

        with open('data/funnelling_data.json', 'w', encoding='utf-8') as fj:
            json.dump(funnel_json, fj, ensure_ascii=False, indent=2)

        print("Saved complete 9-month trends to data/funnelling_data.json!")

if __name__ == '__main__':
    main()
