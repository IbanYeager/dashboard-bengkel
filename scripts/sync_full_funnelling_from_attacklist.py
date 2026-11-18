import urllib.request
import csv
import io
import json
from datetime import datetime
from collections import Counter, defaultdict

print("1. Mengunduh data terbaru dari live Google Sheets ATTACKLIST (GID 2141708170)...")
url = 'https://docs.google.com/spreadsheets/d/1b60d-JO50LU4KyywuULokmDIU7z3Ts_1/gviz/tq?tqx=out:csv&gid=2141708170'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
content = urllib.request.urlopen(req).read().decode('utf-8')
reader = list(csv.reader(io.StringIO(content)))
header = reader[0]
rows = reader[1:]

print(f"Total baris ATTACKLIST berhasil diunduh: {len(rows)} baris")

def get_row_month(r):
    # 1. Col 15 (Bulan)
    b = r[15].strip() if len(r) > 15 else ''
    for m, k in [
        ('Jan','Jan'), ('Feb','Feb'), ('Mar','Mar'), ('Apr','Apr'),
        ('Mei','Mei'), ('May','Mei'), ('Jun','Jun'), ('Jul','Jul'),
        ('Agu','Agt'), ('Aug','Agt'), ('Sep','Sep'),
        ('Okt','Okt'), ('Oct','Okt'), ('Nov','Nov'), ('Des','Des'), ('Dec','Des')
    ]:
        if m in b: return k
    
    # 2. Col 39 (Tgl Follow Up)
    fu = r[39].strip() if len(r) > 39 else ''
    for m, k in [
        ('Jan','Jan'), ('Feb','Feb'), ('Mar','Mar'), ('Apr','Apr'),
        ('Mei','Mei'), ('May','Mei'), ('Jun','Jun'), ('Jul','Jul'),
        ('Agu','Agt'), ('Aug','Agt'), ('Sep','Sep'),
        ('Okt','Okt'), ('Oct','Okt'), ('Nov','Nov'), ('Des','Des'), ('Dec','Des')
    ]:
        if m in fu: return k
        
    # 3. Col 55 (NEXT SERVICE (MONTH))
    nsm = r[55].strip() if len(r) > 55 else ''
    if '2026-10' in nsm or '10/' in nsm: return 'Okt'
    if '2026-11' in nsm or '11/' in nsm: return 'Nov'
    if '2026-12' in nsm or '12/' in nsm: return 'Des'

    # 4. Fallback to Quartal
    q = r[0].strip() if len(r) > 0 else ''
    if q == '1': return 'Q1'
    if q == '2': return 'Q2'
    if q == '3': return 'Q3'
    if q == '4':
        row_str = ' '.join(r).lower()
        if 'des' in row_str or 'dec' in row_str: return 'Des'
        if 'nov' in row_str: return 'Nov'
        return 'Okt'
    return 'unknown'

def compute_funnel_stages(row_subset):
    potency = len(row_subset)
    cust_fu = sum(1 for r in row_subset if len(r) > 1 and 'CUST FU' in r[1].upper())
    connected = sum(1 for r in row_subset if len(r) > 2 and 'CONNECTED' in r[2].upper())
    contacted = sum(1 for r in row_subset if len(r) > 3 and 'CONTACTED' in r[3].upper())
    booking = sum(1 for r in row_subset if (len(r) > 5 and r[5].strip().upper() in ['SO', 'BOOKING']) or (len(r) > 81 and r[81].strip()))
    cai = sum(1 for r in row_subset if len(r) > 4 and r[4].strip().upper() == 'CAI')
    return {
        "potency": potency,
        "cust_fu": cust_fu or potency,
        "connected": connected,
        "contacted": contacted,
        "booking": booking,
        "cai": cai
    }

