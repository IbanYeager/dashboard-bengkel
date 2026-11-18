import csv
import json
from collections import defaultdict, Counter

month_map = {
    'Jan-26': 'Jan', 'Feb-26': 'Feb', 'Mar-26': 'Mar',
    'Apr-26': 'Apr', 'Jun-26': 'Jun', 'Jul-26': 'Jul', 'Sep-26': 'Sep'
}

months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agt', 'Sep']
q_map = {
    'Jan': 'Q1', 'Feb': 'Q1', 'Mar': 'Q1',
    'Apr': 'Q2', 'Mei': 'Q2', 'Jun': 'Q2',
    'Jul': 'Q3', 'Agt': 'Q3', 'Sep': 'Q3'
}

all_periods = ['all', 'Q1', 'Q2', 'Q3'] + months

# 1. Load existing funnelling_data.json
with open('data/funnelling_data.json', 'r', encoding='utf-8') as f:
    fdata = json.load(f)

# Priority Segments structures
p_data = defaultdict(lambda: defaultdict(Counter))
tcare_data = defaultdict(lambda: defaultdict(Counter))
booking_data = defaultdict(Counter)

with open('data/mra_raw_sheet.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    headers = next(reader)
    for r in reader:
        if not r or len(r) < 38: continue
        q = r[0].strip()
        k1 = r[1].strip()
        k2 = r[2].strip()
        k3 = r[3].strip()
        cai = r[4].strip()
        due = r[13].strip()
        bln_raw = r[15].strip()
        hasil_fu = r[37].strip()
        judge = r[8].strip().upper() if len(r) > 8 else ''
        asal = r[20].strip().upper() if len(r) > 20 else ''
        prospect = r[11].strip().upper() if len(r) > 11 else ''
        part_type = r[7].strip().upper() if len(r) > 7 else ''
        
        if bln_raw in month_map: m = month_map[bln_raw]
        elif q == '2' or '30/5/26' in due: m = 'Mei'
        elif q == '3' or 'Agu' in (r[39] if len(r)>39 else ''): m = 'Agt'
        else: m = 'Unknown'
        
        if m not in months: continue
        quarter = q_map[m]
        periods_for_row = [m, quarter, 'all']
        
        # --- Modul 3: Priority Segments ---
        group_key = None
        subgroup = None
        
        if 'EXPIRED SOON' in judge:
            group_key = 'p1'
            if 'ELIGIBLE' in judge and 'NOT' not in judge: subgroup = 'Expired soon - Eligible'
            elif 'NOT ELIGIBLE' in judge: subgroup = 'Expired soon - Not Eligible'
            elif 'NEVER' in judge: subgroup = 'Expired soon - Never claim'
            else: subgroup = 'Expired soon - Eligible'
        elif 'ACTIVE' in judge:
            group_key = 'p2'
            if 'ELIGIBLE' in judge and 'NOT' not in judge: subgroup = 'Active - Eligible'
            elif 'NOT ELIGIBLE' in judge: subgroup = 'Active - Not Eligible'
            elif 'NEVER' in judge: subgroup = 'Active - Never claim'
            else: subgroup = 'Active - Eligible'
        elif 'FINISH' in judge:
            group_key = 'p3'
            if 'ELIGIBLE' in judge and 'NOT' not in judge: subgroup = 'Finish - Eligible'
            elif 'NOT ELIGIBLE' in judge: subgroup = 'Finish - Not Eligible'
            else: subgroup = 'Finish - Eligible'
        elif 'EXPIRED' in judge:
            group_key = 'p4'
            if 'ELIGIBLE' in judge and 'NOT' not in judge: subgroup = 'Expired - Eligible'
            elif 'NOT ELIGIBLE' in judge: subgroup = 'Expired - Not Eligible'
            elif 'NEVER' in judge: subgroup = 'Expired - Never claim'
            else: subgroup = 'Expired - Eligible'
        elif 'CRT' in judge or '8TH' in judge:
            sub = prospect if prospect in ['HOT', 'Medium', 'MEDIUM', 'Low', 'LOW'] else 'Low'
            sub = sub.capitalize() if sub.upper() in ['HOT', 'MEDIUM', 'LOW'] else sub
            if sub.upper() == 'HOT': sub = 'HOT'
            elif sub.upper() == 'MEDIUM': sub = 'Medium'
            elif sub.upper() == 'LOW': sub = 'Low'
            
            if 'MERDEKA' in asal:
                group_key = 'p5'
                subgroup = sub
            else:
                group_key = 'p6'
                subgroup = sub
                
        if group_key and subgroup:
            for p in periods_for_row:
                p_data[p][(group_key, subgroup)]['potensi'] += 1
                if cai == 'CAI':
                    p_data[p][(group_key, subgroup)]['cai'] += 1
                    
        # --- Modul 4: T-Care Programs ---
        prog_key = None
        if part_type == 'T-CARE':
            prog_key = 't_care'
        elif 'LITE+' in part_type or 'LITE +' in part_type:
            prog_key = 't_care_lite_plus'
        elif 'LITE' in part_type:
            prog_key = 't_care_lite'
        else:
            prog_key = 'care_x'
            
        for p in periods_for_row:
            tcare_data[p][prog_key]['potency'] += 1
            if k1 == 'CUST FU': tcare_data[p][prog_key]['cust_fu'] += 1
            if k2 == 'CONNECTED': tcare_data[p][prog_key]['connected'] += 1
            if k3 == 'CONTACTED': tcare_data[p][prog_key]['contacted'] += 1
            if 'BOOKING' in hasil_fu.upper(): tcare_data[p][prog_key]['booking'] += 1
            if cai == 'CAI': tcare_data[p][prog_key]['cai'] += 1
            
        # --- Modul 5: Status Booking ---
        if 'BOOKING' in hasil_fu.upper():
            for p in periods_for_row:
                booking_data[p]['total_booking'] += 1
                if cai == 'CAI':
                    booking_data[p]['show_cai'] += 1
                else:
                    booking_data[p]['open_not_cai'] += 1

# Format Priority Segments per period
priority_config = [
    {
        'key': 'p1',
        'group': 'Priority 1',
        'subgroups_keys': ['Expired soon - Eligible', 'Expired soon - Not Eligible', 'Expired soon - Never claim'],
        'total_label': 'TOTAL EX SOON'
    },
    {
        'key': 'p2',
        'group': 'Priority 2',
        'subgroups_keys': ['Active - Eligible', 'Active - Not Eligible', 'Active - Never claim'],
        'total_label': 'TOTAL ACTIVE'
    },
    {
        'key': 'p3',
        'group': 'Priority 3',
        'subgroups_keys': ['Finish - Eligible', 'Finish - Not Eligible'],
        'total_label': 'TOTAL FINISH'
    },
    {
        'key': 'p4',
        'group': 'Priority 4',
        'subgroups_keys': ['Expired - Eligible', 'Expired - Not Eligible', 'Expired - Never claim'],
        'total_label': 'TOTAL EXPIRED'
    },
    {
        'key': 'p5',
        'group': 'Priority 5',
        'title': 'CRT > 8th Merdeka Motor (Pembelian Asal: MERDEKA MOTOR)',
        'subgroups_keys': ['HOT', 'Medium', 'Low'],
        'total_label': 'TOTAL CRT MERDEKA MOTOR'
    },
    {
        'key': 'p6',
        'group': 'Priority 6',
        'title': 'CRT > 8th All Penjualan (Pembelian Asal: Selain Merdeka Motor)',
        'subgroups_keys': ['HOT', 'Medium', 'Low'],
        'total_label': 'TOTAL CRT NON MERDEKA MOTOR'
    }
]

formatted_priority_by_period = {}
for p in all_periods:
    seg_list = []
    for cfg in priority_config:
        gkey = cfg['key']
        sub_list = []
        tot_pot = 0
        tot_cai = 0
        for skey in cfg['subgroups_keys']:
            pot = p_data[p][(gkey, skey)]['potensi']
            cai_val = p_data[p][(gkey, skey)]['cai']
            pct = round(cai_val / pot * 100, 1) if pot > 0 else 0.0
            sub_list.append({
                'label': skey,
                'potensi': pot,
                'cai': cai_val,
                'pct': pct
            })
            tot_pot += pot
            tot_cai += cai_val
        tot_pct = round(tot_cai / tot_pot * 100, 1) if tot_pot > 0 else 0.0
        
        seg_entry = {
            'group': cfg['group'],
            'subgroups': sub_list,
            'total_label': cfg['total_label'],
            'total_potensi': tot_pot,
            'total_cai': tot_cai,
            'total_pct': tot_pct
        }
        if 'title' in cfg:
            seg_entry['title'] = cfg['title']
        seg_list.append(seg_entry)
    formatted_priority_by_period[p] = seg_list

fdata['priority_segments_by_period'] = formatted_priority_by_period
fdata['priority_segments'] = formatted_priority_by_period['all']

# Format T-Care Programs per period
formatted_tcare_by_period = {}
prog_titles = {
    't_care': 'I. T-CARE',
    't_care_lite_plus': 'II. T-CARE Lite +',
    't_care_lite': 'III. T-CARE Lite',
    'care_x': 'IV. Potensi CARE-X'
}
for p in all_periods:
    progs = {}
    for k, title in prog_titles.items():
        v = tcare_data[p][k]
        progs[k] = {
            'title': title,
            'potency': v['potency'],
            'cust_fu': v['cust_fu'],
            'connected': v['connected'],
            'contacted': v['contacted'],
            'booking': v['booking'],
            'cai': v['cai']
        }
    formatted_tcare_by_period[p] = progs

fdata['potensi_by_program_by_period'] = formatted_tcare_by_period
fdata['potensi_by_program'] = formatted_tcare_by_period['all']

# Format Status Booking per period
formatted_booking_by_period = {}
for p in all_periods:
    b = booking_data[p]
    tot = b['total_booking']
    cai_val = b['show_cai']
    open_val = b['open_not_cai']
    cai_pct = round(cai_val / tot * 100, 1) if tot > 0 else 0.0
    open_pct = round(open_val / tot * 100, 1) if tot > 0 else 0.0
    formatted_booking_by_period[p] = {
        'booking': { 'count': tot, 'pct': 100 },
        'show_cai': { 'count': cai_val, 'pct': cai_pct },
        'open': {
            'count': open_val,
            'pct': open_pct,
            'note': 'Customer yang jawab Booking tapi Not CAI (perlu follow up ulang)'
        }
    }

fdata['status_booking_by_period'] = formatted_booking_by_period
fdata['status_booking'] = formatted_booking_by_period['all']

if 'funnel_stages_by_period' in fdata and 'all' in fdata['funnel_stages_by_period']:
    fdata['funnel_stages'] = fdata['funnel_stages_by_period']['all']

if 'not_cai_reasons_by_period' in fdata and 'all' in fdata['not_cai_reasons_by_period']:
    fdata['not_cai_reasons'] = fdata['not_cai_reasons_by_period']['all']

with open('data/funnelling_data.json', 'w', encoding='utf-8') as f:
    json.dump(fdata, f, indent=2, ensure_ascii=False)

print('Successfully generated priority_segments_by_period, potensi_by_program_by_period, and status_booking_by_period!')
