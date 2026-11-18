with open('assets/js/dashboard.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Update getRowMonth Q4 detection to scan for nov/des/dec
old_q4_part = '''    const q = r[0] ? r[0].trim() : '';
    if (q === '1') return 'Q1';
    if (q === '2') return 'Q2';
    if (q === '3') return 'Q3';
    if (q === '4') return 'Okt';
    return 'unknown';'''

new_q4_part = '''    const q = r[0] ? r[0].trim() : '';
    if (q === '1') return 'Q1';
    if (q === '2') return 'Q2';
    if (q === '3') return 'Q3';
    if (q === '4') {
      const rowStr = r.join(' ').toLowerCase();
      if (rowStr.includes('des') || rowStr.includes('dec')) return 'Des';
      if (rowStr.includes('nov')) return 'Nov';
      return 'Okt';
    }
    return 'unknown';'''

assert old_q4_part in js, "old_q4_part not found"
js = js.replace(old_q4_part, new_q4_part)

# 2. Update processLiveAttacklistCSV to handle all 12 months dynamically
old_body = '''  const monthsList = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agt', 'Sep', 'Okt'];
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
  }

  const funnelStagesByPeriod = {};
  const notCaiReasonsByPeriod = {};
  const prioritySegmentsByPeriod = {};

  for (const [pKey, pSubset] of Object.entries(periodRows)) {
    const stg = computeFunnelStages(pSubset);
    funnelStagesByPeriod[pKey] = stg;
    notCaiReasonsByPeriod[pKey] = computeNotCaiReasons(pSubset, stg.cust_fu);
    prioritySegmentsByPeriod[pKey] = buildPrioritySegments(pSubset);
  }

  const monthIdNames = {
    Jan: 'Januari', Feb: 'Februari', Mar: 'Maret', Apr: 'April',
    Mei: 'Mei', Jun: 'Juni', Jul: 'Juli', Agt: 'Agustus', Sep: 'September',
    Okt: 'Oktober', Nov: 'November', Des: 'Desember'
  };

  const monthlySummary = monthsList.map(m => {
    const stg = funnelStagesByPeriod[m];
    return {
      month: m,
      month_name: monthIdNames[m] || m,
      cust_fu: stg.cust_fu,
      contacted: stg.contacted,
      cai: stg.cai,
      has_data: true
    };
  });

  for (const m of ['Nov', 'Des']) {
    monthlySummary.push({
      month: m,
      month_name: monthIdNames[m] || m,
      cust_fu: 0,
      contacted: 0,
      cai: 0,
      has_data: false
    });
  }

  // SA Breakdown
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
  });'''

new_body = '''  const all12Months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agt', 'Sep', 'Okt', 'Nov', 'Des'];
  const periodRows = { all: dataRows };
  for (const q of ['1', '2', '3', '4']) {
    periodRows[`Q${q}`] = dataRows.filter(r => r[0] && r[0].trim() === q);
  }
  // Q4 includes any rows that map to Okt, Nov, or Des
  for (const r of dataRows) {
    const rm = getRowMonth(r);
    if (['Okt', 'Nov', 'Des'].includes(rm) && !periodRows['Q4'].includes(r)) {
      periodRows['Q4'].push(r);
    }
  }
  for (const m of all12Months) {
    periodRows[m] = dataRows.filter(r => getRowMonth(r) === m);
  }

  const funnelStagesByPeriod = {};
  const notCaiReasonsByPeriod = {};
  const prioritySegmentsByPeriod = {};

  for (const [pKey, pSubset] of Object.entries(periodRows)) {
    const stg = computeFunnelStages(pSubset);
    funnelStagesByPeriod[pKey] = stg;
    notCaiReasonsByPeriod[pKey] = computeNotCaiReasons(pSubset, stg.cust_fu);
    prioritySegmentsByPeriod[pKey] = buildPrioritySegments(pSubset);
  }

  const monthIdNames = {
    Jan: 'Januari', Feb: 'Februari', Mar: 'Maret', Apr: 'April',
    Mei: 'Mei', Jun: 'Juni', Jul: 'Juli', Agt: 'Agustus', Sep: 'September',
    Okt: 'Oktober', Nov: 'November', Des: 'Desember'
  };

  const monthlySummary = all12Months.map(m => {
    const stg = funnelStagesByPeriod[m] || { cust_fu: 0, contacted: 0, cai: 0 };
    const hasData = (stg.cust_fu > 0 || stg.potency > 0);
    return {
      month: m,
      month_name: monthIdNames[m] || m,
      cust_fu: stg.cust_fu || 0,
      contacted: stg.contacted || 0,
      cai: stg.cai || 0,
      has_data: hasData
    };
  });

  // SA Breakdown for all 12 months dynamically
  const saNames = ['DIDIN', 'FICKY', 'ACEP'];
  const saRaw = { DIDIN: {}, FICKY: {}, ACEP: {} };
  saNames.forEach(sa => {
    all12Months.forEach(m => { saRaw[sa][m] = { potensi: 0, contacted: 0, cai: 0 }; });
  });

  dataRows.forEach(r => {
    const m = getRowMonth(r);
    if (!all12Months.includes(m)) return;
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
  all12Months.forEach(m => {
    totCaiPerMonth[m] = saNames.reduce((acc, sa) => acc + saRaw[sa][m].cai, 0);
    totContPerMonth[m] = saNames.reduce((acc, sa) => acc + saRaw[sa][m].contacted, 0);
  });

  const saBreakdown = {};
  saNames.forEach(sa => {
    saBreakdown[sa] = {
      monthly: all12Months.map(m => {
        const caiVal = saRaw[sa][m].cai;
        const totC = totCaiPerMonth[m] || 0;
        const mStg = funnelStagesByPeriod[m] || { cust_fu: 0 };
        const hasData = (mStg.cust_fu > 0 || mStg.potency > 0);
        return {
          month: m,
          potensi: saRaw[sa][m].potensi,
          contacted: saRaw[sa][m].contacted,
          cai: caiVal,
          contrib_pct: totC > 0 ? parseFloat(((caiVal / totC) * 100).toFixed(1)) : 0,
          has_data: hasData
        };
      })
    };
  });

  saBreakdown['ALL'] = {
    monthly: all12Months.map(m => {
      const totC = totCaiPerMonth[m] || 0;
      const mStg = funnelStagesByPeriod[m] || { cust_fu: 0 };
      const hasData = (mStg.cust_fu > 0 || mStg.potency > 0);
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
        has_data: hasData
      };
    })
  };

  // Ring & Fleet trend for all 12 months dynamically
  const ringMonthly = {};
  const fleetMonthly = {};
  all12Months.forEach(m => {
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
    if (!all12Months.includes(m)) return;
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
  });'''

assert old_body in js, "old_body not found"
js = js.replace(old_body, new_body)

# 3. Dynamic months in renderFunnelRingAndFleetCharts
old_ring_months = "const months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agt', 'Sep', 'Okt'];"
new_ring_months = """const all12 = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agt', 'Sep', 'Okt', 'Nov', 'Des'];
  const activeMonthsList = all12.filter(m => {
    const r = ringTrend[m];
    const f = fleetTrend[m];
    return (r && (r['Ring 1']?.cust_fu > 0 || r['Ring 2']?.cust_fu > 0 || r['Ring 3']?.cust_fu > 0 || r['Out of Area']?.cust_fu > 0)) ||
           (f && (f['Retail']?.cust_fu > 0 || f['Fleet']?.cust_fu > 0));
  });
  const months = activeMonthsList.length > 0 ? activeMonthsList : ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agt', 'Sep', 'Okt'];"""

assert old_ring_months in js, "old_ring_months not found"
js = js.replace(old_ring_months, new_ring_months)

# 4. Dynamic SA table title and footer based on latest active month
old_sa_title = "tableTitle.textContent = isAll\n      ? 'Ringkasan Kinerja 3 SA (Jan - Okt)'\n      : `SA ${saName} — Ringkasan Bulanan`;"
new_sa_title = """const activeSummaryMonths = (funnellingData?.monthly_summary || []).filter(s => s.has_data !== false && s.cust_fu > 0);
  const lastActiveMonth = activeSummaryMonths.length > 0 ? activeSummaryMonths[activeSummaryMonths.length - 1].month : 'Okt';

  const tableTitle = document.getElementById('sa-table-title');
  if (tableTitle) {
    tableTitle.textContent = isAll
      ? `Ringkasan Kinerja 3 SA (Jan - ${lastActiveMonth})`
      : `SA ${saName} — Ringkasan Bulanan`;
  }"""

assert old_sa_title in js, "old_sa_title not found"
js = js.replace(old_sa_title, new_sa_title)

old_sa_footer = "<td>TOTAL (Jan - Okt)</td>"
new_sa_footer = "<td>TOTAL (Jan - ${lastActiveMonth})</td>"
js = js.replace(old_sa_footer, new_sa_footer)

# 5. Dynamic Q4 in getSaStats in renderAIAdvisor
old_q_advisor = "const qMonths = period === 'Q1' ? ['Jan','Feb','Mar'] : (period === 'Q2' ? ['Apr','Mei','Jun'] : (period === 'Q3' ? ['Jul','Agt','Sep'] : ['Okt']));"
new_q_advisor = "const qMonths = period === 'Q1' ? ['Jan','Feb','Mar'] : (period === 'Q2' ? ['Apr','Mei','Jun'] : (period === 'Q3' ? ['Jul','Agt','Sep'] : ['Okt','Nov','Des']));"
assert old_q_advisor in js, "old_q_advisor not found"
js = js.replace(old_q_advisor, new_q_advisor)

# 6. Make TikTok table dynamic footer
old_tt_foot = "<td>TOTAL / RATA-RATA (Jan - Sep)</td>"
new_tt_foot = "<td>TOTAL / RATA-RATA (YTD)</td>"
if old_tt_foot in js:
    js = js.replace(old_tt_foot, new_tt_foot)

with open('assets/js/dashboard.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("assets/js/dashboard.js updated for dynamic future months!")