def compute_not_cai_reasons(row_subset, total_cust_fu):
    reasons_counter = Counter()
    for r in row_subset:
        if len(r) > 4 and r[4].strip().upper() != 'CAI':
            reason = r[37].strip() if len(r) > 37 and r[37].strip() else ''
            if not reason and len(r) > 34:
                reason = r[34].strip()
            if not reason:
                reason = 'Lain-lain'
            
            r_low = reason.lower()
            if 'tidak diangkat' in r_low or 'tidak ada jawaban' in r_low or 'tutup' in r_low or 'reject' in r_low:
                r_norm = 'Tidak diangkat'
            elif 'akan menghubungi' in r_low or 'hubungi nanti' in r_low:
                r_norm = 'Akan menghubungi Bengkel'
            elif 'booking' in r_low:
                r_norm = 'Booking'
            elif 'dijual' in r_low:
                r_norm = 'Kendaraan dijual'
            elif 'operasional' in r_low:
                r_norm = 'Kendaraan operasional'
            elif 'tempat lain' in r_low or 'bengkel lain' in r_low or 'luar' in r_low:
                r_norm = 'Service ditempat lain'
            elif 'tidak dapat dihubungi' in r_low or 'nomor salah' in r_low or 'inaktif' in r_low:
                r_norm = 'Nomor tidak dapat dihubungi'
            elif 'bukan user' in r_low:
                r_norm = 'Bukan user'
            elif 'lokasi' in r_low or 'jauh' in r_low:
                r_norm = 'Lokasi'
            elif 'early' in r_low:
                r_norm = 'Early'
            elif 'late' in r_low:
                r_norm = 'Late'
            else:
                r_norm = 'Lain-lain'
            reasons_counter[r_norm] += 1

    std_reasons = [
        "Akan menghubungi Bengkel",
        "Booking",
        "Bukan user",
        "Early",
        "Kendaraan dijual",
        "Kendaraan operasional",
        "Lain-lain",
        "Late",
        "Lokasi",
        "Nomor tidak dapat dihubungi",
        "Service ditempat lain",
        "Tidak diangkat"
    ]
    res = []
    base_div = total_cust_fu if total_cust_fu > 0 else sum(reasons_counter.values()) or 1
    for sr in std_reasons:
        cnt = reasons_counter.get(sr, 0)
        pct = round(cnt / base_div * 100, 1)
        res.append({"reason": sr, "count": cnt, "percentage": pct})
    return res

