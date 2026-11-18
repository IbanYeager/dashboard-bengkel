import re

js_file = 'assets/js/dashboard.js'
with open(js_file, 'r', encoding='utf-8') as f:
    content = f.read()

# -------------------------------------------------------------------
# 1. Update updateExecutiveSummary
# -------------------------------------------------------------------
old_exec_target = """  // Calculate Metrics
  const cpusAchieve = targetCPUS > 0 ? actualCPUS / targetCPUS : 0;
  const cpusGrowth = lyCPUS > 0 ? (actualCPUS - lyCPUS) / lyCPUS : 0;

  const revAchieve = targetRev > 0 ? actualRev / targetRev : 0;
  const revGrowth = lyRev > 0 ? (actualRev - lyRev) / lyRev : 0;

  const revPerCPUS = actualCPUS > 0 ? actualRev / actualCPUS : 0;
  const lyRevPerCPUS = lyCPUS > 0 ? lyRev / lyCPUS : 0;
  const revPerCPUSGrowth = lyRevPerCPUS > 0 ? (revPerCPUS - lyRevPerCPUS) / lyRevPerCPUS : 0;
  const revPerCPUSAchieve = revPerCPUS / 1_500_000; // Benchmark Rp 1.5M"""

new_exec_target = """  // Calculate Metrics
  const cpusAchieve = targetCPUS > 0 ? actualCPUS / targetCPUS : 0;
  const cpusGrowth = lyCPUS > 0 ? (actualCPUS - lyCPUS) / lyCPUS : 0;

  const revAchieve = targetRev > 0 ? actualRev / targetRev : 0;
  const revGrowth = lyRev > 0 ? (actualRev - lyRev) / lyRev : 0;

  // Revisi No 2: Rumus Total Revenue dibagi Total Unit Entry (CPUS & Non CPUS)
  const revPerUnit = actualUE > 0 ? actualRev / actualUE : (actualCPUS > 0 ? actualRev / actualCPUS : 0);
  const lyRevPerUnit = lyUE > 0 ? lyRev / lyUE : (lyCPUS > 0 ? lyRev / lyCPUS : 0);
  const revPerUnitGrowth = lyRevPerUnit > 0 ? (revPerUnit - lyRevPerUnit) / lyRevPerUnit : 0;
  const revPerUnitAchieve = revPerUnit / 1_500_000; // Benchmark Rp 1.5M"""

if old_exec_target in content:
    content = content.replace(old_exec_target, new_exec_target)
    print("1a. Replaced revPerCPUS calculation with revPerUnit in updateExecutiveSummary")
else:
    print("WARNING: old_exec_target not found!")

# Update DOM update in updateExecutiveSummary
old_dom_update = """  // 3. Rev / CPUS Card
  document.getElementById('kpi-revpcpus-val').textContent = formatIDR(revPerCPUS);
  document.getElementById('kpi-revpcpus-target').textContent = 'Rp 1,5 Jt';
  document.getElementById('kpi-revpcpus-achieve').textContent = formatPct(revPerCPUSAchieve);
  document.getElementById('kpi-revpcpus-ly').textContent = formatIDR(lyRevPerCPUS);
  updateGrowthBadge('kpi-revpcpus-growth', revPerCPUSGrowth, formatPct(revPerCPUSGrowth) + ' YoY');
  updateTargetBar('kpi-revpcpus-bar', revPerCPUSAchieve * 100, 'var(--status-up)');"""

new_dom_update = """  // 3. Rev / Unit Card (Total Revenue dibagi Total Unit Entry CPUS & Non CPUS)
  document.getElementById('kpi-revpcpus-val').textContent = formatIDR(revPerUnit);
  document.getElementById('kpi-revpcpus-target').textContent = 'Rp 1,5 Jt';
  document.getElementById('kpi-revpcpus-achieve').textContent = formatPct(revPerUnitAchieve);
  document.getElementById('kpi-revpcpus-ly').textContent = formatIDR(lyRevPerUnit);
  updateGrowthBadge('kpi-revpcpus-growth', revPerUnitGrowth, formatPct(revPerUnitGrowth) + ' YoY');
  updateTargetBar('kpi-revpcpus-bar', revPerUnitAchieve * 100, 'var(--status-up)');"""

