import json
import csv
import math

print("===============================================================")
print(" COMPREHENSIVE DATA AUDIT & VALIDATION FOR DASHBOARD BENGKEL")
print("===============================================================\n")

issues_found = []

# =====================================================================
# 1. AUDIT FUNNELLING DATA (data/funnelling_data.json)
# =====================================================================
print("--- 1. AUDITING FUNNELLING DATA ---")
try:
    with open('data/funnelling_data.json', 'r', encoding='utf-8') as f:
        fn_data = json.load(f)
    
    periods = list(fn_data.get('periods', {}).keys())
    print(f"Periods found in funnelling_data.json: {periods}")
    
    for p in periods:
        p_data = fn_data['periods'][p]
        mra = p_data.get('mra_pic', {})
        ths = p_data.get('ths', {})
        p_segs = p_data.get('priority_segments', {})
        funnel = p_data.get('funnel_stages', {})
        dropoffs = p_data.get('dropoff_reasons', [])
        sas = p_data.get('sa_breakdown', {})
        
        # Check MRA PIC
        for pic in ['RANI', 'NURI']:
            pic_d = mra.get(pic, {})
            pot = pic_d.get('potensi', 0)
            fu = pic_d.get('fu', 0)
            cai = pic_d.get('cai', 0)
            if fu > pot:
                issues_found.append(f"[Funnelling - {p}] {pic}: FU ({fu}) > Potensi ({pot})")
            if cai > fu:
                issues_found.append(f"[Funnelling - {p}] {pic}: CAI ({cai}) > FU ({fu})")
                
        # Check Priority Segments
        p1 = p_segs.get('priority_1', {})
        p2 = p_segs.get('priority_2', {})
        p3 = p_segs.get('priority_3', {})
        p4 = p_segs.get('priority_4', {})
        
        # Check Priority 1 (Expired Soon)
        p1_tot = p1.get('total', {})
        p1_calc_pot = sum(v.get('potensi', 0) for k, v in p1.items() if k != 'total')
        p1_calc_cai = sum(v.get('cai', 0) for k, v in p1.items() if k != 'total')
        if p1_tot.get('potensi', 0) != p1_calc_pot:
            issues_found.append(f"[Funnelling - {p}] Priority 1 total potensi mismatch: {p1_tot.get('potensi')} != {p1_calc_pot}")
        if p1_tot.get('cai', 0) != p1_calc_cai:
            issues_found.append(f"[Funnelling - {p}] Priority 1 total cai mismatch: {p1_tot.get('cai')} != {p1_calc_cai}")
            
        # Check Priority 2 (Active)
        p2_tot = p2.get('total', {})
        p2_calc_pot = sum(v.get('potensi', 0) for k, v in p2.items() if k != 'total')
        p2_calc_cai = sum(v.get('cai', 0) for k, v in p2.items() if k != 'total')
        if p2_tot.get('potensi', 0) != p2_calc_pot:
            issues_found.append(f"[Funnelling - {p}] Priority 2 total potensi mismatch: {p2_tot.get('potensi')} != {p2_calc_pot}")
            
        # Check Priority 3 (CRT)
        p3_tot = p3.get('total', {})
        p3_calc_pot = sum(v.get('potensi', 0) for k, v in p3.items() if k != 'total')
        p3_calc_cai = sum(v.get('cai', 0) for k, v in p3.items() if k != 'total')
        if p3_tot.get('potensi', 0) != p3_calc_pot:
            issues_found.append(f"[Funnelling - {p}] Priority 3 total potensi mismatch: {p3_tot.get('potensi')} != {p3_calc_pot}")
            
        # Check Overall Total
        tot_all = p_segs.get('total_overall', {})
        expected_all_pot = p1_tot.get('potensi', 0) + p2_tot.get('potensi', 0) + p3_tot.get('potensi', 0) + p4.get('total', {}).get('potensi', 0)
        expected_all_cai = p1_tot.get('cai', 0) + p2_tot.get('cai', 0) + p3_tot.get('cai', 0) + p4.get('total', {}).get('cai', 0)
        if tot_all.get('potensi', 0) != expected_all_pot:
            issues_found.append(f"[Funnelling - {p}] Overall total potensi mismatch: {tot_all.get('potensi')} != {expected_all_pot}")
        if tot_all.get('cai', 0) != expected_all_cai:
            issues_found.append(f"[Funnelling - {p}] Overall total cai mismatch: {tot_all.get('cai')} != {expected_all_cai}")

        print(f"  Period '{p}': Overall Potensi={tot_all.get('potensi')}, CAI={tot_all.get('cai')}, P1 ExSoon={p1_tot.get('potensi')} Pot/{p1_tot.get('cai')} CAI")