def build_priority_segments(row_subset):
    ex_soon = {'Eligible': [0,0], 'Not Eligible': [0,0], 'Never claim': [0,0]}
    active = {'Eligible': [0,0], 'Not Eligible': [0,0], 'Never claim': [0,0]}
    finish = {'Eligible': [0,0], 'Not Eligible': [0,0]}
    expired = {'Eligible': [0,0], 'Not Eligible': [0,0], 'Never claim': [0,0]}
    crt_merdeka = {'HOT': [0,0], 'Medium': [0,0], 'Low': [0,0]}
    crt_non_merdeka = {'HOT': [0,0], 'Medium': [0,0], 'Low': [0,0]}

    for r in row_subset:
        if len(r) <= 8: continue
        j = r[8].strip().upper()
        cai = (r[4].strip().upper() == 'CAI')
        cabang = r[20].strip().upper() if len(r) > 20 else ''
        pros = r[11].strip().upper() if len(r) > 11 else 'MEDIUM'
        
        p_label = 'Medium'
        if 'HOT' in pros: p_label = 'HOT'
        elif 'LOW' in pros: p_label = 'Low'

        if 'EXPIRED SOON' in j:
            if 'NEVER' in j:
                ex_soon['Never claim'][0] += 1
                if cai: ex_soon['Never claim'][1] += 1
            elif 'NOT' in j:
                ex_soon['Not Eligible'][0] += 1
                if cai: ex_soon['Not Eligible'][1] += 1
            else:
                ex_soon['Eligible'][0] += 1
                if cai: ex_soon['Eligible'][1] += 1
        elif 'ACTIVE' in j:
            if 'NEVER' in j:
                active['Never claim'][0] += 1
                if cai: active['Never claim'][1] += 1
            elif 'NOT' in j:
                active['Not Eligible'][0] += 1
                if cai: active['Not Eligible'][1] += 1
            else:
                active['Eligible'][0] += 1
                if cai: active['Eligible'][1] += 1
        elif 'FINISH' in j:
            if 'NOT' in j:
                finish['Not Eligible'][0] += 1
                if cai: finish['Not Eligible'][1] += 1
            else:
                finish['Eligible'][0] += 1
                if cai: finish['Eligible'][1] += 1
        elif 'EXPIRED' in j:
            if 'NEVER' in j:
                expired['Never claim'][0] += 1
                if cai: expired['Never claim'][1] += 1
            elif 'NOT' in j:
                expired['Not Eligible'][0] += 1
                if cai: expired['Not Eligible'][1] += 1
            else:
                expired['Eligible'][0] += 1
                if cai: expired['Eligible'][1] += 1
        elif 'CRT' in j:
            target = crt_merdeka if 'MERDEKA' in cabang else crt_non_merdeka
            target[p_label][0] += 1
            if cai: target[p_label][1] += 1

    def make_group(group_name, title, data_dict, total_label):
        subgroups = []
        tot_pot = 0
        tot_cai = 0
        for lbl, (pot, c) in data_dict.items():
            tot_pot += pot
            tot_cai += c
            pct = round(c / pot * 100, 1) if pot > 0 else 0
            if group_name == "Priority 1": full_lbl = f"Expired soon - {lbl}"
            elif group_name == "Priority 2": full_lbl = f"Active - {lbl}"
            elif group_name == "Priority 3": full_lbl = f"Finish - {lbl}"
            elif group_name == "Priority 4": full_lbl = f"Expired - {lbl}"
            else: full_lbl = lbl
            subgroups.append({"label": full_lbl, "potensi": pot, "cai": c, "pct": pct})
        tot_pct = round(tot_cai / tot_pot * 100, 1) if tot_pot > 0 else 0
        res = {
            "group": group_name,
            "subgroups": subgroups,
            "total_label": total_label,
            "total_potensi": tot_pot,
            "total_cai": tot_cai,
            "total_pct": tot_pct
        }
        if title: res["title"] = title
        return res

    return [
        make_group("Priority 1", None, ex_soon, "TOTAL EX SOON"),
        make_group("Priority 2", None, active, "TOTAL ACTIVE"),
        make_group("Priority 3", None, finish, "TOTAL FINISH"),
        make_group("Priority 4", None, expired, "TOTAL EXPIRED"),
        make_group("Priority 5", "CRT > 8th Merdeka Motor (Pembelian Asal: MERDEKA — Kolom Judgement Cust)", crt_merdeka, "TOTAL CRT MERDEKA"),
        make_group("Priority 6", "CRT > 8th All Penjualan (Pembelian Asal: Selain Merdeka — Kolom Judgement Cust)", crt_non_merdeka, "TOTAL CRT NON MERDEKA"),
    ]

def compute_tcare_programs(row_subset):
    prog_titles = {
        't_care': 'I. T-CARE',
        't_care_lite_plus': 'II. T-CARE Lite +',
        't_care_lite': 'III. T-CARE Lite',
        'care_x': 'IV. Potensi CARE-X'
    }
    raw = {k: {'potency': 0, 'cust_fu': 0, 'connected': 0, 'contacted': 0, 'booking': 0, 'cai': 0} for k in prog_titles}
    for r in row_subset:
        part_type = r[7].strip().upper() if len(r) > 7 else ''
        if part_type == 'T-CARE':
            prog_key = 't_care'
        elif 'LITE+' in part_type or 'LITE +' in part_type:
            prog_key = 't_care_lite_plus'
        elif 'LITE' in part_type:
            prog_key = 't_care_lite'
        else:
            prog_key = 'care_x'
        
        raw[prog_key]['potency'] += 1
        if len(r) > 1 and 'CUST FU' in r[1].upper(): raw[prog_key]['cust_fu'] += 1
        if len(r) > 2 and 'CONNECTED' in r[2].upper(): raw[prog_key]['connected'] += 1
        if len(r) > 3 and 'CONTACTED' in r[3].upper(): raw[prog_key]['contacted'] += 1
        
        has_bk = False
        if len(r) > 5 and r[5].strip().upper() in ['SO', 'BOOKING']: has_bk = True
        elif len(r) > 81 and r[81].strip(): has_bk = True
        elif len(r) > 37 and 'BOOKING' in r[37].strip().upper(): has_bk = True
        if has_bk: raw[prog_key]['booking'] += 1
        
        if len(r) > 4 and r[4].strip().upper() == 'CAI': raw[prog_key]['cai'] += 1

    return {
        k: {
            'title': prog_titles[k],
            **raw[k]
        } for k in prog_titles
    }