if old_dom_update in content:
    content = content.replace(old_dom_update, new_dom_update)
    print("1b. Replaced DOM update for card 3 with revPerUnit")
else:
    print("WARNING: old_dom_update not found!")

# Also add actualUE and lyUE initialization and accumulation
old_vars_decl = """  let actualCPUS = 0;
  let targetCPUS = 0;
  let lyCPUS = 0;

  let actualRev = 0;
  let targetRev = 0;
  let lyRev = 0;

  let tcareUnits = 0;
  let lyTcareUnits = 0;
  let actualSBE = 0;
  let lySBE = 0;"""

new_vars_decl = """  let actualUE = 0;
  let lyUE = 0;

  let actualCPUS = 0;
  let targetCPUS = 0;
  let lyCPUS = 0;

  let actualRev = 0;
  let targetRev = 0;
  let lyRev = 0;

  let tcareUnits = 0;
  let lyTcareUnits = 0;
  let actualSBE = 0;
  let lySBE = 0;"""

if old_vars_decl in content:
    content = content.replace(old_vars_decl, new_vars_decl)
    print("1c. Added actualUE and lyUE declarations")
else:
    print("WARNING: old_vars_decl not found!")

# Segment accumulation in updateExecutiveSummary
old_seg_acc = """    dashboardData.breakdown
      .filter(item => String(item.year) === yr && isMonthInFilter(item.month_name) && isSegmentInFilter(item.fleet_retail) && (STATE.sa === 'all' || item.sa === STATE.sa))
      .forEach(item => {
        actualCPUS += item.units || 0;
        actualRev += item.revenue || 0;
        if (item.tcare && item.tcare.toLowerCase() === 't-care') tcareUnits += item.units || 0;
        if (item.type_service && item.type_service.toUpperCase().includes('SBE')) actualSBE += item.units || 0;
      });

    dashboardData.breakdown
      .filter(item => String(item.year) === ly && isMonthInFilter(item.month_name) && isSegmentInFilter(item.fleet_retail) && (STATE.sa === 'all' || item.sa === STATE.sa))
      .forEach(item => {
        lyCPUS += item.units || 0;
        lyRev += item.revenue || 0;
        if (item.tcare && item.tcare.toLowerCase() === 't-care') lyTcareUnits += item.units || 0;
        if (item.type_service && item.type_service.toUpperCase().includes('SBE')) lySBE += item.units || 0;
      });"""

new_seg_acc = """    dashboardData.breakdown
      .filter(item => String(item.year) === yr && isMonthInFilter(item.month_name) && isSegmentInFilter(item.fleet_retail) && (STATE.sa === 'all' || item.sa === STATE.sa))
      .forEach(item => {
        actualUE += item.units || 0;
        actualCPUS += item.units || 0;
        actualRev += item.revenue || 0;
        if (item.tcare && item.tcare.toLowerCase() === 't-care') tcareUnits += item.units || 0;
        if (item.type_service && item.type_service.toUpperCase().includes('SBE')) actualSBE += item.units || 0;
      });

    dashboardData.breakdown
      .filter(item => String(item.year) === ly && isMonthInFilter(item.month_name) && isSegmentInFilter(item.fleet_retail) && (STATE.sa === 'all' || item.sa === STATE.sa))
      .forEach(item => {
        lyUE += item.units || 0;
        lyCPUS += item.units || 0;
        lyRev += item.revenue || 0;
        if (item.tcare && item.tcare.toLowerCase() === 't-care') lyTcareUnits += item.units || 0;
        if (item.type_service && item.type_service.toUpperCase().includes('SBE')) lySBE += item.units || 0;
      });"""

if old_seg_acc in content:
    content = content.replace(old_seg_acc, new_seg_acc)
    print("1d. Added actualUE and lyUE to segment filtered accumulation")
else:
    print("WARNING: old_seg_acc not found!")