except Exception as e:
    issues_found.append(f"Funnelling audit error: {e}")


# =====================================================================
# 2. AUDIT BOOKING DATA (data/booking_data.json)
# =====================================================================
print("\n--- 2. AUDITING BOOKING DATA ---")
try:
    with open('data/booking_data.json', 'r', encoding='utf-8') as f:
        bk_data = json.load(f)
    
    channels = bk_data.get('channels', {})
    total_ytd_all_channels = sum(ch.get('ytd_total', 0) for ch in channels.values())
    print(f"Total YTD Bookings (Jan-Sep): {total_ytd_all_channels}")
    
    for ch_name, ch in channels.items():
        m_vals = ch.get('monthly', [])
        # Check that months 9, 10, 11 (Oct, Nov, Dec) are None/null
        for idx in [9, 10, 11]:
            if idx < len(m_vals) and m_vals[idx] is not None:
                issues_found.append(f"[Booking - {ch_name}] Month idx {idx} is not None: {m_vals[idx]}")
        # Check YTD sum
        calc_ytd = sum(v for v in m_vals if v is not None)
        if ch.get('ytd_total') != calc_ytd:
            issues_found.append(f"[Booking - {ch_name}] YTD total mismatch: {ch.get('ytd_total')} != {calc_ytd}")
            
    # Check TikTok Live Monthly
    tt_live = bk_data.get('tiktok_live', {})
    print(f"TikTok Live YTD Bookings: {tt_live.get('ytd_bookings')}")
    print(f"TikTok Live Total Sessions: {tt_live.get('total_sessions')}")
    for item in tt_live.get('monthly_trend', []):
        m = item.get('month')
        if m in ['Okt', 'Nov', 'Des']:
            if item.get('booking') is not None or item.get('has_data') is not False:
                issues_found.append(f"[Booking - TikTok Live] Month {m} has non-null data: {item}")
        else:
            if item.get('has_data') is not True:
                issues_found.append(f"[Booking - TikTok Live] Month {m} has_data is False")

except Exception as e:
    issues_found.append(f"Booking audit error: {e}")