def compute_status_booking(row_subset):
    tot = 0
    cai_val = 0
    open_val = 0
    for r in row_subset:
        has_bk = False
        if len(r) > 5 and r[5].strip().upper() in ['SO', 'BOOKING']: has_bk = True
        elif len(r) > 81 and r[81].strip(): has_bk = True
        elif len(r) > 37 and 'BOOKING' in r[37].strip().upper(): has_bk = True
        
        if has_bk:
            tot += 1
            if len(r) > 4 and r[4].strip().upper() == 'CAI':
                cai_val += 1
            else:
                open_val += 1
    
    cai_pct = round(cai_val / tot * 100, 1) if tot > 0 else 0.0
    open_pct = round(open_val / tot * 100, 1) if tot > 0 else 0.0
    return {
        'booking': {'count': tot, 'pct': 100},
        'show_cai': {'count': cai_val, 'pct': cai_pct},
        'open': {
            'count': open_val,
            'pct': open_pct,
            'warning_text': f"⚠️ {open_pct}%: Customer yang jawab Booking tapi Not CAI (perlu follow up ulang)"
        }
    }

all_12_months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agt', 'Sep', 'Okt', 'Nov', 'Des']
month_to_q = {
    'Jan': 'Q1', 'Feb': 'Q1', 'Mar': 'Q1',
    'Apr': 'Q2', 'Mei': 'Q2', 'Jun': 'Q2',
    'Jul': 'Q3', 'Agt': 'Q3', 'Sep': 'Q3',
    'Okt': 'Q4', 'Nov': 'Q4', 'Des': 'Q4'
}

period_rows = {'all': rows}
for q in ['1', '2', '3', '4']:
    period_rows[f"Q{q}"] = [r for r in rows if len(r) > 0 and r[0].strip() == q]

# Add any additional Q4 rows (Okt, Nov, Des) into Q4
for r in rows:
    rm = get_row_month(r)
    if rm in ['Okt', 'Nov', 'Des'] and r not in period_rows['Q4']:
        period_rows['Q4'].append(r)

for m in all_12_months:
    period_rows[m] = [r for r in rows if get_row_month(r) == m]

# Assemble stages, reasons, priority segments, tcare programs, status booking
funnel_stages_by_period = {}
not_cai_reasons_by_period = {}
priority_segments_by_period = {}
potensi_by_program_by_period = {}
status_booking_by_period = {}

for p_key, p_subset in period_rows.items():
    stg = compute_funnel_stages(p_subset)
    funnel_stages_by_period[p_key] = stg
    not_cai_reasons_by_period[p_key] = compute_not_cai_reasons(p_subset, stg['cust_fu'])
    priority_segments_by_period[p_key] = build_priority_segments(p_subset)
    potensi_by_program_by_period[p_key] = compute_tcare_programs(p_subset)
    status_booking_by_period[p_key] = compute_status_booking(p_subset)

# Monthly summary dynamically detecting active months
month_id_names = {
    'Jan': 'Januari', 'Feb': 'Februari', 'Mar': 'Maret', 'Apr': 'April',
    'Mei': 'Mei', 'Jun': 'Juni', 'Jul': 'Juli', 'Agt': 'Agustus', 'Sep': 'September',
    'Okt': 'Oktober', 'Nov': 'November', 'Des': 'Desember'
}

