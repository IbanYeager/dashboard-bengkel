with open('scripts/sync_full_funnelling_from_attacklist.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update get_row_month in python script
old_q4_py = """    # 4. Fallback to Quartal
    q = r[0].strip() if len(r) > 0 else ''
    if q == '1': return 'Q1'
    if q == '2': return 'Q2'
    if q == '3': return 'Q3'
    if q == '4': return 'Okt' # currently in Q4 active month is October
    return 'unknown'"""

new_q4_py = """    # 4. Fallback to Quartal
    q = r[0].strip() if len(r) > 0 else ''
    if q == '1': return 'Q1'
    if q == '2': return 'Q2'
    if q == '3': return 'Q3'
    if q == '4':
        row_str = ' '.join(r).lower()
        if 'des' in row_str or 'dec' in row_str: return 'Des'
        if 'nov' in row_str: return 'Nov'
        return 'Okt'
    return 'unknown'"""

assert old_q4_py in code, "old_q4_py not found"
code = code.replace(old_q4_py, new_q4_py)

# 2. Dynamic all_12_months for periods & monthly_summary
old_periods_py = """# Months list including Okt!
months_list = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agt', 'Sep', 'Okt']
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

# Add any additional Okt rows into Q4
for r in rows:
    if get_row_month(r) == 'Okt' and r not in period_rows['Q4']:
        period_rows['Q4'].append(r)

for m in months_list:
    period_rows[m] = [r for r in rows if get_row_month(r) == m]

# Assemble stages, reasons, priority segments
funnel_stages_by_period = {}
not_cai_reasons_by_period = {}
priority_segments_by_period = {}

for p_key, p_subset in period_rows.items():
    stg = compute_funnel_stages(p_subset)
    funnel_stages_by_period[p_key] = stg
    not_cai_reasons_by_period[p_key] = compute_not_cai_reasons(p_subset, stg['cust_fu'])
    priority_segments_by_period[p_key] = build_priority_segments(p_subset)

# Monthly summary
month_id_names = {
    'Jan': 'Januari', 'Feb': 'Februari', 'Mar': 'Maret', 'Apr': 'April',
    'Mei': 'Mei', 'Jun': 'Juni', 'Jul': 'Juli', 'Agt': 'Agustus', 'Sep': 'September',
    'Okt': 'Oktober', 'Nov': 'November', 'Des': 'Desember'
}

monthly_summary = []
for m in months_list:
    stg = funnel_stages_by_period[m]
    monthly_summary.append({
        "month": m,
        "month_name": month_id_names.get(m, m),
        "cust_fu": stg['cust_fu'],
        "contacted": stg['contacted'],
        "cai": stg['cai'],
        "has_data": True
    })

# Add Nov, Des placeholders
for m in ['Nov', 'Des']:
    monthly_summary.append({
        "month": m,
        "month_name": month_id_names[m],
        "cust_fu": 0,
        "contacted": 0,
        "cai": 0,
        "has_data": False
    })"""

new_periods_py = """all_12_months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agt', 'Sep', 'Okt', 'Nov', 'Des']
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

# Assemble stages, reasons, priority segments
funnel_stages_by_period = {}
not_cai_reasons_by_period = {}
priority_segments_by_period = {}

for p_key, p_subset in period_rows.items():
    stg = compute_funnel_stages(p_subset)
    funnel_stages_by_period[p_key] = stg
    not_cai_reasons_by_period[p_key] = compute_not_cai_reasons(p_subset, stg['cust_fu'])
    priority_segments_by_period[p_key] = build_priority_segments(p_subset)

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
    })"""

assert old_periods_py in code, "old_periods_py not found"
code = code.replace(old_periods_py, new_periods_py)

# 3. SA Breakdown using all_12_months
old_sa_py = """sa_names = ['DIDIN', 'FICKY', 'ACEP']
sa_raw = {sa: {m: {'potensi': 0, 'contacted': 0, 'cai': 0} for m in months_list} for sa in sa_names}

for r in rows:
    m = get_row_month(r)
    if m not in months_list: continue
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
for m in months_list:
    total_cai_per_month[m] = sum(sa_raw[sa][m]['cai'] for sa in sa_names)
    total_contacted_per_month[m] = sum(sa_raw[sa][m]['contacted'] for sa in sa_names)

sa_breakdown = {}
for sa in sa_names:
    sa_months_list = []
    for m in all_12_months:
        if m in months_list:
            cai_val = sa_raw[sa][m]['cai']
            cnt_val = sa_raw[sa][m]['contacted']
            tot_cai = total_cai_per_month[m]
            contrib = round(cai_val / tot_cai * 100, 1) if tot_cai > 0 else 0
            sa_months_list.append({
                'month': m,
                'potensi': sa_raw[sa][m]['potensi'],
                'contacted': cnt_val,
                'cai': cai_val,
                'contrib_pct': contrib,
                'has_data': True
            })
        else:
            sa_months_list.append({
                'month': m, 'potensi': 0, 'contacted': 0, 'cai': 0, 'contrib_pct': 0, 'has_data': False
            })
    sa_breakdown[sa] = {'monthly': sa_months_list}

all_sa_monthly = []
for m in all_12_months:
    if m in months_list:
        tot_cai = total_cai_per_month[m]
        tot_cnt = total_contacted_per_month[m]
        all_sa_monthly.append({
            'month': m,
            'contacted': tot_cnt,
            'cai': tot_cai,
            'contrib_pct': 100.0,
            'didin_cai': sa_raw['DIDIN'][m]['cai'],
            'didin_cnt': sa_raw['DIDIN'][m]['contacted'],
            'didin_contrib': round(sa_raw['DIDIN'][m]['cai'] / tot_cai * 100, 1) if tot_cai else 0,
            'ficky_cai': sa_raw['FICKY'][m]['cai'],
            'ficky_cnt': sa_raw['FICKY'][m]['contacted'],
            'ficky_contrib': round(sa_raw['FICKY'][m]['cai'] / tot_cai * 100, 1) if tot_cai else 0,
            'acep_cai': sa_raw['ACEP'][m]['cai'],
            'acep_cnt': sa_raw['ACEP'][m]['contacted'],
            'acep_contrib': round(sa_raw['ACEP'][m]['cai'] / tot_cai * 100, 1) if tot_cai else 0,
            'has_data': True
        })
    else:
        all_sa_monthly.append({
            'month': m, 'contacted': 0, 'cai': 0, 'contrib_pct': 0,
            'didin_cai': 0, 'didin_cnt': 0, 'didin_contrib': 0,
            'ficky_cai': 0, 'ficky_cnt': 0, 'ficky_contrib': 0,
            'acep_cai': 0, 'acep_cnt': 0, 'acep_contrib': 0,
            'has_data': False
        })
sa_breakdown['ALL'] = {'monthly': all_sa_monthly}"""

new_sa_py = """sa_names = ['DIDIN', 'FICKY', 'ACEP']
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
sa_breakdown['ALL'] = {'monthly': all_sa_monthly}"""

assert old_sa_py in code, "old_sa_py not found"
code = code.replace(old_sa_py, new_sa_py)

# 4. MRA Breakdown for all_12_months
old_mra_py = """mra_raw = {
    'RANI': {'monthly': {m: Counter() for m in months_list}, 'quarterly': {q: Counter() for q in ['Q1','Q2','Q3','Q4']}, 'ytd': Counter()},
    'NURI': {'monthly': {m: Counter() for m in months_list}, 'quarterly': {q: Counter() for q in ['Q1','Q2','Q3','Q4']}, 'ytd': Counter()}
}

for r in rows:
    m = get_row_month(r)
    if m not in months_list: continue
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
        'monthly': {m: dict(mra_raw['RANI']['monthly'][m]) for m in months_list}
    },
    'NURI': {
        'ytd': dict(mra_raw['NURI']['ytd']),
        'quarterly': {q: dict(mra_raw['NURI']['quarterly'][q]) for q in ['Q1', 'Q2', 'Q3', 'Q4']},
        'monthly': {m: dict(mra_raw['NURI']['monthly'][m]) for m in months_list}
    }
}"""

new_mra_py = """mra_raw = {
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
}"""

assert old_mra_py in code, "old_mra_py not found"
code = code.replace(old_mra_py, new_mra_py)

# 5. Potensi THS for all_12_months
old_ths_py = """ths_raw = {m: {'potensi': 0, 'contacted': 0, 'cai': 0} for m in months_list}
for r in rows:
    m = get_row_month(r)
    if m not in months_list: continue
    if len(r) > 72 and 'THS' in r[72].strip().upper() and 'NON' not in r[72].strip().upper():
        ths_raw[m]['potensi'] += 1
        if len(r) > 3 and 'CONTACTED' in r[3].upper(): ths_raw[m]['contacted'] += 1
        if len(r) > 4 and r[4].strip().upper() == 'CAI': ths_raw[m]['cai'] += 1

ths_monthly = []
for m in all_12_months:
    if m in months_list:
        ths_monthly.append({
            'month': m,
            'potensi': ths_raw[m]['potensi'],
            'contacted': ths_raw[m]['contacted'],
            'cai': ths_raw[m]['cai'],
            'has_data': True
        })
    else:
        ths_monthly.append({
            'month': m, 'potensi': 0, 'contacted': 0, 'cai': 0, 'has_data': False
        })

ths_quarterly = {}
for q, q_months in [('Q1',['Jan','Feb','Mar']), ('Q2',['Apr','Mei','Jun']), ('Q3',['Jul','Agt','Sep']), ('Q4',['Okt'])]:
    ths_quarterly[q] = {
        'potensi': sum(ths_raw[m]['potensi'] for m in q_months if m in ths_raw),
        'contacted': sum(ths_raw[m]['contacted'] for m in q_months if m in ths_raw),
        'cai': sum(ths_raw[m]['cai'] for m in q_months if m in ths_raw)
    }

potensi_ths = {
    'ytd': {
        'potensi': sum(ths_raw[m]['potensi'] for m in months_list),
        'contacted': sum(ths_raw[m]['contacted'] for m in months_list),
        'cai': sum(ths_raw[m]['cai'] for m in months_list)
    },
    'quarterly': ths_quarterly,
    'monthly': ths_monthly
}"""

new_ths_py = """ths_raw = {m: {'potensi': 0, 'contacted': 0, 'cai': 0} for m in all_12_months}
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
}"""

assert old_ths_py in code, "old_ths_py not found"
code = code.replace(old_ths_py, new_ths_py)

# 6. Ring & Fleet for all_12_months
old_ring_py = "if m not in months_list: continue"
new_ring_py = "if m not in all_12_months: continue"
code = code.replace(old_ring_py, new_ring_py)

with open('scripts/sync_full_funnelling_from_attacklist.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("sync_full_funnelling_from_attacklist.py updated for dynamic future months!")