# Non-segment accumulation in updateExecutiveSummary
old_nonseg_acc = """      if (STATE.sa === 'all') {
        let mCpus = curMonthData.cpus || 0;
        let mRev = (curMonthData.total_revenue !== undefined ? curMonthData.total_revenue : curMonthData.cpus_revenue) || 0;
        let mTc = curMonthData.tcare_count || 0;
        let mSbe = curMonthData.sbe_count || 0;

        // Authoritative reconciliation from ws_matrix_kabeng for 2026
        if (yr === '2026' && dashboardData.ws_matrix_kabeng?.rows) {
          const mIdx = MONTH_NAMES.indexOf(m);
          if (mIdx >= 0) {
            const sbeRow = dashboardData.ws_matrix_kabeng.rows.find(r => String(r.no) === '5' || r.kpi === 'Unit SBE Total');
            if (sbeRow && sbeRow.months?.[mIdx] !== undefined) {
              const v = Number(sbeRow.months[mIdx]) || 0;
              if (v > 0) mSbe = v;
            }
            const tcRow = dashboardData.ws_matrix_kabeng.rows.find(r => String(r.no) === '7' || r.kpi === 'SBE Tcare');
            if (tcRow && tcRow.months?.[mIdx] !== undefined) {
              const v = Number(tcRow.months[mIdx]) || 0;
              if (v > mTc) mTc = v;
            }
            const cpusRow = dashboardData.ws_matrix_kabeng.rows.find(r => String(r.no) === '2' || r.kpi === 'CPUS (PKB)');
            if (cpusRow && cpusRow.months?.[mIdx] !== undefined) {
              const v = Number(cpusRow.months[mIdx]) || 0;
              if (v > mCpus) mCpus = v;
            }
            const revRow = dashboardData.ws_matrix_kabeng.rows.find(r => String(r.no) === '12' || r.kpi === 'Revenue Total');
            if (revRow && revRow.months?.[mIdx] !== undefined) {
              const v = (Number(revRow.months[mIdx]) || 0) * 1000;
              if (v > mRev) mRev = v;
            }
          }
        }
        actualCPUS += mCpus;
        actualRev += mRev;
        tcareUnits += mTc;
        actualSBE += mSbe;
      } else {
        const saItem = dashboardData.sa_performance.find(
          item => String(item.year) === yr && item.month_name === m && item.sa === STATE.sa
        );
        if (saItem) {
          actualCPUS += saItem.cpus || 0;
          actualRev += saItem.revenue || 0;
          tcareUnits += saItem.tcare_ue || 0;
          actualSBE += saItem.sbe_ue || 0;
        }
      }"""