monthly_summary = []
for m in all_12_months:
    stg = funnel_stages_by_period.get(m, {'cust_fu': 0, 'contacted': 0, 'cai': 0, 'potency': 0})
    has_data = (stg['cust_fu'] > 0 or stg['potency'] > 0)
    monthly_summary.append({
        "month": m,
        "month_name": month_id_names.get(m, m),
        "cust_fu": stg['cust_fu'],
        "contacted": stg['contacted'],
        "cai": stg['cai'],
        "has_data": has_data
    })

# -------------------------------------------------------------
# Compute SA Breakdown (DIDIN, FICKY, ACEP, ALL)
# -------------------------------------------------------------
sa_names = ['DIDIN', 'FICKY', 'ACEP']
sa_raw = {sa: {m: {'potensi': 0, 'contacted': 0, 'cai': 0} for m in all_12_months} for sa in sa_names}

for r in rows:
    m = get_row_month(r)
    if m not in all_12_months: continue
    sa_col = r[76].strip().upper() if len(r) > 76 else ''
    is_cont = (len(r) > 3 and 'CONTACTED' in r[3].upper())
    is_cai = (len(r) > 4 and r[4].strip().upper() == 'CAI')

    for sa in sa_names:
        if sa in sa_col:
            sa_raw[sa][m]['potensi'] += 1
            if is_cont: sa_raw[sa][m]['contacted'] += 1
            if is_cai: sa_raw[sa][m]['cai'] += 1

total_cai_per_month = {}
total_contacted_per_month = {}
for m in all_12_months:
    total_cai_per_month[m] = sum(sa_raw[sa][m]['cai'] for sa in sa_names)
    total_contacted_per_month[m] = sum(sa_raw[sa][m]['contacted'] for sa in sa_names)

sa_breakdown = {}
for sa in sa_names:
    sa_months_list = []
    for m in all_12_months:
        cai_val = sa_raw[sa][m]['cai']
        cnt_val = sa_raw[sa][m]['contacted']
        tot_cai = total_cai_per_month[m]
        contrib = round(cai_val / tot_cai * 100, 1) if tot_cai > 0 else 0
        m_stg = funnel_stages_by_period.get(m, {'cust_fu': 0, 'potency': 0})
        has_data = (m_stg['cust_fu'] > 0 or m_stg['potency'] > 0)
        sa_months_list.append({
            'month': m,
            'potensi': sa_raw[sa][m]['potensi'],
            'contacted': cnt_val,
            'cai': cai_val,
            'contrib_pct': contrib,
            'has_data': has_data
        })
    sa_breakdown[sa] = {'monthly': sa_months_list}

all_sa_monthly = []
for m in all_12_months:
    tot_cai = total_cai_per_month[m]
    tot_cnt = total_contacted_per_month[m]
    m_stg = funnel_stages_by_period.get(m, {'cust_fu': 0, 'potency': 0})
    has_data = (m_stg['cust_fu'] > 0 or m_stg['potency'] > 0)
    all_sa_monthly.append({
        'month': m,
        'contacted': tot_cnt,
        'cai': tot_cai,
        'contrib_pct': 100.0 if tot_cai > 0 else 0,
        'didin_cai': sa_raw['DIDIN'][m]['cai'],
        'didin_cnt': sa_raw['DIDIN'][m]['contacted'],
        'didin_contrib': round(sa_raw['DIDIN'][m]['cai'] / tot_cai * 100, 1) if tot_cai else 0,
        'ficky_cai': sa_raw['FICKY'][m]['cai'],
        'ficky_cnt': sa_raw['FICKY'][m]['contacted'],
        'ficky_contrib': round(sa_raw['FICKY'][m]['cai'] / tot_cai * 100, 1) if tot_cai else 0,
        'acep_cai': sa_raw['ACEP'][m]['cai'],
        'acep_cnt': sa_raw['ACEP'][m]['contacted'],
        'acep_contrib': round(sa_raw['ACEP'][m]['cai'] / tot_cai * 100, 1) if tot_cai else 0,
        'has_data': has_data
    })
sa_breakdown['ALL'] = {'monthly': all_sa_monthly}