# =====================================================================
# 3. AUDIT DASHBOARD DATA (data/dashboard_data.json)
# =====================================================================
print("\n--- 3. AUDITING DASHBOARD DATA ---")
try:
    with open('data/dashboard_data.json', 'r', encoding='utf-8') as f:
        db_data = json.load(f)
        
    monthly_kpis = db_data.get('monthly_kpis', {})
    targets = db_data.get('targets', {})
    
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September']
    
    # 3.1 Check 2026 Actuals vs Targets
    print("\n2026 Monthly Summary (Actual vs Target):")
    for m in months:
        act = monthly_kpis.get('2026', {}).get(m, {})
        tgt = targets.get('2026', {}).get(m, {})
        
        act_ue = act.get('ue_total', 0)
        act_cpus = act.get('cpus', 0)
        act_rev = act.get('total_revenue') or act.get('cpus_revenue') or 0
        
        tgt_cpus = tgt.get('cpus', 0)
        tgt_rev = tgt.get('revenue_total', 0)
        
        # Check sanity
        if act_cpus > act_ue:
            issues_found.append(f"[Dashboard 2026 - {m}] CPUS ({act_cpus}) > UE ({act_ue})")
        if tgt_cpus <= 0:
            issues_found.append(f"[Dashboard 2026 - {m}] Target CPUS is 0 or negative: {tgt_cpus}")
        if tgt_rev <= 0:
            issues_found.append(f"[Dashboard 2026 - {m}] Target Revenue is 0 or negative: {tgt_rev}")
            
        achieve_rev = (act_rev / tgt_rev * 100) if tgt_rev > 0 else 0
        achieve_cpus = (act_cpus / tgt_cpus * 100) if tgt_cpus > 0 else 0
        
        print(f"  {m:<10} | UE: {act_ue:>4} | CPUS: {act_cpus:>4} / {tgt_cpus:>4} ({achieve_cpus:>5.1f}%) | Rev: Rp {act_rev/1e6:>7.1f}M / Rp {tgt_rev/1e6:>7.1f}M ({achieve_rev:>5.1f}%)")

    # 3.2 Check 2025 Actuals vs Targets
    print("\n2025 Monthly Summary (Actual vs Target):")
    for m in ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']:
        act = monthly_kpis.get('2025', {}).get(m, {})
        tgt = targets.get('2025', {}).get(m, {})
        act_cpus = act.get('cpus', 0)
        tgt_cpus = tgt.get('cpus', 0)
        act_rev = act.get('total_revenue') or act.get('cpus_revenue') or 0
        tgt_rev = tgt.get('revenue_total', 0)
        achieve_rev = (act_rev / tgt_rev * 100) if tgt_rev > 0 else 0
        achieve_cpus = (act_cpus / tgt_cpus * 100) if tgt_cpus > 0 else 0
        print(f"  {m:<10} | CPUS: {act_cpus:>4} / {tgt_cpus:>4} ({achieve_cpus:>5.1f}%) | Rev: Rp {act_rev/1e6:>7.1f}M / Rp {tgt_rev/1e6:>7.1f}M ({achieve_rev:>5.1f}%)")

    # 3.3 Check SA Performance in dashboard_data.json
    sa_perf = db_data.get('sa_performance', [])
    print(f"\nSA Performance Records: {len(sa_perf)}")
    for sa_name in ['DIDIN', 'FICKY', 'ACEP']:
        sa_2026 = [x for x in sa_perf if str(x.get('year')) == '2026' and x.get('sa') == sa_name]
        tot_ue = sum(x.get('ue', 0) for x in sa_2026)
        tot_cpus = sum(x.get('cpus', 0) for x in sa_2026)
        tot_rev = sum(x.get('revenue', 0) for x in sa_2026)
        print(f"  SA {sa_name:<6}: {len(sa_2026)} months | UE: {tot_ue} | CPUS: {tot_cpus} | Rev: Rp {tot_rev/1e6:,.1f}M")

    # 3.4 Check Cross Selling
    cross = db_data.get('cross_selling', [])
    print(f"\nCross Selling Records: {len(cross)}")
    cross_2026 = [x for x in cross if str(x.get('year')) == '2026']
    categories = set(x.get('category') for x in cross_2026)
    print(f"  Categories in 2026: {categories}")
    for cat in sorted(categories):
        cat_items = [x for x in cross_2026 if x.get('category') == cat]
        tot_qty = sum(x.get('qty', 0) for x in cat_items)
        tot_rev = sum(x.get('revenue', 0) for x in cat_items)
        print(f"    {cat:<20}: Qty = {tot_qty:>6} | Rev = Rp {tot_rev/1e6:>8.1f}M")

    # 3.5 Check SBE Breakdown
    bd = db_data.get('breakdown', [])
    bd_2026 = [x for x in bd if str(x.get('year')) == '2026']
    svc_types = set(x.get('type_service') for x in bd_2026)
    print(f"\nOperational Breakdown Service Types (2026): {svc_types}")
    for st in sorted(svc_types):
        st_items = [x for x in bd_2026 if x.get('type_service') == st]
        tot_u = sum(x.get('units', 0) for x in st_items)
        tot_r = sum(x.get('revenue', 0) for x in st_items)
        print(f"    {st:<20}: Units = {tot_u:>6} | Rev = Rp {tot_r/1e6:>8.1f}M")

except Exception as e:
    issues_found.append(f"Dashboard data audit error: {e}")

# =====================================================================
# 4. SUMMARY OF AUDIT
# =====================================================================
print("\n===============================================================")
print(f" AUDIT COMPLETE: {len(issues_found)} POTENTIAL ISSUES DETECTED")
print("===============================================================")
if issues_found:
    for iss in issues_found:
        print(f"  [!] {iss}")
else:
    print("  [OK] All internal data checks and balances PASSED!")
