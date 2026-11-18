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

# 1. Load existing funnelling_data.json
with open('data/funnelling_data.json', 'r', encoding='utf-8') as f:
    fdata = json.load(f)

# 2. Process mra_raw_sheet.csv
mra_data = {
    'RANI': {'monthly': {}, 'quarterly': {}, 'ytd': Counter()},
    'NURI': {'monthly': {}, 'quarterly': {}, 'ytd': Counter()}
}
for p in ['RANI', 'NURI']:
    for m in months: mra_data[p]['monthly'][m] = Counter()
    for q in ['Q1', 'Q2', 'Q3']: mra_data[p]['quarterly'][q] = Counter()

sa_data = {
    'DIDIN': {m: Counter() for m in months},
    'FICKY': {m: Counter() for m in months},
    'ACEP': {m: Counter() for m in months}
}

stages_by_period = defaultdict(Counter)
reasons_by_period = defaultdict(Counter)

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
        pic = r[14].strip()
        bln_raw = r[15].strip()
        hasil_fu = r[37].strip()
        sa_val = r[76].strip().upper() if len(r) > 76 else ''
        
        if bln_raw in month_map: m = month_map[bln_raw]
        elif q == '2' or '30/5/26' in due: m = 'Mei'
        elif q == '3' or 'Agu' in (r[39] if len(r)>39 else ''): m = 'Agt'
        else: m = 'Unknown'
        
        if m not in months: continue
        quarter = q_map[m]
        
        # MRA
        pic_norm = 'RANI' if 'RANI' in pic.upper() else ('NURI' if 'NURI' in pic.upper() else None)
        if pic_norm:
            mra_data[pic_norm]['monthly'][m]['potensi'] += 1
            mra_data[pic_norm]['quarterly'][quarter]['potensi'] += 1
            mra_data[pic_norm]['ytd']['potensi'] += 1
            if k1 == 'CUST FU':
                mra_data[pic_norm]['monthly'][m]['fu'] += 1
                mra_data[pic_norm]['quarterly'][quarter]['fu'] += 1
                mra_data[pic_norm]['ytd']['fu'] += 1
            if k3 == 'CONTACTED':
                mra_data[pic_norm]['monthly'][m]['contacted'] += 1
                mra_data[pic_norm]['quarterly'][quarter]['contacted'] += 1
                mra_data[pic_norm]['ytd']['contacted'] += 1
            if cai == 'CAI':
                mra_data[pic_norm]['monthly'][m]['cai'] += 1
                mra_data[pic_norm]['quarterly'][quarter]['cai'] += 1
                mra_data[pic_norm]['ytd']['cai'] += 1
                
        # SA
        if sa_val in sa_data:
            sa_data[sa_val][m]['potensi'] += 1
            if k3 == 'CONTACTED':
                sa_data[sa_val][m]['contacted'] += 1
            if cai == 'CAI':
                sa_data[sa_val][m]['cai'] += 1
                
        # Stages & Reasons
        for period in [m, quarter, 'all']:
            stages_by_period[period]['potency'] += 1
            if k1 == 'CUST FU': stages_by_period[period]['cust_fu'] += 1
            if k2 == 'CONNECTED': stages_by_period[period]['connected'] += 1
            if k3 == 'CONTACTED': stages_by_period[period]['contacted'] += 1
            if 'BOOKING' in hasil_fu.upper(): stages_by_period[period]['booking'] += 1
            if cai == 'CAI': stages_by_period[period]['cai'] += 1
            if hasil_fu: reasons_by_period[period][hasil_fu] += 1

# Format mra_breakdown
formatted_mra = {
    'RANI': {
        'ytd': dict(mra_data['RANI']['ytd']),
        'quarterly': {q: dict(mra_data['RANI']['quarterly'][q]) for q in ['Q1', 'Q2', 'Q3']},
        'monthly': {m: dict(mra_data['RANI']['monthly'][m]) for m in months}
    },
    'NURI': {
        'ytd': dict(mra_data['NURI']['ytd']),
        'quarterly': {q: dict(mra_data['NURI']['quarterly'][q]) for q in ['Q1', 'Q2', 'Q3']},
        'monthly': {m: dict(mra_data['NURI']['monthly'][m]) for m in months}
    }
}
fdata['mra_breakdown'] = formatted_mra

# THS data: keep monthly chart values, add quarterly and ytd
ths_monthly = [
    { "month": "Jan", "potensi": 35, "contacted": 26, "cai": 9, "has_data": True },
    { "month": "Feb", "potensi": 38, "contacted": 28, "cai": 10, "has_data": True },
    { "month": "Mar", "potensi": 32, "contacted": 24, "cai": 8, "has_data": True },
    { "month": "Apr", "potensi": 22, "contacted": 16, "cai": 5, "has_data": True },
    { "month": "Mei", "potensi": 30, "contacted": 22, "cai": 7, "has_data": True },
    { "month": "Jun", "potensi": 34, "contacted": 26, "cai": 9, "has_data": True },
    { "month": "Jul", "potensi": 31, "contacted": 23, "cai": 8, "has_data": True },
    { "month": "Agt", "potensi": 33, "contacted": 25, "cai": 8, "has_data": True },
    { "month": "Sep", "potensi": 30, "contacted": 25, "cai": 8, "has_data": True },
    { "month": "Okt", "potensi": 0, "contacted": 0, "cai": 0, "has_data": False },
    { "month": "Nov", "potensi": 0, "contacted": 0, "cai": 0, "has_data": False },
    { "month": "Des", "potensi": 0, "contacted": 0, "cai": 0, "has_data": False }
]

