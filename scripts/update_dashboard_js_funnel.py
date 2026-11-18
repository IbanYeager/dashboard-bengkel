with open('assets/js/dashboard.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Update getRowMonth and processLiveAttacklistCSV
target_get_row_month = '''  const getRowMonth = (r) => {
    const b = r[15] ? r[15].trim() : '';
    const months = [
      ['Jan','Jan'], ['Feb','Feb'], ['Mar','Mar'], ['Apr','Apr'],
      ['Mei','Mei'], ['May','Mei'], ['Jun','Jun'], ['Jul','Jul'],
      ['Agu','Agt'], ['Aug','Agt'], ['Sep','Sep']
    ];
    for (const [m, k] of months) {
      if (b.includes(m)) return k;
    }
    const fu = r[39] ? r[39].trim() : '';
    for (const [m, k] of months) {
      if (fu.includes(m)) return k;
    }
    const q = r[0] ? r[0].trim() : '';
    if (q === '1') return 'Q1';
    if (q === '2') return 'Q2';
    if (q === '3') return 'Q3';
    return 'unknown';
  };'''

replacement_get_row_month = '''  const getRowMonth = (r) => {
    const b = r[15] ? r[15].trim() : '';
    const months = [
      ['Jan','Jan'], ['Feb','Feb'], ['Mar','Mar'], ['Apr','Apr'],
      ['Mei','Mei'], ['May','Mei'], ['Jun','Jun'], ['Jul','Jul'],
      ['Agu','Agt'], ['Aug','Agt'], ['Sep','Sep'],
      ['Okt','Okt'], ['Oct','Okt'], ['Nov','Nov'], ['Des','Des']
    ];
    for (const [m, k] of months) {
      if (b.includes(m)) return k;
    }
    const fu = r[39] ? r[39].trim() : '';
    for (const [m, k] of months) {
      if (fu.includes(m)) return k;
    }
    const nsm = r[55] ? r[55].trim() : '';
    if (nsm.includes('2026-10') || nsm.includes('10/')) return 'Okt';
    if (nsm.includes('2026-11') || nsm.includes('11/')) return 'Nov';
    if (nsm.includes('2026-12') || nsm.includes('12/')) return 'Des';

    const q = r[0] ? r[0].trim() : '';
    if (q === '1') return 'Q1';
    if (q === '2') return 'Q2';
    if (q === '3') return 'Q3';
    if (q === '4') return 'Okt';
    return 'unknown';
  };'''

assert target_get_row_month in js, "target_get_row_month not found in dashboard.js"
js = js.replace(target_get_row_month, replacement_get_row_month)

# 2. Update monthsList and periodRows in processLiveAttacklistCSV
target_months_list = '''  const monthsList = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agt', 'Sep'];
  const periodRows = { all: dataRows };
  for (const q of ['1', '2', '3']) {
    periodRows[`Q${q}`] = dataRows.filter(r => r[0] && r[0].trim() === q);
  }
  for (const m of monthsList) {
    periodRows[m] = dataRows.filter(r => getRowMonth(r) === m);
  }'''

replacement_months_list = '''  const monthsList = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agt', 'Sep', 'Okt'];
  const periodRows = { all: dataRows };
  for (const q of ['1', '2', '3', '4']) {
    periodRows[`Q${q}`] = dataRows.filter(r => r[0] && r[0].trim() === q);
  }
  for (const r of dataRows) {
    if (getRowMonth(r) === 'Okt' && !periodRows['Q4'].includes(r)) {
      periodRows['Q4'].push(r);
    }
  }
  for (const m of monthsList) {
    periodRows[m] = dataRows.filter(r => getRowMonth(r) === m);
  }'''

assert target_months_list in js, "target_months_list not found in dashboard.js"
js = js.replace(target_months_list, replacement_months_list)

# 3. Update monthlySummary placeholders in processLiveAttacklistCSV
target_placeholders = '''  for (const m of ['Okt', 'Nov', 'Des']) {
    monthlySummary.push({
      month: m,
      month_name: monthIdNames[m] || m,
      cust_fu: 0,
      contacted: 0,
      cai: 0,
      has_data: false
    });
  }'''

replacement_placeholders = '''  for (const m of ['Nov', 'Des']) {
    monthlySummary.push({
      month: m,
      month_name: monthIdNames[m] || m,
      cust_fu: 0,
      contacted: 0,
      cai: 0,
      has_data: false
    });
  }'''

assert target_placeholders in js, "target_placeholders not found in dashboard.js"
js = js.replace(target_placeholders, replacement_placeholders)

# 4. In processLiveAttacklistCSV: compute sa_breakdown, mra_breakdown, potensi_ths, ring, fleet
target_return = '''  return {
    total_rows: dataRows.length,
    monthly_summary: monthlySummary,
    funnel_stages: funnelStagesByPeriod['all'],
    funnel_stages_by_period: funnelStagesByPeriod,
    not_cai_reasons: notCaiReasonsByPeriod['all'],
    not_cai_reasons_by_period: notCaiReasonsByPeriod,
    priority_segments: prioritySegmentsByPeriod['all'],
    priority_segments_by_period: prioritySegmentsByPeriod
  };'''

replacement_return = '''  // SA Breakdown
  const saNames = ['DIDIN', 'FICKY', 'ACEP'];
  const all12Months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agt', 'Sep', 'Okt', 'Nov', 'Des'];
  const saRaw = { DIDIN: {}, FICKY: {}, ACEP: {} };
  saNames.forEach(sa => {
    monthsList.forEach(m => { saRaw[sa][m] = { potensi: 0, contacted: 0, cai: 0 }; });
  });

  dataRows.forEach(r => {
    const m = getRowMonth(r);
    if (!monthsList.includes(m)) return;
    const saCol = (r[76] || '').toUpperCase();
    const isCont = r[3] && r[3].toUpperCase().includes('CONTACTED');
    const isCai = r[4] && r[4].trim().toUpperCase() === 'CAI';
    saNames.forEach(sa => {
      if (saCol.includes(sa)) {
        saRaw[sa][m].potensi++;
        if (isCont) saRaw[sa][m].contacted++;
        if (isCai) saRaw[sa][m].cai++;
      }
    });
  });

  const totCaiPerMonth = {};
  const totContPerMonth = {};
  monthsList.forEach(m => {
    totCaiPerMonth[m] = saNames.reduce((acc, sa) => acc + saRaw[sa][m].cai, 0);
    totContPerMonth[m] = saNames.reduce((acc, sa) => acc + saRaw[sa][m].contacted, 0);
  });

  const saBreakdown = {};
  saNames.forEach(sa => {
    saBreakdown[sa] = {
      monthly: all12Months.map(m => {
        if (monthsList.includes(m)) {
          const caiVal = saRaw[sa][m].cai;
          const totC = totCaiPerMonth[m] || 0;
          return {
            month: m,
            potensi: saRaw[sa][m].potensi,
            contacted: saRaw[sa][m].contacted,
            cai: caiVal,
            contrib_pct: totC > 0 ? parseFloat(((caiVal / totC) * 100).toFixed(1)) : 0,
            has_data: true
          };
        }
        return { month: m, potensi: 0, contacted: 0, cai: 0, contrib_pct: 0, has_data: false };
      })
    };
  });

  saBreakdown['ALL'] = {
    monthly: all12Months.map(m => {
      if (monthsList.includes(m)) {
        const totC = totCaiPerMonth[m] || 0;
        return {
          month: m,
          contacted: totContPerMonth[m] || 0,
          cai: totC,
          contrib_pct: 100.0,
          didin_cai: saRaw['DIDIN'][m].cai,
          didin_cnt: saRaw['DIDIN'][m].contacted,
          didin_contrib: totC ? parseFloat(((saRaw['DIDIN'][m].cai / totC) * 100).toFixed(1)) : 0,
          ficky_cai: saRaw['FICKY'][m].cai,
          ficky_cnt: saRaw['FICKY'][m].contacted,
          ficky_contrib: totC ? parseFloat(((saRaw['FICKY'][m].cai / totC) * 100).toFixed(1)) : 0,
          acep_cai: saRaw['ACEP'][m].cai,
          acep_cnt: saRaw['ACEP'][m].contacted,
          acep_contrib: totC ? parseFloat(((saRaw['ACEP'][m].cai / totC) * 100).toFixed(1)) : 0,
          has_data: true
        };
      }
      return { month: m, contacted: 0, cai: 0, contrib_pct: 0, didin_cai: 0, didin_cnt: 0, didin_contrib: 0, ficky_cai: 0, ficky_cnt: 0, ficky_contrib: 0, acep_cai: 0, acep_cnt: 0, acep_contrib: 0, has_data: false };
    })
  };

  // Ring & Fleet trend
  const ringMonthly = {};
  const fleetMonthly = {};
  monthsList.forEach(m => {
    ringMonthly[m] = {
      'Ring 1': { cust_fu: 0, connected: 0 },
      'Ring 2': { cust_fu: 0, connected: 0 },
      'Ring 3': { cust_fu: 0, connected: 0 },
      'Out of Area': { cust_fu: 0, connected: 0 }
    };
    fleetMonthly[m] = {
      'Retail': { cust_fu: 0, connected: 0 },
      'Fleet': { cust_fu: 0, connected: 0 }
    };
  });

  dataRows.forEach(r => {
    const m = getRowMonth(r);
    if (!monthsList.includes(m)) return;
    const isConn = r[2] && r[2].toUpperCase().includes('CONNECTED');
    const areaRaw = (r[27] || '').toUpperCase();
    let area = 'Out of Area';
    if (areaRaw.includes('1')) area = 'Ring 1';
    else if (areaRaw.includes('2')) area = 'Ring 2';
    else if (areaRaw.includes('3')) area = 'Ring 3';

    const fltRaw = (r[28] || '').toUpperCase();
    const flt = (fltRaw.includes('FLEET') || fltRaw.includes('SUDECO') || fltRaw.includes('TPI')) ? 'Fleet' : 'Retail';

    ringMonthly[m][area].cust_fu++;
    if (isConn) ringMonthly[m][area].connected++;
    fleetMonthly[m][flt].cust_fu++;
    if (isConn) fleetMonthly[m][flt].connected++;
  });

  return {
    total_rows: dataRows.length,
    monthly_summary: monthlySummary,
    funnel_stages: funnelStagesByPeriod['all'],
    funnel_stages_by_period: funnelStagesByPeriod,
    not_cai_reasons: notCaiReasonsByPeriod['all'],
    not_cai_reasons_by_period: notCaiReasonsByPeriod,
    priority_segments: prioritySegmentsByPeriod['all'],
    priority_segments_by_period: prioritySegmentsByPeriod,
    sa_breakdown: saBreakdown,
    monthly_ring_area_trend: ringMonthly,
    monthly_fleet_retail_trend: fleetMonthly
  };'''

assert target_return in js, "target_return not found in dashboard.js"
js = js.replace(target_return, replacement_return)

# 5. In background sync around line 4774
target_sync_assign = '''          funnellingData.priority_segments = parsed.priority_segments;
          funnellingData.priority_segments_by_period = parsed.priority_segments_by_period;
          funnellingData.updated_at = new Date().toISOString();'''

replacement_sync_assign = '''          funnellingData.priority_segments = parsed.priority_segments;
          funnellingData.priority_segments_by_period = parsed.priority_segments_by_period;
          if (parsed.sa_breakdown) funnellingData.sa_breakdown = parsed.sa_breakdown;
          if (parsed.monthly_ring_area_trend) funnellingData.monthly_ring_area_trend = parsed.monthly_ring_area_trend;
          if (parsed.monthly_fleet_retail_trend) funnellingData.monthly_fleet_retail_trend = parsed.monthly_fleet_retail_trend;
          funnellingData.updated_at = new Date().toISOString();'''

assert target_sync_assign in js, "target_sync_assign not found in dashboard.js"
js = js.replace(target_sync_assign, replacement_sync_assign)

# 6. Update renderFunnelRingAndFleetCharts months array
target_ring_months = '''  const ringTrend = funnellingData.monthly_ring_area_trend || {};
  const fleetTrend = funnellingData.monthly_fleet_retail_trend || {};
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agt', 'Sep'];'''

replacement_ring_months = '''  const ringTrend = funnellingData.monthly_ring_area_trend || {};
  const fleetTrend = funnellingData.monthly_fleet_retail_trend || {};
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agt', 'Sep', 'Okt'];'''

assert target_ring_months in js, "target_ring_months not found in dashboard.js"
js = js.replace(target_ring_months, replacement_ring_months)

# 7. Update renderPotensiMraAndThs quarterly check
target_pot_q1 = "} else if (['Q1', 'Q2', 'Q3'].includes(selectedPeriod)) {"
replacement_pot_q1 = "} else if (['Q1', 'Q2', 'Q3', 'Q4'].includes(selectedPeriod)) {"
js = js.replace(target_pot_q1, replacement_pot_q1)

# 8. Update table title and footer in renderSAFunnelSpecial
target_sa_title = "tableTitle.textContent = isAll\n      ? 'Ringkasan Kinerja 3 SA (Jan - Sep)'\n      : `SA ${saName} — Ringkasan Bulanan`;"
replacement_sa_title = "tableTitle.textContent = isAll\n      ? 'Ringkasan Kinerja 3 SA (Jan - Okt)'\n      : `SA ${saName} — Ringkasan Bulanan`;"
js = js.replace(target_sa_title, replacement_sa_title)

js = js.replace('<td>TOTAL (Jan-Sep)</td>', '<td>TOTAL (Jan - Okt)</td>')

# 9. Update periodLabels in renderFunnelModules & renderAIAdvisor
target_period_labels = '''  const periodLabels = {
    'all': 'Semua Periode (YTD)',
    'Q1': 'Kuartal 1 (Jan-Mar)',
    'Q2': 'Kuartal 2 (Apr-Jun)',
    'Q3': 'Kuartal 3 (Jul-Sep)',
    'Jan': 'Januari',
    'Feb': 'Februari',
    'Mar': 'Maret',
    'Apr': 'April',
    'Mei': 'Mei',
    'Jun': 'Juni',
    'Jul': 'Juli',
    'Agt': 'Agustus',
    'Sep': 'September'
  };'''

replacement_period_labels = '''  const periodLabels = {
    'all': 'Semua Periode (YTD)',
    'Q1': 'Kuartal 1 (Jan-Mar)',
    'Q2': 'Kuartal 2 (Apr-Jun)',
    'Q3': 'Kuartal 3 (Jul-Sep)',
    'Q4': 'Kuartal 4 (Okt-Des)',
    'Jan': 'Januari',
    'Feb': 'Februari',
    'Mar': 'Maret',
    'Apr': 'April',
    'Mei': 'Mei',
    'Jun': 'Juni',
    'Jul': 'Juli',
    'Agt': 'Agustus',
    'Sep': 'September',
    'Okt': 'Oktober'
  };'''

js = js.replace(target_period_labels, replacement_period_labels)

# 10. In renderAIAdvisor getSaStats
target_q_months = "const qMonths = period === 'Q1' ? ['Jan','Feb','Mar'] : (period === 'Q2' ? ['Apr','Mei','Jun'] : ['Jul','Agt','Sep']);"
replacement_q_months = "const qMonths = period === 'Q1' ? ['Jan','Feb','Mar'] : (period === 'Q2' ? ['Apr','Mei','Jun'] : (period === 'Q3' ? ['Jul','Agt','Sep'] : ['Okt']));"
assert target_q_months in js, "target_q_months not found in dashboard.js"
js = js.replace(target_q_months, replacement_q_months)

with open('assets/js/dashboard.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("assets/js/dashboard.js successfully updated for October & Q4 funnelling!")
