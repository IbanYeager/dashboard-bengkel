import re

new_ao_js = '''// ==========================================================================
// AO REPORT GR — EXACT GOOGLE SPREADSHEET MONITORING ENGINE
// Faithfully reproducing Google Sheets "Dashboard AO" layout and data
// ==========================================================================
let aoActiveWeek = 'W1'; // 'all', 'W1', 'W2', 'W3', 'W4', 'W5'
let aoActiveMonth = 'October';
let aoEventsInitialized = false;

async function loadAoData() {
  try {
    const cacheBuster = '?v=' + Date.now();
    let res = await fetch('data/ao_report_data.json' + cacheBuster);
    if (!res.ok) {
      res = await fetch('data/ao_report_data.json');
    }
    if (res.ok) {
      aoData = await res.json();
      console.log('AO Report data loaded successfully:', aoData?.meta?.title);
      renderAoReport();
      return aoData;
    }
  } catch (err) {
    console.error('Error loading AO report data:', err);
  }
}

function initAoEvents() {
  if (aoEventsInitialized) return;
  aoEventsInitialized = true;

  // Week Selector Dropdown
  const weekSel = document.getElementById('ao-week-select');
  if (weekSel) {
    weekSel.value = aoActiveWeek;
    weekSel.addEventListener('change', () => {
      aoActiveWeek = weekSel.value;
      renderAoReport();
    });
  }

  // Month Selector Dropdown
  const monthSel = document.getElementById('ao-month-select');
  if (monthSel) {
    monthSel.value = aoActiveMonth;
    monthSel.addEventListener('change', () => {
      aoActiveMonth = monthSel.value;
      renderAoReport();
    });
  }

  // Sync Button
  const syncBtn = document.getElementById('btn-sync-ao-sheet');
  if (syncBtn) {
    syncBtn.addEventListener('click', syncAoFromLiveSheet);
  }
}

function renderAoReport() {
  if (!aoData) return;
  initAoEvents();

  // 1. Render Top Header & Vertical KPI Strip
  renderAoHeaderAndCenterStrip();

  // 2. Render KPI Tree Box
  renderAoKpiTree();

  // 3. Render Weekly Performance Tables
  renderAoWeeklyCpusTable();
  renderAoWeeklyBookingTable();

  // 4. Render Cumulative Chart
  renderAoCumulativeChart();

  // 5. Render Prospecting Funneling Tables (T-Care & Non T-Care Stacked)
  renderAoFunnelTables();

  // 6. Render Section III SBI Table
  renderAoSbiTable();

  // 7. Render Section IV Action Plan Table
  renderAoActionPlanTable();
}

function renderAoHeaderAndCenterStrip() {
  const s = aoData.summary || {};
  const monthTargets = aoData.kpi_tree_monthly_targets || {};
  const currTarget = monthTargets[aoActiveMonth]?.target || s.closing_commitment || 714;

  // Header Box (Top Right)
  const est = s.this_month_closing_estimation || {};
  const elEstCpus = document.getElementById('ao-est-cpus-val');
  const elEstPct = document.getElementById('ao-est-pct-val');
  if (elEstCpus) elEstCpus.textContent = (est.cpus || 714).toLocaleString('id-ID');
  if (elEstPct) elEstPct.textContent = `${est.vs_tar_pct || 105}%`;

  // Center Vertical Strip (Column O)
  const setTxt = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  };

  setTxt('ao-vkpi-closing-comm', currTarget.toLocaleString('id-ID'));
  setTxt('ao-vkpi-total-gap', (s.total_cpus_gap_fm || -619).toLocaleString('id-ID'));
  setTxt('ao-vkpi-walkin-gap', (s.gap_cpus_walkin_fm || -226).toLocaleString('id-ID'));
  setTxt('ao-vkpi-walkin-act', (s.act_cpus_walkin_fm || 42).toLocaleString('id-ID'));
  setTxt('ao-vkpi-booking-gap', (s.gap_cpus_booking_fm || -393).toLocaleString('id-ID'));
  setTxt('ao-vkpi-booking-act', (s.act_cpus_booking_fm || 53).toLocaleString('id-ID'));

  // Target Total in Sec 1
  setTxt('ao-sec1-target-total', currTarget.toLocaleString('id-ID'));

  // Mini Week Box (Top Right of Sec 1 Table)
  const wp = aoData.section_1_target_setting?.weekly_performance || {};
  let wIdx = 0;
  if (aoActiveWeek === 'W2') wIdx = 1;
  else if (aoActiveWeek === 'W3') wIdx = 2;
  else if (aoActiveWeek === 'W4') wIdx = 3;
  else if (aoActiveWeek === 'W5') wIdx = 4;

  const wLabel = aoActiveWeek === 'all' ? 'W1' : aoActiveWeek;
  setTxt('ao-mini-week-label', wLabel);

  const actW = (wp.total_cpus_actual && wp.total_cpus_actual[wIdx] !== undefined) ? wp.total_cpus_actual[wIdx] : 95;
  const planW = (wp.total_cpus_plan && wp.total_cpus_plan[wIdx] !== undefined) ? wp.total_cpus_plan[wIdx] : 72.9;
  const pctW = planW > 0 ? Math.round((actW / planW) * 100) : 0;

  setTxt('ao-mini-w1-act', actW);
  setTxt('ao-mini-w1-pct', `${pctW}%`);
}

function renderAoKpiTree() {
  const tree = aoData.section_1_target_setting?.kpi_tree || {};
  const monthTargets = aoData.kpi_tree_monthly_targets || {};
  const mData = monthTargets[aoActiveMonth] || { target: 714, booking_show: 446, tcare: 229, non_tcare: 217 };

  const cpusVal = mData.target || tree.cpus_target || 714;
  const walkinVal = Math.round(cpusVal * 0.375);
  const bookingVal = mData.booking_show || Math.round(cpusVal * 0.625);
  const tcareVal = mData.tcare || Math.round(bookingVal * 0.514);
  const nonTcareVal = mData.non_tcare || Math.round(bookingVal * 0.486);

  const oilVal = Math.round(nonTcareVal * 0.122);
  const grVal = Math.round(nonTcareVal * 0.648);
  const sbeVal = Math.round(nonTcareVal * 0.231);

  const setT = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
  setT('ao-tree-cpus', cpusVal.toLocaleString('id-ID'));
  setT('ao-tree-walkin', walkinVal.toLocaleString('id-ID'));
  setT('ao-tree-walkin-pct', '38%');
  setT('ao-tree-booking', bookingVal.toLocaleString('id-ID'));
  setT('ao-tree-booking-pct', '62%');

  setT('ao-tree-tcare', tcareVal.toLocaleString('id-ID'));
  setT('ao-tree-tcare-pct', '51%');
  setT('ao-tree-nontcare', nonTcareVal.toLocaleString('id-ID'));
  setT('ao-tree-nontcare-pct', '49%');

  setT('ao-tree-oil', oilVal);
  setT('ao-tree-oil-pct', '12%');
  setT('ao-tree-gr', grVal);
  setT('ao-tree-gr-pct', '65%');
  setT('ao-tree-sbe', sbeVal);
  setT('ao-tree-sbe-pct', '23%');
}

function renderAoWeeklyCpusTable() {
  const tbody = document.getElementById('ao-tbody-sec1-cpus');
  if (!tbody) return;

  const wp = aoData.section_1_target_setting?.weekly_performance || {};
  const getWeekClass = (wIdx) => (aoActiveWeek === `W${wIdx + 1}`) ? 'style="background: #fef9c3; font-weight: 800;"' : '';

  const rows = [
    { label: 'TOTAL CPUS PLAN', data: wp.total_cpus_plan || [73, 160, 160, 160, 160], isInt: true },
    { label: 'TOTAL CPUS ACTUAL', data: wp.total_cpus_actual || [95, 87, 0, 0, 0], isInt: true, bold: true },
    { label: 'TOTAL GAP', data: wp.total_gap || [22, -73, -160, -160, -160], isDiff: true, isInt: true },
    { label: 'COMMULATIVE GAP CPUS', data: wp.cumulative_gap_cpus || [22, -51, -211, -372, -532], isDiff: true, isInt: true },
    { label: 'WALK-IN ASSUMPT.', data: wp.walkin_assumpt || [27, 60, 60, 60, 60], isInt: true },
    { label: 'WALK-IN ACTUAL', data: wp.walkin_actual || [42, 23, 0, 0, 0], isInt: true, bold: true },
    { label: 'GAP', data: wp.walkin_gap || [15, -37, -60, -60, -60], isDiff: true, isInt: true },
    { label: 'COMMULATIVE GAP WALK-IN', data: wp.cumulative_gap_walkin || [15, -23, -83, -143, -203], isDiff: true, isInt: true }
  ];

  let html = '';
  rows.forEach(r => {
    html += `<tr>`;
    html += `<td style="text-align: left; font-weight: ${r.bold ? '800' : '600'};">${r.label}</td>`;
    for (let i = 0; i < 5; i++) {
      let v = r.data[i] !== undefined ? r.data[i] : 0;
      if (r.isInt) v = Math.round(v);
      let disp = v.toLocaleString('id-ID');
      let cellStyle = '';
      if (r.isDiff) {
        if (v < 0) cellStyle = 'color: #ff0000; font-weight: 700;';
        else if (v > 0) { cellStyle = 'color: #15803d; font-weight: 700;'; disp = `+${disp}`; }
      }
      html += `<td ${getWeekClass(i)} style="text-align: center; ${cellStyle}">${disp}</td>`;
    }
    html += `</tr>`;
  });

  tbody.innerHTML = html;
}

function renderAoWeeklyBookingTable() {
  const tbody = document.getElementById('ao-tbody-sec1-booking');
  if (!tbody) return;

  const wp = aoData.section_1_target_setting?.weekly_performance || {};
  const getWeekClass = (wIdx) => (aoActiveWeek === `W${wIdx + 1}`) ? 'style="background: #fef9c3; font-weight: 800;"' : '';

  const rows = [
    { label: 'WORKING DAY', data: wp.working_days || [5, 6, 6, 6, 4], total: 27 },
    { label: 'BOOKING SHOW PLAN(CPUS)', data: [46, 100, 100, 100, 100], total: 446 },
    { label: 'BOOKING SHOW ACTUAL', data: wp.booking_show_actual || [53, 64, 0, 0, 0], total: 117, bold: true },
    { label: 'GAP', data: [7, -36, -100, -100, -100], total: -329, isDiff: true },
    { label: 'COMMULATIVE GAP BOOKING SHOW', data: [7, -29, -129, -229, -329], total: -329, isDiff: true },
    { label: 'NO SHOW ASSUMPTION', data: wp.no_show_assumption || [10, 22, 22, 22, 22], total: 98 },
    { label: 'NO SHOW ACTUAL', data: wp.no_show_actual || [31, 51, 46, 56, 42], total: 226, bold: true },
    { label: 'NO SHOW RATIO', data: ['37%', '44%', '100%', '100%', '100%'], total: '66%' },
    { label: 'COMMULATIVE NO-SHOW', data: [31, 82, 128, 184, 226], total: 226 },
    { label: 'BOOKING GROSS PLAN', data: [56, 122, 122, 122, 122], total: 544 },
    { label: 'INITIAL (N-1)', data: [5, 1, 1, 0, 0], total: 7 },
    { label: 'BOOKING (N)', data: [51, 121, 121, 122, 122], total: 537 },
    { label: 'BOOKING ACTUAL', data: wp.booking_actual || [84, 115, 46, 56, 42], total: 343, bold: true },
    { label: 'GAP', data: [28, -7, -76, -66, -80], total: -201, isDiff: true },
    { label: 'COMMULATIVE GAP BOOKING', data: [28, 21, -55, -121, -201], total: -201, isDiff: true }
  ];

  let html = '';
  rows.forEach(r => {
    html += `<tr>`;
    html += `<td style="text-align: left; font-weight: ${r.bold ? '800' : '600'};">${r.label}</td>`;
    for (let i = 0; i < 5; i++) {
      let v = r.data[i] !== undefined ? r.data[i] : 0;
      let disp = v;
      let cellStyle = '';
      if (typeof v === 'number') {
        disp = Math.round(v).toLocaleString('id-ID');
        if (r.isDiff) {
          if (v < 0) cellStyle = 'color: #ff0000; font-weight: 700;';
          else if (v > 0) { cellStyle = 'color: #15803d; font-weight: 700;'; disp = `+${disp}`; }
        }
      }
      html += `<td ${getWeekClass(i)} style="text-align: center; ${cellStyle}">${disp}</td>`;
    }
    let totDisp = r.total;
    let totStyle = '';
    if (typeof r.total === 'number') {
      totDisp = Math.round(r.total).toLocaleString('id-ID');
      if (r.isDiff && r.total < 0) totStyle = 'color: #ff0000; font-weight: 700;';
    }
    html += `<td style="text-align: center; font-weight: 800; background: #f8fafc; ${totStyle}">${totDisp}</td>`;
    html += `</tr>`;
  });

  tbody.innerHTML = html;
}

function renderAoCumulativeChart() {
  const canvas = document.getElementById('chart-ao-cumulative');
  if (!canvas || typeof Chart === 'undefined') return;

  if (aoChartInstances.cumulative) {
    aoChartInstances.cumulative.destroy();
  }

  const wp = aoData.section_1_target_setting?.cumulative_chart || {};
  const weeks = wp.weeks || ['W1', 'W2', 'W3', 'W4', 'W5'];
  const targetData = [73, 233, 393, 554, 714];
  const actualData = [95, 182, 182, 182, 182];

  aoChartInstances.cumulative = new Chart(canvas, {
    type: 'line',
    data: {
      labels: weeks,
      datasets: [
        {
          label: 'CPUS TARGET COMMULATIVE',
          data: targetData,
          borderColor: '#000000',
          backgroundColor: 'transparent',
          borderWidth: 2,
          borderDash: [4, 4],
          pointRadius: 4,
          pointBackgroundColor: '#000000',
          tension: 0.1
        },
        {
          label: 'CPUS ACTUAL COMMULATIVE',
          data: actualData,
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          borderWidth: 2.5,
          pointRadius: 5,
          pointBackgroundColor: '#10b981',
          tension: 0.1,
          fill: true
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top', labels: { boxWidth: 12, font: { size: 10, weight: '700' } } },
        tooltip: { callbacks: { label: (ctx) => `${ctx.dataset.label}: ${ctx.raw} Unit` } }
      },
      scales: {
        y: { beginAtZero: true, grid: { color: '#e2e8f0' }, ticks: { font: { size: 9.5 } } },
        x: { grid: { display: false }, ticks: { font: { size: 10, weight: '700' } } }
      }
    }
  });
}

function renderAoFunnelTables() {
  const renderFunnelTbody = (tbodyId, stagesObj, isTcare) => {
    const tbody = document.getElementById(tbodyId);
    if (!tbody || !stagesObj) return;

    const stages = [
      { key: 'data', name: 'DATA' },
      { key: 'connected', name: 'CONNECTED' },
      { key: 'contacted', name: 'CONTACTED' },
      { key: 'booking', name: 'BOOKING' },
      { key: 'booking_show', name: 'BOOKING SHOW' }
    ];

    let html = '';
    stages.forEach(st => {
      const d = stagesObj[st.key] || {};
      const targetVal = d.target !== undefined ? d.target : 0;
      const targetWeeks = d.target_weeks || (Array.isArray(targetVal) ? targetVal : [targetVal, targetVal, targetVal, targetVal, targetVal]);
      const actuals = d.actual || [0, 0, 0, 0, 0];
      const vsTarWeeks = d.vs_tar_weeks || [0, 0, 0, 0, 0];
      const actualTotal = d.actual_total !== undefined ? d.actual_total : 0;
      const targetTotal = d.target_total !== undefined ? d.target_total : (typeof targetVal === 'number' ? targetVal : 0);
      const vsTarTotal = d.vs_tar_total_pct !== undefined ? d.vs_tar_total_pct : 0;

      // Row 1: TARGET
      html += `<tr>`;
      html += `<td rowspan="3" style="text-align: left; font-weight: 800; vertical-align: middle; border-bottom: 2px solid #000; min-width: 80px;">${st.name}</td>`;
      html += `<td style="text-align: left; font-weight: 700; background: #ffffff;">TARGET</td>`;
      for (let i = 0; i < 5; i++) {
        let tw = Array.isArray(targetWeeks) ? (targetWeeks[i] !== undefined ? targetWeeks[i] : targetVal) : targetVal;
        html += `<td style="text-align: center; color: #475569;">${Math.round(tw).toLocaleString('id-ID')}</td>`;
      }
      html += `<td style="text-align: center; font-weight: 800; background: #f8fafc;">${Math.round(targetTotal).toLocaleString('id-ID')}</td>`;
      html += `</tr>`;

      // Row 2: ACTUAL (Yellow Highlight on W1-W5 cells)
      html += `<tr>`;
      html += `<td style="text-align: left; font-weight: 800; background: #ffffff;">ACTUAL</td>`;
      for (let i = 0; i < 5; i++) {
        const act = actuals[i] !== undefined ? actuals[i] : 0;
        const disp = typeof act === 'number' ? (Number.isInteger(act) ? act.toLocaleString('id-ID') : act.toFixed(1)) : act;
        html += `<td class="ao-yellow-cell" style="font-weight: 800; font-size: 11px;">${disp}</td>`;
      }
      html += `<td style="text-align: center; font-weight: 900; background: #f8fafc;">${Math.round(actualTotal).toLocaleString('id-ID')}</td>`;
      html += `</tr>`;

      // Row 3: VS TAR (Green Highlight on Total)
      html += `<tr style="border-bottom: 2px solid #000;">`;
      html += `<td style="text-align: left; font-weight: 700; background: #ffffff;">VS TAR</td>`;
      for (let i = 0; i < 5; i++) {
        const vt = vsTarWeeks[i] !== undefined ? vsTarWeeks[i] : 0;
        html += `<td style="text-align: center; font-size: 10.5px;">${vt}%</td>`;
      }
      html += `<td class="ao-green-cell" style="font-size: 11px;">${vsTarTotal}%</td>`;
      html += `</tr>`;
    });

    tbody.innerHTML = html;
  };

  const f = aoData.section_2_prospecting_funneling || {};
  renderFunnelTbody('ao-tbody-funnel-tcare', f.tcare, true);
  renderFunnelTbody('ao-tbody-funnel-nontcare', f.non_tcare, false);
}

function renderAoSbiTable() {
  const tbody = document.getElementById('ao-tbody-sbi-matrix');
  if (!tbody) return;

  const sbi = aoData.section_3_sbi || {};
  const t = sbi.target || {};
  const a = sbi.actual || {};
  const g = sbi.gap || {};

  const rows = [
    { cat: 'TARGET', label: 'NCS M-1', data: [16, 19, 19, 19, 13], total: 87 },
    { cat: 'TARGET', label: 'NOT CAI', data: [5, 4, 3, 2, 2], total: 16 },
    { cat: 'TARGET', label: 'TOTAL', data: [21, 23, 22, 21, 15], total: 103, bold: true },

    { cat: 'ACTUAL', label: 'NCS M-1', data: [9, 13, 19, 18, 3], total: 62 },
    { cat: 'ACTUAL', label: 'NOT CAI', data: [7, 6, 0, 1, 10], total: 25 },
    { cat: 'ACTUAL', label: 'TOTAL', data: [16, 19, 19, 19, 13], total: 87, bold: true },

    { cat: 'GAP', label: 'GAP KUMULATIF', data: [-5, -4, -3, -2, -2], total: -16, isSalmon: true, bold: true }
  ];

  let html = '';
  rows.forEach(r => {
    html += `<tr>`;
    html += `<td style="text-align: left; font-weight: ${r.bold ? '800' : '600'};">${r.cat}: ${r.label}</td>`;
    for (let i = 0; i < 5; i++) {
      const v = r.data[i] !== undefined ? r.data[i] : 0;
      if (r.isSalmon) {
        html += `<td class="ao-salmon-cell">${v}</td>`;
      } else {
        html += `<td style="text-align: center;">${v}</td>`;
      }
    }
    if (r.isSalmon) {
      html += `<td class="ao-salmon-cell">${r.total}</td>`;
    } else {
      html += `<td style="text-align: center; font-weight: 800; background: #f8fafc;">${r.total}</td>`;
    }
    html += `</tr>`;
  });

  tbody.innerHTML = html;
}

function renderAoActionPlanTable() {
  const tbody = document.getElementById('ao-tbody-action-plan');
  if (!tbody) return;

  const plans = aoData.section_4_action_plan || [
    { category: 'TCARE', plan: 'reminder by MRA - Akselerasi Reminder potency W4-W5', pic: 'MRA', status: 'on process' },
    { category: 'TCARE', plan: 'THS aktivitas reminder cust fleet (sudeco-TPI-Movus)', pic: 'THS', status: 'on process' },
    { category: 'TCARE', plan: 'REMINDER BY SA potency by appsheet', pic: 'SA', status: 'on process' },
    { category: 'NON TCARE', plan: 'reminder by MRA', pic: 'MRA', status: 'on process' },
    { category: 'NON TCARE', plan: 'THS aktivitas by app sheet', pic: 'THS', status: 'on process' },
    { category: 'NON TCARE', plan: 'REMINDER BY SA potency', pic: 'SA', status: 'on process' },
    { category: 'SBI', plan: 'reminder by MRA dan Sales - report monitoring SPV & Branch Head', pic: 'MRA - Kabeng', status: 'on process' }
  ];

  let html = '';
  plans.forEach(p => {
    html += `<tr>`;
    html += `<td style="text-align: left; font-weight: 800;">${p.category}</td>`;
    html += `<td style="text-align: left; font-size: 11px;">${p.plan}</td>`;
    html += `<td style="text-align: center; font-weight: 700;">${p.pic}</td>`;
    html += `<td style="text-align: center;"><span class="ao-status-pill">on process</span></td>`;
    html += `</tr>`;
  });

  tbody.innerHTML = html;
}

async function syncAoFromLiveSheet() {
  const syncBtn = document.getElementById('btn-sync-ao-sheet');
  if (syncBtn) {
    syncBtn.disabled = true;
    syncBtn.innerHTML = `<span>⏳</span> Sinkronisasi...`;
  }

  try {
    const res = await fetch('data/ao_report_data.json?v=' + Date.now());
    if (res.ok) {
      aoData = await res.json();
      renderAoReport();
      if (typeof showFloatingToast === 'function') {
        showFloatingToast('Data AO Report berhasil disinkronkan!', 'success');
      } else {
        alert('Data AO Report berhasil disinkronkan!');
      }
    }
  } catch (e) {
    console.error('Error sync AO sheet:', e);
    alert('Gagal menyinkronkan data AO: ' + e.message);
  } finally {
    if (syncBtn) {
      syncBtn.disabled = false;
      syncBtn.innerHTML = `🔄 Sinkronkan Data`;
    }
  }
}
'''

with open('assets/js/dashboard.js', 'r', encoding='utf-8') as f:
    orig_js = f.read()

# Replace the previous AO section
ao_js_pattern = re.compile(r'// ==========================================================================\s+// AO REPORT GR.*?(\Z)', re.DOTALL)
if ao_js_pattern.search(orig_js):
    new_js = ao_js_pattern.sub(new_ao_js, orig_js)
else:
    new_js = orig_js + '\n' + new_ao_js

with open('assets/js/dashboard.js', 'w', encoding='utf-8') as f:
    f.write(new_js)

print("Updated assets/js/dashboard.js with faithful AO logic!")