ths_quarterly = {
    'Q1': { 'potensi': 35+38+32, 'contacted': 26+28+24, 'cai': 9+10+8 },
    'Q2': { 'potensi': 22+30+34, 'contacted': 16+22+26, 'cai': 5+7+9 },
    'Q3': { 'potensi': 31+33+30, 'contacted': 23+25+25, 'cai': 8+8+8 }
}

fdata['potensi_ths'] = {
    'ytd': { 'potensi': 285, 'contacted': 215, 'cai': 72 },
    'quarterly': ths_quarterly,
    'monthly': ths_monthly
}

# Remove potensi_tuls if present
if 'potensi_tuls' in fdata:
    del fdata['potensi_tuls']

# Format sa_breakdown
# All 12 months for chart display
all_12_months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agt', 'Sep', 'Okt', 'Nov', 'Des']

# Calculate total CAI for All SA per month to compute contribution %
total_cai_per_month = {}
total_contacted_per_month = {}
for m in months:
    total_cai_per_month[m] = sum(sa_data[sa][m]['cai'] for sa in ['DIDIN', 'FICKY', 'ACEP'])
    total_contacted_per_month[m] = sum(sa_data[sa][m]['contacted'] for sa in ['DIDIN', 'FICKY', 'ACEP'])

formatted_sa = {}
for sa in ['DIDIN', 'FICKY', 'ACEP']:
    sa_months_list = []
    for m in all_12_months:
        if m in months:
            cnt = sa_data[sa][m]['contacted']
            cai_val = sa_data[sa][m]['cai']
            tot_cai = total_cai_per_month[m]
            contrib = round((cai_val / tot_cai * 100), 1) if tot_cai > 0 else 0
            sa_months_list.append({
                'month': m,
                'potensi': sa_data[sa][m]['potensi'],
                'contacted': cnt,
                'cai': cai_val,
                'contrib_pct': contrib,
                'has_data': True
            })
        else:
            sa_months_list.append({
                'month': m,
                'potensi': 0,
                'contacted': 0,
                'cai': 0,
                'contrib_pct': 0,
                'has_data': False
            })
    formatted_sa[sa] = {'monthly': sa_months_list}

# Add ALL SA entry
all_sa_monthly = []
for m in all_12_months:
    if m in months:
        tot_cnt = total_contacted_per_month[m]
        tot_cai = total_cai_per_month[m]
        all_sa_monthly.append({
            'month': m,
            'contacted': tot_cnt,
            'cai': tot_cai,
            'contrib_pct': 100.0,
            'didin_cai': sa_data['DIDIN'][m]['cai'],
            'didin_cnt': sa_data['DIDIN'][m]['contacted'],
            'didin_contrib': round(sa_data['DIDIN'][m]['cai'] / tot_cai * 100, 1) if tot_cai else 0,
            'ficky_cai': sa_data['FICKY'][m]['cai'],
            'ficky_cnt': sa_data['FICKY'][m]['contacted'],
            'ficky_contrib': round(sa_data['FICKY'][m]['cai'] / tot_cai * 100, 1) if tot_cai else 0,
            'acep_cai': sa_data['ACEP'][m]['cai'],
            'acep_cnt': sa_data['ACEP'][m]['contacted'],
            'acep_contrib': round(sa_data['ACEP'][m]['cai'] / tot_cai * 100, 1) if tot_cai else 0,
            'has_data': True
        })
    else:
        all_sa_monthly.append({
            'month': m,
            'contacted': 0,
            'cai': 0,
            'contrib_pct': 0,
            'didin_cai': 0,
            'didin_cnt': 0,
            'didin_contrib': 0,
            'ficky_cai': 0,
            'ficky_cnt': 0,
            'ficky_contrib': 0,
            'acep_cai': 0,
            'acep_cnt': 0,
            'acep_contrib': 0,
            'has_data': False
        })
formatted_sa['ALL'] = {'monthly': all_sa_monthly}
fdata['sa_breakdown'] = formatted_sa

# Funnel stages by period & NOT CAI reasons by period
formatted_stages = {}
formatted_reasons = {}

all_periods = ['all', 'Q1', 'Q2', 'Q3'] + months
for p in all_periods:
    stg = stages_by_period[p]
    formatted_stages[p] = dict(stg)
    
    # Calculate sorted reasons
    cust_fu = stg['cust_fu'] if stg['cust_fu'] > 0 else 1
    rsn_counter = reasons_by_period[p]
    r_list = []
    for rname in sorted(rsn_counter.keys()):
        count = rsn_counter[rname]
        pct = round((count / cust_fu * 100), 1)
        r_list.append({
            'reason': rname,
            'count': count,
            'percentage': pct
        })
    formatted_reasons[p] = r_list

fdata['funnel_stages_by_period'] = formatted_stages
fdata['not_cai_reasons_by_period'] = formatted_reasons

# Update meta timestamp
fdata['meta']['updated_at'] = '2026-09-21T17:00:00.000000'

with open('data/funnelling_data.json', 'w', encoding='utf-8') as f:
    json.dump(fdata, f, indent=2, ensure_ascii=False)

print('Successfully generated and updated data/funnelling_data.json!')
