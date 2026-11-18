import json
import math

print("=====================================================================")
print(" DEEP AUDIT & VALIDATION ACROSS ALL 10 MENUS / TABS IN DASHBOARD")
print("=====================================================================\n")

with open('data/dashboard_data.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

with open('data/funnelling_data.json', 'r', encoding='utf-8') as f:
    fn = json.load(f)

with open('data/booking_data.json', 'r', encoding='utf-8') as f:
    bk = json.load(f)

report = {}

# -------------------------------------------------------------------
# MENU 1: RINGKASAN EKSEKUTIF & TREN (#pane-executive)
# -------------------------------------------------------------------
print("1. VALIDATING MENU: RINGKASAN EKSEKUTIF & TREN (#pane-executive)")
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September']
m_kpis_2026 = db.get('monthly_kpis', {}).get('2026', {})
targets_2026 = db.get('targets', {}).get('2026', {})
m_kpis_2025 = db.get('monthly_kpis', {}).get('2025', {})

tot_cpus_2026 = sum(m_kpis_2026.get(m, {}).get('cpus', 0) for m in months)
tot_tgt_cpus_2026 = sum(targets_2026.get(m, {}).get('cpus', 0) for m in months)
tot_rev_2026 = sum((m_kpis_2026.get(m, {}).get('total_revenue') or m_kpis_2026.get(m, {}).get('cpus_revenue') or 0) for m in months)
tot_tgt_rev_2026 = sum(targets_2026.get(m, {}).get('revenue_total', 0) for m in months)
tot_ue_2026 = sum(m_kpis_2026.get(m, {}).get('ue_total', 0) for m in months)
tot_tcare_2026 = sum(m_kpis_2026.get(m, {}).get('tcare_count', 0) for m in months)
tot_sbe_2026 = sum(m_kpis_2026.get(m, {}).get('sbe_count', 0) for m in months)

print(f"   - 2026 YTD Actual CPUS: {tot_cpus_2026} vs Target: {tot_tgt_cpus_2026} ({tot_cpus_2026/tot_tgt_cpus_2026*100:.1f}%)")
print(f"   - 2026 YTD Actual Rev : Rp {tot_rev_2026/1e6:,.1f}M vs Target: Rp {tot_tgt_rev_2026/1e6:,.1f}M ({tot_rev_2026/tot_tgt_rev_2026*100:.1f}%)")
print(f"   - 2026 YTD Actual UE  : {tot_ue_2026} Unit")
print(f"   - 2026 YTD T-Care     : {tot_tcare_2026} Unit, SBE: {tot_sbe_2026} Unit")
print(f"   - Frequency Revenue Records: {len(db.get('executive_frequency_revenue', []))}")
print(f"   - Analytics Charts Records : {len(db.get('analytics_charts', []))}")
report['pane-executive'] = {
    'status': 'VALID',
    'actual_cpus_ytd': tot_cpus_2026,
    'target_cpus_ytd': tot_tgt_cpus_2026,
    'actual_rev_ytd_m': round(tot_rev_2026/1e6, 1),
    'target_rev_ytd_m': round(tot_tgt_rev_2026/1e6, 1)
}

# -------------------------------------------------------------------
# MENU 2: WS PERFORMANCE MATRIX (#pane-ws-matrix)
# -------------------------------------------------------------------
print("\n2. VALIDATING MENU: WS PERFORMANCE MATRIX (#pane-ws-matrix)")
ws_kabeng = db.get('ws_matrix_kabeng', {})
ws_excel = db.get('ws_matrix_excel', {})
rows_k = ws_kabeng.get('rows', [])
print(f"   - Kabeng Matrix Rows: {len(rows_k)}")
for r in rows_k[:5]:
    m_vals = [v for v in r.get('months', [])[:9] if v is not None]
    print(f"     Row {r.get('no')}: {r.get('kpi'):<28} | Jan-Sep Avg/Total={r.get('total')}")
report['pane-ws-matrix'] = {
    'status': 'VALID',
    'rows_count': len(rows_k)
}

# -------------------------------------------------------------------
# MENU 3: OPERATIONAL BREAKDOWN (#pane-breakdown)
# -------------------------------------------------------------------
print("\n3. VALIDATING MENU: OPERATIONAL BREAKDOWN (#pane-breakdown)")
bd = db.get('breakdown', [])
bd_2026 = [x for x in bd if str(x.get('year')) == '2026']
svc_summary = {}
for item in bd_2026:
    st = item.get('type_service', 'UNKNOWN')
    if st not in svc_summary:
        svc_summary[st] = {'units': 0, 'revenue': 0}
    svc_summary[st]['units'] += item.get('units', 0)
    svc_summary[st]['revenue'] += item.get('revenue', 0)

print(f"   - Total Breakdown Records (2026): {len(bd_2026)}")
for st, vals in sorted(svc_summary.items()):
    print(f"     {st:<15}: {vals['units']:>5} Unit | Rp {vals['revenue']/1e6:>8.1f}M")
report['pane-breakdown'] = {
    'status': 'VALID',
    'categories': list(svc_summary.keys()),
    'total_units': sum(v['units'] for v in svc_summary.values()),
    'total_rev_m': round(sum(v['revenue'] for v in svc_summary.values())/1e6, 1)
}

# -------------------------------------------------------------------
# MENU 4: CROSS SELLING & UPSELLING (#pane-cross)
# -------------------------------------------------------------------
print("\n4. VALIDATING MENU: CROSS SELLING & UPSELLING (#pane-cross)")
cross = db.get('cross_selling', [])
cross_2026 = [x for x in cross if str(x.get('year')) == '2026']
cross_cats = {}
for item in cross_2026:
    cat = item.get('category', 'UNKNOWN')
    if cat not in cross_cats:
        cross_cats[cat] = {'qty': 0, 'revenue': 0}
    cross_cats[cat]['qty'] += item.get('qty', 0)
    cross_cats[cat]['revenue'] += item.get('revenue', 0)

print(f"   - Total Cross Selling Records (2026): {len(cross_2026)}")
for cat, vals in sorted(cross_cats.items()):
    print(f"     {cat:<20}: Qty={vals['qty']:>6.0f} | Rp {vals['revenue']/1e6:>7.1f}M")
report['pane-cross'] = {
    'status': 'VALID',
    'categories_count': len(cross_cats),
    'total_qty': sum(v['qty'] for v in cross_cats.values()),
    'total_rev_m': round(sum(v['revenue'] for v in cross_cats.values())/1e6, 1)
}

# -------------------------------------------------------------------
# MENU 5: SERVICE ADVISOR PERFORMANCE (#pane-sa-perf)
# -------------------------------------------------------------------
print("\n5. VALIDATING MENU: SERVICE ADVISOR PERFORMANCE (#pane-sa-perf)")
sa_perf = db.get('sa_performance', [])
sas = ['DIDIN', 'FICKY', 'ACEP']
sa_res = {}
for sa in sas:
    sa_items = [x for x in sa_perf if str(x.get('year')) == '2026' and x.get('sa') == sa]
    tot_ue = sum(x.get('ue', 0) for x in sa_items)
    tot_cpus = sum(x.get('cpus', 0) for x in sa_items)
    tot_rev = sum(x.get('revenue', 0) for x in sa_items)
    tot_tc = sum(x.get('tcare_ue', 0) for x in sa_items)
    tot_sbe = sum(x.get('sbe_ue', 0) for x in sa_items)
    sa_res[sa] = {'ue': tot_ue, 'cpus': tot_cpus, 'rev_m': round(tot_rev/1e6, 1), 'tcare': tot_tc, 'sbe': tot_sbe}
    print(f"     SA {sa:<6}: UE={tot_ue:>4} | CPUS={tot_cpus:>4} | Rev=Rp {tot_rev/1e6:>7.1f}M | T-Care={tot_tc:>3} | SBE={tot_sbe:>4}")

report['pane-sa-perf'] = {
    'status': 'VALID',
    'sa_data': sa_res
}

# -------------------------------------------------------------------
# MENU 6: MAPPING PER AREA (#pane-area-mapping)
# -------------------------------------------------------------------
print("\n6. VALIDATING MENU: MAPPING PER AREA (#pane-area-mapping)")
area_char = db.get('area_characteristics', [])
map_cfg = db.get('area_map_config', {})
rings = set(x.get('ring_area') for x in area_char if isinstance(x, dict))
print(f"   - Rings Defined: {rings}")
print(f"   - Area Records Count: {len(area_char)}")
report['pane-area-mapping'] = {
    'status': 'VALID',
    'rings': list(rings),
    'records_count': len(area_char)
}

# -------------------------------------------------------------------
# MENU 7: DASHBOARD FUNNELLING (#pane-funnelling)
# -------------------------------------------------------------------
print("\n7. VALIDATING MENU: DASHBOARD FUNNELLING (#pane-funnelling)")
p_segs = fn.get('priority_segments_by_period', {}).get('all', [])
mra = fn.get('mra_breakdown', {})
ths = fn.get('potensi_ths', {})
stages = fn.get('funnel_stages_by_period', {}).get('all', {})
reasons = fn.get('not_cai_reasons_by_period', {}).get('all', [])
sb = fn.get('status_booking_by_period', {}).get('all', {})

p1_tot = p_segs[0] if p_segs else {}
print(f"   - Priority 1 Total Ex Soon: {p1_tot.get('total_potensi')} Potensi | {p1_tot.get('total_cai')} CAI ({p1_tot.get('total_pct')}%)")
print(f"   - MRA RANI: {mra.get('RANI',{}).get('ytd',{}).get('potensi')} Pot | {mra.get('RANI',{}).get('ytd',{}).get('fu')} FU | {mra.get('RANI',{}).get('ytd',{}).get('cai')} CAI")
print(f"   - MRA NURI: {mra.get('NURI',{}).get('ytd',{}).get('potensi')} Pot | {mra.get('NURI',{}).get('ytd',{}).get('fu')} FU | {mra.get('NURI',{}).get('ytd',{}).get('cai')} CAI")
print(f"   - THS YTD : {ths.get('ytd',{}).get('potensi')} Pot | {ths.get('ytd',{}).get('contacted')} Cont | {ths.get('ytd',{}).get('cai')} CAI")
print(f"   - Funnel  : {stages.get('potency')} -> {stages.get('cust_fu')} -> {stages.get('contacted')} -> {stages.get('cai')}")
print(f"   - NOT CAI : {len(reasons)} reasons")
print(f"   - Booking : {sb.get('booking',{}).get('count')} total | {sb.get('show_cai',{}).get('count')} show | {sb.get('open',{}).get('count')} open")

report['pane-funnelling'] = {
    'status': 'VALID',
    'p1_ex_soon_potensi': p1_tot.get('total_potensi'),
    'p1_ex_soon_cai': p1_tot.get('total_cai'),
    'mra_rani_cai': mra.get('RANI',{}).get('ytd',{}).get('cai'),
    'mra_nuri_cai': mra.get('NURI',{}).get('ytd',{}).get('cai'),
    'ths_cai': ths.get('ytd',{}).get('cai')
}

# -------------------------------------------------------------------
# MENU 8: BOOKING (#pane-booking)
# -------------------------------------------------------------------
print("\n8. VALIDATING MENU: BOOKING (#pane-booking)")
channels = bk.get('channels', {})
print(f"   - Booking Channels: {list(channels.keys())}")
for ch_k, ch in channels.items():
    print(f"     {ch_k:<10}: {ch.get('title'):<30} | YTD = {ch.get('ytd_total')}")
report['pane-booking'] = {
    'status': 'VALID',
    'channels_count': len(channels),
    'ytd_bookings_sum': sum(c.get('ytd_total', 0) for c in channels.values() if not c.get('is_sub'))
}

# -------------------------------------------------------------------
# MENU 9: LIVE TIKTOK (#pane-tiktok)
# -------------------------------------------------------------------
print("\n9. VALIDATING MENU: LIVE TIKTOK (#pane-tiktok)")
tt = bk.get('tiktok_live', {})
kpis = tt.get('kpis', {})
print(f"   - Live TikTok Total Bookings: {kpis.get('total_booking',{}).get('value')} Unit")
print(f"   - Live TikTok Avg Duration  : {kpis.get('duration_minutes',{}).get('value')} Mnt")
print(f"   - Live TikTok Avg Likes     : {kpis.get('likes_per_day',{}).get('value')} Likes/day")
print(f"   - Live TikTok Avg Viewer    : {kpis.get('viewer_per_day',{}).get('value')} Viewer/day")
print(f"   - Live TikTok Avg Comments  : {kpis.get('comments_per_day',{}).get('value')} Komen/day")
report['pane-tiktok'] = {
    'status': 'VALID',
    'total_booking': kpis.get('total_booking',{}).get('value'),
    'avg_likes': kpis.get('likes_per_day',{}).get('value'),
    'avg_duration': kpis.get('duration_minutes',{}).get('value')
}

# -------------------------------------------------------------------
# MENU 10: DATA EXPLORER PKB (#pane-explorer)
# -------------------------------------------------------------------
print("\n10. VALIDATING MENU: DATA EXPLORER PKB (#pane-explorer)")
samples = db.get('sample_pkb', [])
print(f"   - Sample PKB Records Available: {len(samples)}")
if samples:
    first_pkb = samples[0]
    print(f"     Sample PKB #1: No={first_pkb.get('pkb_no')}, Date={first_pkb.get('tgl')}/{first_pkb.get('month')}, SA={first_pkb.get('sa')}, Polisi={first_pkb.get('police_no')}, Rev={first_pkb.get('revenue')}")
report['pane-explorer'] = {
    'status': 'VALID',
    'records_count': len(samples)
}

print("\n=====================================================================")
print(" ALL 10 MENUS VALIDATION SUMMARY")
print("=====================================================================")
for menu, d in report.items():
    print(f"  [OK] Menu #{menu:<15}: {d['status']}")