# -------------------------------------------------------------
# Compute MRA Breakdown (RANI & NURI)
# -------------------------------------------------------------
mra_raw = {
    'RANI': {'monthly': {m: Counter() for m in all_12_months}, 'quarterly': {q: Counter() for q in ['Q1','Q2','Q3','Q4']}, 'ytd': Counter()},
    'NURI': {'monthly': {m: Counter() for m in all_12_months}, 'quarterly': {q: Counter() for q in ['Q1','Q2','Q3','Q4']}, 'ytd': Counter()}
}

for r in rows:
    m = get_row_month(r)
    if m not in all_12_months: continue
    q = month_to_q[m]
    pic_col = r[14].strip().upper() if len(r) > 14 else ''
    pic_norm = 'RANI' if 'RANI' in pic_col else ('NURI' if 'NURI' in pic_col else None)
    if not pic_norm: continue

    is_fu = (len(r) > 1 and 'CUST FU' in r[1].upper())
    is_cont = (len(r) > 3 and 'CONTACTED' in r[3].upper())
    is_cai = (len(r) > 4 and r[4].strip().upper() == 'CAI')

    for target in [mra_raw[pic_norm]['monthly'][m], mra_raw[pic_norm]['quarterly'][q], mra_raw[pic_norm]['ytd']]:
        target['potensi'] += 1
        if is_fu: target['fu'] += 1
        if is_cont: target['contacted'] += 1
        if is_cai: target['cai'] += 1

mra_breakdown = {
    'RANI': {
        'ytd': dict(mra_raw['RANI']['ytd']),
        'quarterly': {q: dict(mra_raw['RANI']['quarterly'][q]) for q in ['Q1', 'Q2', 'Q3', 'Q4']},
        'monthly': {m: dict(mra_raw['RANI']['monthly'][m]) for m in all_12_months}
    },
    'NURI': {
        'ytd': dict(mra_raw['NURI']['ytd']),
        'quarterly': {q: dict(mra_raw['NURI']['quarterly'][q]) for q in ['Q1', 'Q2', 'Q3', 'Q4']},
        'monthly': {m: dict(mra_raw['NURI']['monthly'][m]) for m in all_12_months}
    }
}

# -------------------------------------------------------------
# Compute Potensi THS
# -------------------------------------------------------------
ths_raw = {m: {'potensi': 0, 'contacted': 0, 'cai': 0} for m in all_12_months}
for r in rows:
    m = get_row_month(r)
    if m not in all_12_months: continue
    if len(r) > 72 and 'THS' in r[72].strip().upper() and 'NON' not in r[72].strip().upper():
        ths_raw[m]['potensi'] += 1
        if len(r) > 3 and 'CONTACTED' in r[3].upper(): ths_raw[m]['contacted'] += 1
        if len(r) > 4 and r[4].strip().upper() == 'CAI': ths_raw[m]['cai'] += 1

ths_monthly = []
for m in all_12_months:
    m_stg = funnel_stages_by_period.get(m, {'cust_fu': 0, 'potency': 0})
    has_data = (m_stg['cust_fu'] > 0 or m_stg['potency'] > 0)
    ths_monthly.append({
        'month': m,
        'potensi': ths_raw[m]['potensi'],
        'contacted': ths_raw[m]['contacted'],
        'cai': ths_raw[m]['cai'],
        'has_data': has_data
    })

ths_quarterly = {}
for q, q_months in [('Q1',['Jan','Feb','Mar']), ('Q2',['Apr','Mei','Jun']), ('Q3',['Jul','Agt','Sep']), ('Q4',['Okt','Nov','Des'])]:
    ths_quarterly[q] = {
        'potensi': sum(ths_raw[m]['potensi'] for m in q_months),
        'contacted': sum(ths_raw[m]['contacted'] for m in q_months),
        'cai': sum(ths_raw[m]['cai'] for m in q_months)
    }

potensi_ths = {
    'ytd': {
        'potensi': sum(ths_raw[m]['potensi'] for m in all_12_months),
        'contacted': sum(ths_raw[m]['contacted'] for m in all_12_months),
        'cai': sum(ths_raw[m]['cai'] for m in all_12_months)
    },
    'quarterly': ths_quarterly,
    'monthly': ths_monthly
}