new_nonseg_acc = """      if (STATE.sa === 'all') {
        let mCpus = curMonthData.cpus || 0;
        let mUe = curMonthData.ue_total || curMonthData.ue || mCpus;
        let mRev = (curMonthData.total_revenue !== undefined ? curMonthData.total_revenue : curMonthData.cpus_revenue) || 0;
        let mTc = curMonthData.tcare_count || 0;
        let mSbe = curMonthData.sbe_count || 0;

        // Authoritative reconciliation from ws_matrix_kabeng for 2026
        if (yr === '2026' && dashboardData.ws_matrix_kabeng?.rows) {
          const mIdx = MONTH_NAMES.indexOf(m);
          if (mIdx >= 0) {
            const ueRow = dashboardData.ws_matrix_kabeng.rows.find(r => String(r.no) === '1' || r.kpi === 'Unit Entry');
            if (ueRow && ueRow.months?.[mIdx] !== undefined) {
              const v = Number(ueRow.months[mIdx]) || 0;
              if (v > mUe) mUe = v;
            }
            const sbeRow = dashboardData.ws_matrix_kabeng.rows.find(r => String(r.no) === '5' || r.kpi === 'Unit SBE Total');
            if (sbeRow && sbeRow.months?.[mIdx] !== undefined) {
              const v = Number(sbeRow.months[mIdx]) || 0;
              if (v > 0) mSbe = v;
            }
            const tcRow = dashboardData.ws_matrix_kabeng.rows.find(r => String(r.no) === '7' || r.kpi === 'SBE Tcare');
            if (tcRow && tcRow.months?.[mIdx] !== undefined) {
              const v = Number(tcRow.months[mIdx]) || 0;
              if (v > mTc) mTc = v;
            }
            const cpusRow = dashboardData.ws_matrix_kabeng.rows.find(r => String(r.no) === '2' || r.kpi === 'CPUS (PKB)');
            if (cpusRow && cpusRow.months?.[mIdx] !== undefined) {
              const v = Number(cpusRow.months[mIdx]) || 0;
              if (v > mCpus) mCpus = v;
            }
            const revRow = dashboardData.ws_matrix_kabeng.rows.find(r => String(r.no) === '12' || r.kpi === 'Revenue Total');
            if (revRow && revRow.months?.[mIdx] !== undefined) {
              const v = (Number(revRow.months[mIdx]) || 0) * 1000;
              if (v > mRev) mRev = v;
            }
          }
        }
        actualUE += mUe;
        actualCPUS += mCpus;
        actualRev += mRev;
        tcareUnits += mTc;
        actualSBE += mSbe;
      } else {
        const saItem = dashboardData.sa_performance.find(
          item => String(item.year) === yr && item.month_name === m && item.sa === STATE.sa
        );
        if (saItem) {
          actualUE += saItem.ue || saItem.cpus || 0;
          actualCPUS += saItem.cpus || 0;
          actualRev += saItem.revenue || 0;
          tcareUnits += saItem.tcare_ue || 0;
          actualSBE += saItem.sbe_ue || 0;
        }
      }"""

if old_nonseg_acc in content:
    content = content.replace(old_nonseg_acc, new_nonseg_acc)
    print("1e. Added actualUE to non-segment accumulation")
else:
    print("WARNING: old_nonseg_acc not found!")

# Last year accumulation in updateExecutiveSummary
old_ly_acc = """      if (STATE.sa === 'all') {
        lyCPUS += lyMonthData.cpus || 0;
        lyRev += (lyMonthData.total_revenue !== undefined ? lyMonthData.total_revenue : lyMonthData.cpus_revenue) || 0;
        lyTcareUnits += lyMonthData.tcare_count || 0;
        lySBE += lyMonthData.sbe_count || 0;
      } else {
        const saLy = dashboardData.sa_performance.find(
          item => String(item.year) === ly && item.month_name === m && item.sa === STATE.sa
        );
        if (saLy) {
          lyCPUS += saLy.cpus || 0;
          lyRev += saLy.revenue || 0;
          lyTcareUnits += saLy.tcare_ue || 0;
          lySBE += saLy.sbe_ue || 0;
        }
      }"""

new_ly_acc = """      if (STATE.sa === 'all') {
        lyUE += lyMonthData.ue_total || lyMonthData.ue || lyMonthData.cpus || 0;
        lyCPUS += lyMonthData.cpus || 0;
        lyRev += (lyMonthData.total_revenue !== undefined ? lyMonthData.total_revenue : lyMonthData.cpus_revenue) || 0;
        lyTcareUnits += lyMonthData.tcare_count || 0;
        lySBE += lyMonthData.sbe_count || 0;
      } else {
        const saLy = dashboardData.sa_performance.find(
          item => String(item.year) === ly && item.month_name === m && item.sa === STATE.sa
        );
        if (saLy) {
          lyUE += saLy.ue || saLy.cpus || 0;
          lyCPUS += saLy.cpus || 0;
          lyRev += saLy.revenue || 0;
          lyTcareUnits += saLy.tcare_ue || 0;
          lySBE += saLy.sbe_ue || 0;
        }
      }"""

if old_ly_acc in content:
    content = content.replace(old_ly_acc, new_ly_acc)
    print("1f. Added lyUE to LY accumulation")
else:
    print("WARNING: old_ly_acc not found!")

# -------------------------------------------------------------------
# 2. Replace renderSARadarCharts and renderSARadarOverlay
# -------------------------------------------------------------------
radar_start = "// -------------------------------------------------------------------\n// 4B. SERVICE ADVISOR RADAR CHARTS"
radar_end = "// -------------------------------------------------------------------\n// 5. OPERATIONAL BREAKDOWN TABLE"