# -------------------------------------------------------------
# Compute Monthly Ring Area Trend & Fleet/Retail Trend
# -------------------------------------------------------------
ring_monthly = defaultdict(lambda: defaultdict(lambda: {'cust_fu': 0, 'connected': 0}))
fleet_monthly = defaultdict(lambda: defaultdict(lambda: {'cust_fu': 0, 'connected': 0}))

for r in rows:
    m = get_row_month(r)
    if m not in all_12_months: continue

    is_conn = (len(r) > 2 and 'CONNECTED' in r[2].upper())

    # Ring Area Col 27
    area_raw = r[27].strip().upper() if len(r) > 27 else ''
    if '1' in area_raw: area = 'Ring 1'
    elif '2' in area_raw: area = 'Ring 2'
    elif '3' in area_raw: area = 'Ring 3'
    else: area = 'Out of Area'

    # Fleet / Retail Col 28
    flt_raw = r[28].strip().upper() if len(r) > 28 else ''
    if any(k in flt_raw for k in ['FLEET', 'SUDECO', 'TPI']): flt = 'Fleet'
    else: flt = 'Retail'

    ring_monthly[m][area]['cust_fu'] += 1
    if is_conn: ring_monthly[m][area]['connected'] += 1

    fleet_monthly[m][flt]['cust_fu'] += 1
    if is_conn: fleet_monthly[m][flt]['connected'] += 1

# Read existing JSON to preserve meta and other fields
with open('data/funnelling_data.json', 'r', encoding='utf-8') as f:
    fn = json.load(f)

fn['meta']['updated_at'] = datetime.now().isoformat()
fn['meta']['valid_until'] = 'Oktober 2026'
fn['meta']['active_months_count'] = 10

fn['monthly_summary'] = monthly_summary
fn['funnel_stages'] = funnel_stages_by_period['all']
fn['funnel_stages_by_period'] = funnel_stages_by_period
fn['not_cai_reasons'] = not_cai_reasons_by_period['all']
fn['not_cai_reasons_by_period'] = not_cai_reasons_by_period
fn['priority_segments'] = priority_segments_by_period['all']
fn['priority_segments_by_period'] = priority_segments_by_period
fn['sa_breakdown'] = sa_breakdown
fn['mra_breakdown'] = mra_breakdown
fn['potensi_ths'] = potensi_ths
fn['monthly_ring_area_trend'] = ring_monthly
fn['monthly_fleet_retail_trend'] = fleet_monthly
fn['potensi_by_program'] = potensi_by_program_by_period['all']
fn['potensi_by_program_by_period'] = potensi_by_program_by_period
fn['status_booking'] = status_booking_by_period['all']
fn['status_booking_by_period'] = status_booking_by_period

with open('data/funnelling_data.json', 'w', encoding='utf-8') as f:
    json.dump(fn, f, indent=2, ensure_ascii=False)

print("\n=== HASIL SINKRONISASI LENGKAP TERSIMPAN KE data/funnelling_data.json ===")
print(f"Total Rows: {len(rows)}")
print(f"Bulan Oktober:")
stg_okt = funnel_stages_by_period['Okt']
print(f"  Potensi: {stg_okt['potency']}, Cust FU: {stg_okt['cust_fu']}, Connected: {stg_okt['connected']}, Contacted: {stg_okt['contacted']}, Booking: {stg_okt['booking']}, CAI: {stg_okt['cai']}")
print(f"  SA Breakdown Oktober: DIDIN={sa_raw['DIDIN']['Okt']}, FICKY={sa_raw['FICKY']['Okt']}, ACEP={sa_raw['ACEP']['Okt']}")
print(f"  MRA Oktober: RANI={mra_breakdown['RANI']['monthly']['Okt']}, NURI={mra_breakdown['NURI']['monthly']['Okt']}")
print(f"  THS Oktober: {ths_raw['Okt']}")