radar_start_idx = content.find(radar_start)
radar_end_idx = content.find(radar_end)

if radar_start_idx != -1 and radar_end_idx != -1:
    new_radar_block = """// -------------------------------------------------------------------
// 4B. SERVICE ADVISOR RADAR CHARTS (KOMPARASI 11 KOMODITAS PRODUK: ACH BULAN VS ACH TOTAL TAHUN)
// -------------------------------------------------------------------
function renderSARadarCharts() {
  if (!dashboardData) return;

  const yr = STATE.year;
  const sas = ['DIDIN', 'FICKY', 'ACEP'];

  // 11 Komoditas Produk Sesuai Gambar 2 (Urutan Standar)
  const CANONICAL_COMMODITIES = [
    'CHEMICAL SMM', 'FULL SYNT', 'OPL CAR CARE', 'OPL AC',
    'SPOORING', 'BATTERY', 'TIRE', 'REMATCHING',
    'CROSS SELLING TAM', 'SMM OIL', 'OLI SMM'
  ];

  const METRIC_DEFS = CANONICAL_COMMODITIES.map(c => ({ key: c, label: c }));

  // Segment scaling factor if a segment filter is applied
  let segRatio = 1.0;
  if (STATE.segment !== 'all' && dashboardData.breakdown) {
    const totalYrUnits = dashboardData.breakdown.filter(item => String(item.year) === yr).reduce((s, b) => s + (b.units || 0), 0) || 1;
    const segYrUnits = dashboardData.breakdown.filter(item => String(item.year) === yr && isSegmentInFilter(item.fleet_retail)).reduce((s, b) => s + (b.units || 0), 0);
    segRatio = segYrUnits / totalYrUnits;
    if (segRatio <= 0) segRatio = 0.05;
  }

  // 1. Calculate Period & YTD commodity revenue for each SA and 3 SA Consolidated
  const totPeriod3SA = {};
  const totYtd3SA = {};
  CANONICAL_COMMODITIES.forEach(c => {
    totPeriod3SA[c] = 0;
    totYtd3SA[c] = 0;
  });

  const saRaw = {};
  sas.forEach(saName => {
    saRaw[saName] = {};
    CANONICAL_COMMODITIES.forEach(c => {
      saRaw[saName][c] = { pRev: 0, pQty: 0, ytdRev: 0, ytdQty: 0 };
    });
  });

  if (dashboardData.sa_cross_selling) {
    dashboardData.sa_cross_selling
      .filter(item => String(item.year) === yr && sas.includes(item.sa))
      .forEach(item => {
        const cat = (item.category || '').toUpperCase().trim();
        if (!CANONICAL_COMMODITIES.includes(cat)) return;
        const sa = item.sa;
        const rev = (item.revenue || 0) * (STATE.segment !== 'all' ? segRatio : 1.0);
        const qty = (item.qty || 0) * (STATE.segment !== 'all' ? segRatio : 1.0);

        // YTD
        saRaw[sa][cat].ytdRev += rev;
        saRaw[sa][cat].ytdQty += qty;
        totYtd3SA[cat] += rev;

        // Period
        if (isMonthInFilter(item.month_name)) {
          saRaw[sa][cat].pRev += rev;
          saRaw[sa][cat].pQty += qty;
          totPeriod3SA[cat] += rev;
        }
      });
  }

  // 2. Compute Achievement % for each SA across 11 commodities
  // Benchmark = Fair Share 33.333% (1/3 of total 3 SA). Share 33.3% = 100% Ach.
  const saCalculated = {};
  sas.forEach(saName => {
    const periodValues = [];
    const ytdValues = [];
    const catStats = {};

    CANONICAL_COMMODITIES.forEach(cName => {
      const raw = saRaw[saName][cName];
      const pTot = totPeriod3SA[cName] || 0;
      const ytdTot = totYtd3SA[cName] || 0;

      const pShare = pTot > 0 ? raw.pRev / pTot : 0;
      const ytdShare = ytdTot > 0 ? raw.ytdRev / ytdTot : 0;

      // Ach % vs Fair Share benchmark (1/3): 100% when share = 33.33%
      // Capped nicely at 150% max for radar rendering
      const pAch = Math.min(150, Math.round((pShare / (1 / 3)) * 1000) / 10);
      const ytdAch = Math.min(150, Math.round((ytdShare / (1 / 3)) * 1000) / 10);

      periodValues.push(pAch);
      ytdValues.push(ytdAch);

      catStats[cName] = {
        pRev: raw.pRev,
        pQty: raw.pQty,
        pShare: pShare,
        pAch: pAch,
        ytdRev: raw.ytdRev,
        ytdQty: raw.ytdQty,
        ytdShare: ytdShare,
        ytdAch: ytdAch
      };
    });

    const avgPeriod = Math.round(periodValues.reduce((a, b) => a + b, 0) / periodValues.length);
    const avgYTD = Math.round(ytdValues.reduce((a, b) => a + b, 0) / ytdValues.length);

    saCalculated[saName] = {
      periodValues,
      ytdValues,
      avgPeriod,
      avgYTD,
      catStats
    };
  });

  const chartConfigs = [
    {
      saName: 'DIDIN',
      canvasId: 'radar-chart-didin',
      badgeId: 'radar-badge-didin',
      highlightsId: 'radar-highlights-didin',
      instanceKey: 'radarDidinInstance',
      color: '#2563eb',
      bgColor: 'rgba(37, 99, 235, 0.22)',
      labelColor: '#1e40af'
    },
    {
      saName: 'FICKY',
      canvasId: 'radar-chart-ficky',
      badgeId: 'radar-badge-ficky',
      highlightsId: 'radar-highlights-ficky',
      instanceKey: 'radarFickyInstance',
      color: '#10b981',
      bgColor: 'rgba(16, 185, 129, 0.22)',
      labelColor: '#065f46'
    },
    {
      saName: 'ACEP',
      canvasId: 'radar-chart-acep',
      badgeId: 'radar-badge-acep',
      highlightsId: 'radar-highlights-acep',
      instanceKey: 'radarAcepInstance',
      color: '#f59e0b',
      bgColor: 'rgba(245, 158, 11, 0.22)',
      labelColor: '#b45309'
    }
  ];

  const spokeLabels = CANONICAL_COMMODITIES;

  // Render 3 Individual Radar Charts
  chartConfigs.forEach(cfg => {
    const canvas = document.getElementById(cfg.canvasId);
    if (!canvas) return;

    const calc = saCalculated[cfg.saName];
    if (!calc) return;

    const badge = document.getElementById(cfg.badgeId);
    if (badge) {
      badge.textContent = `Ach Periode: ${calc.avgPeriod}% • Ach YTD: ${calc.avgYTD}%`;
    }

    if (cfg.instanceKey === 'radarDidinInstance' && radarDidinInstance) radarDidinInstance.destroy();
    if (cfg.instanceKey === 'radarFickyInstance' && radarFickyInstance) radarFickyInstance.destroy();
    if (cfg.instanceKey === 'radarAcepInstance' && radarAcepInstance) radarAcepInstance.destroy();

    const periodLabel = STATE.month !== 'all' ? `Bulan ${STATE.month}` : `Periode ${yr}`;

    const instance = new Chart(canvas.getContext('2d'), {
      type: 'radar',
      data: {
        labels: spokeLabels,
        datasets: [
          {
            label: `Ach ${periodLabel}`,
            data: calc.periodValues,
            backgroundColor: cfg.bgColor,
            borderColor: cfg.color,
            borderWidth: 2.4,
            pointBackgroundColor: cfg.color,
            pointBorderColor: '#ffffff',
            pointBorderWidth: 1.8,
            pointRadius: 4.5,
            pointHoverRadius: 6,
            fill: true
          },
          {
            label: `Ach Total Tahun (${yr} YTD)`,
            data: calc.ytdValues,
            borderColor: '#64748b',
            borderWidth: 1.8,
            borderDash: [5, 4],
            pointBackgroundColor: '#ffffff',
            pointBorderColor: '#64748b',
            pointBorderWidth: 2,
            pointRadius: 3.5,
            pointHoverRadius: 5.5,
            fill: false
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
          padding: { top: 10, bottom: 10, left: 10, right: 10 }
        },
        plugins: {
          legend: {
            display: true,
            position: 'top',
            labels: {
              boxWidth: 12,
              font: { size: 10, weight: '700' },
              color: '#334155'
            }
          },
          tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.95)',
            padding: 10,
            cornerRadius: 8,
            callbacks: {
              label: (ctx) => {
                const cName = ctx.label;
                const stats = calc.catStats[cName];
                const isPeriod = ctx.datasetIndex === 0;
                const share = isPeriod ? stats?.pShare || 0 : stats?.ytdShare || 0;
                const rev = isPeriod ? stats?.pRev || 0 : stats?.ytdRev || 0;
                return ` ${ctx.dataset.label}: ${ctx.raw}% (Share: ${(share * 100).toFixed(1)}%, ${formatCompactIDR(rev)})`;
              }
            }
          }
        },
        scales: {
          r: {
            min: 0,
            suggestedMax: 150,
            angleLines: { color: 'rgba(226, 232, 240, 0.9)', lineWidth: 1 },
            grid: { color: 'rgba(226, 232, 240, 0.9)', lineWidth: 1 },
            pointLabels: {
              font: { family: "'Plus Jakarta Sans', sans-serif", size: 9.5, weight: '700' },
              color: '#1e293b',
              padding: 5
            },
            ticks: {
              stepSize: 30,
              font: { size: 8.5, weight: '600' },
              color: '#94a3b8',
              backdropColor: 'transparent',
              callback: v => v + '%'
            }
          }
        }
      }
    });

    if (cfg.instanceKey === 'radarDidinInstance') radarDidinInstance = instance;
    if (cfg.instanceKey === 'radarFickyInstance') radarFickyInstance = instance;
    if (cfg.instanceKey === 'radarAcepInstance') radarAcepInstance = instance;

    // Highlights below radar chart
    const highlightsEl = document.getElementById(cfg.highlightsId);
    if (highlightsEl) {
      highlightsEl.innerHTML = `
        <div style="font-size: 11px; font-weight: 700; color: #475569; margin-bottom: 6px;">
          Pencapaian 11 Komoditas Produk (${periodLabel}):
        </div>
        <div style="display: flex; flex-wrap: wrap; gap: 5px;">
          ${CANONICAL_COMMODITIES.map((cName, idx) => {
            const pVal = calc.periodValues[idx];
            const yVal = calc.ytdValues[idx];
            const isGood = pVal >= 100;
            return `
              <span class="sa-badge-chip ${isGood ? 'top' : 'caution'}" style="font-size: 9.5px; padding: 2px 7px;">
                ${cName}: <strong>${pVal}%</strong> (YTD: ${yVal}%)
              </span>
            `;
          }).join('')}
        </div>
      `;
    }
  });

  // Render Overlay Comparison Chart & Table
  renderSARadarOverlay(METRIC_DEFS, saCalculated);
}

// -------------------------------------------------------------------
// 4C. SERVICE ADVISOR RADAR OVERLAY (KOMPARASI 3 SA DALAM 1 GRAFIK)
// -------------------------------------------------------------------
function renderSARadarOverlay(METRIC_DEFS, saCalculated) {
  const overlayCanvas = document.getElementById('radar-chart-overlay');
  const tbody = document.getElementById('radar-comparison-tbody');
  if (!overlayCanvas || !saCalculated || !saCalculated['DIDIN']) return;

  if (radarOverlayInstance) radarOverlayInstance.destroy();

  const labels = METRIC_DEFS.map(m => m.label);

  radarOverlayInstance = new Chart(overlayCanvas.getContext('2d'), {
    type: 'radar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'DIDIN',
          data: saCalculated['DIDIN'].periodValues,
          borderColor: '#2563eb',
          backgroundColor: 'rgba(37, 99, 235, 0.16)',
          borderWidth: 2.2,
          pointBackgroundColor: '#2563eb',
          pointBorderColor: '#ffffff',
          pointRadius: 4
        },
        {
          label: 'FICKY',
          data: saCalculated['FICKY'].periodValues,
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.16)',
          borderWidth: 2.2,
          pointBackgroundColor: '#10b981',
          pointBorderColor: '#ffffff',
          pointRadius: 4
        },
        {
          label: 'ACEP',
          data: saCalculated['ACEP'].periodValues,
          borderColor: '#f59e0b',
          backgroundColor: 'rgba(245, 158, 11, 0.16)',
          borderWidth: 2.2,
          pointBackgroundColor: '#f59e0b',
          pointBorderColor: '#ffffff',
          pointRadius: 4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: true, position: 'top', labels: { boxWidth: 12, font: { size: 10.5, weight: '700' } } },
        tooltip: {
          backgroundColor: 'rgba(15, 23, 42, 0.95)',
          callbacks: {
            label: (ctx) => ` ${ctx.dataset.label}: ${ctx.raw}% Pencapaian`
          }
        }
      },
      scales: {
        r: {
          min: 0,
          suggestedMax: 150,
          angleLines: { color: 'rgba(226, 232, 240, 0.9)' },
          grid: { color: 'rgba(226, 232, 240, 0.9)' },
          pointLabels: {
            font: { family: "'Plus Jakarta Sans', sans-serif", size: 10, weight: '700' },
            color: '#1e293b'
          },
          ticks: {
            stepSize: 30,
            font: { size: 9 },
            color: '#94a3b8',
            backdropColor: 'transparent',
            callback: v => v + '%'
          }
        }
      }
    }
  });

  if (tbody) {
    let rowsHtml = '';
    METRIC_DEFS.forEach((m, idx) => {
      const vDidin = saCalculated['DIDIN'].periodValues[idx] || 0;
      const vFicky = saCalculated['FICKY'].periodValues[idx] || 0;
      const vAcep = saCalculated['ACEP'].periodValues[idx] || 0;

      let leader = 'DIDIN';
      let maxVal = vDidin;
      let badgeClass = 'blue';
      if (vFicky > maxVal) {
        leader = 'FICKY';
        maxVal = vFicky;
        badgeClass = 'green';
      }
      if (vAcep > maxVal) {
        leader = 'ACEP';
        maxVal = vAcep;
        badgeClass = 'amber';
      }

      rowsHtml += `
        <tr>
          <td style="font-weight: 600; color: #1e293b; padding: 7px 10px;">${m.label}</td>
          <td style="text-align: right; padding: 7px 10px; font-weight: ${leader === 'DIDIN' ? '800' : '500'}; color: ${leader === 'DIDIN' ? '#1d4ed8' : '#334155'};">
            ${vDidin}%
          </td>
          <td style="text-align: right; padding: 7px 10px; font-weight: ${leader === 'FICKY' ? '800' : '500'}; color: ${leader === 'FICKY' ? '#047857' : '#334155'};">
            ${vFicky}%
          </td>
          <td style="text-align: right; padding: 7px 10px; font-weight: ${leader === 'ACEP' ? '800' : '500'}; color: ${leader === 'ACEP' ? '#b45309' : '#334155'};">
            ${vAcep}%
          </td>
          <td style="text-align: center; padding: 7px 10px;">
            <span class="tag-badge ${badgeClass}" style="font-size: 10px; padding: 2px 8px;">
              ${leader} (${maxVal}%)
            </span>
          </td>
        </tr>
      `;
    });
    tbody.innerHTML = rowsHtml;
  }
}
"""
    content = content[:radar_start_idx] + new_radar_block + content[radar_end_idx:]
    print("2. Replaced renderSARadarCharts and renderSARadarOverlay successfully with 11 Commodities!")
else:
    print("WARNING: Could not find radar_start or radar_end index!")

with open(js_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated assets/js/dashboard.js successfully.")
