import re

js_file = 'assets/js/dashboard.js'
with open(js_file, 'r', encoding='utf-8') as f:
    content = f.read()

# -------------------------------------------------------------
# 1. UPDATE RADAR CHARTS (POIN 5)
# -------------------------------------------------------------
radar_pattern = re.compile(
    r'// 4B\. SERVICE ADVISOR RADAR CHARTS.*?'
    r'(?=// -------------------------------------------------------------------\s*// 5\. OPERATIONAL BREAKDOWN TABLE)',
    re.DOTALL
)

radar_replacement = """// 4B. SERVICE ADVISOR RADAR CHARTS (KOMPARASI ACH BULAN VS ACH TOTAL TAHUN)
// -------------------------------------------------------------------
function renderSARadarCharts() {
  if (!dashboardData) return;

  const yr = STATE.year;
  const sas = ['DIDIN', 'FICKY', 'ACEP'];

  const METRIC_DEFS = [
    { key: 'cpus', label: 'Unit Entry (CPUS)' },
    { key: 'rev', label: 'Total Revenue' },
    { key: 'tcare', label: 'Penetrasi T-Care' },
    { key: 'cross', label: 'Cross-Selling SO' },
    { key: 'yield', label: 'Yield (Rev / UE)' }
  ];

  // 1. Calculate active filtered period targets & counts
  let periodTargetCpus = 0, periodTargetRev = 0;
  let activeMonthCount = 0;
  MONTHS.forEach(m => {
    if (isMonthInFilter(m)) {
      activeMonthCount++;
      const t = dashboardData.targets[yr]?.[m];
      if (t) {
        periodTargetCpus += t.cpus || 0;
        periodTargetRev += t.revenue_total || 0;
      }
    }
  });
  if (activeMonthCount === 0) activeMonthCount = 1;
  const targetCpusPerSA = (periodTargetCpus > 0 ? periodTargetCpus : activeMonthCount * 650) / 3;
  const targetRevPerSA = (periodTargetRev > 0 ? periodTargetRev : activeMonthCount * 1_250_000_000) / 3;
  const targetCrossPerSA = activeMonthCount * 45_000_000;
  const targetYield = 1_500_000;
  const targetTcareRate = 0.70;

  // 2. Calculate YTD targets & counts for the entire selected year
  let ytdTargetCpus = 0, ytdTargetRev = 0;
  let ytdMonthCount = 0;
  MONTHS.forEach(m => {
    const t = dashboardData.targets[yr]?.[m];
    const actual = dashboardData.monthly_kpis[yr]?.[m];
    if (actual && actual.ue_total > 0) {
      ytdMonthCount++;
      if (t) {
        ytdTargetCpus += t.cpus || 0;
        ytdTargetRev += t.revenue_total || 0;
      }
    }
  });
  if (ytdMonthCount === 0) ytdMonthCount = 9;
  const ytdTargetCpusPerSA = (ytdTargetCpus > 0 ? ytdTargetCpus : ytdMonthCount * 650) / 3;
  const ytdTargetRevPerSA = (ytdTargetRev > 0 ? ytdTargetRev : ytdMonthCount * 1_250_000_000) / 3;
  const ytdTargetCrossPerSA = ytdMonthCount * 45_000_000;

  // 3. Aggregate each SA's performance for Period vs YTD
  const saCalculated = {};

  sas.forEach(saName => {
    let pUE = 0, pCpus = 0, pRev = 0, pTc = 0, pSbe = 0;
    let ytdUE = 0, ytdCpus = 0, ytdRev = 0, ytdTc = 0, ytdSbe = 0;

    dashboardData.sa_performance
      .filter(item => String(item.year) === yr && item.sa === saName)
      .forEach(item => {
        // YTD
        ytdUE += item.ue || 0;
        ytdCpus += item.cpus || 0;
        ytdRev += item.revenue || 0;
        ytdTc += item.tcare_ue || 0;
        ytdSbe += item.sbe_ue || 0;

        // Period
        if (isMonthInFilter(item.month_name)) {
          pUE += item.ue || 0;
          pCpus += item.cpus || 0;
          pRev += item.revenue || 0;
          pTc += item.tcare_ue || 0;
          pSbe += item.sbe_ue || 0;
        }
      });

    // Cross-selling per SA
    let pCrossRev = 0, ytdCrossRev = 0;
    if (dashboardData.sa_cross_selling) {
      dashboardData.sa_cross_selling
        .filter(item => String(item.year) === yr && item.sa === saName)
        .forEach(item => {
          ytdCrossRev += item.revenue || 0;
          if (isMonthInFilter(item.month_name)) {
            pCrossRev += item.revenue || 0;
          }
        });
    }

    const pTcRate = pSbe > 0 ? pTc / pSbe : (pUE > 0 ? pTc / pUE : 0);
    const ytdTcRate = ytdSbe > 0 ? ytdTc / ytdSbe : (ytdUE > 0 ? ytdTc / ytdUE : 0);

    const pYield = pUE > 0 ? pRev / pUE : 0;
    const ytdYield = ytdUE > 0 ? ytdRev / ytdUE : 0;

    const achCpusPeriod = targetCpusPerSA > 0 ? Math.min(150, Math.round((pCpus / targetCpusPerSA) * 1000) / 10) : 0;
    const achRevPeriod = targetRevPerSA > 0 ? Math.min(150, Math.round((pRev / targetRevPerSA) * 1000) / 10) : 0;
    const achTcarePeriod = Math.min(150, Math.round((pTcRate / targetTcareRate) * 1000) / 10);
    const achCrossPeriod = targetCrossPerSA > 0 ? Math.min(150, Math.round((pCrossRev / targetCrossPerSA) * 1000) / 10) : 0;
    const achYieldPeriod = Math.min(150, Math.round((pYield / targetYield) * 1000) / 10);

    const achCpusYTD = ytdTargetCpusPerSA > 0 ? Math.min(150, Math.round((ytdCpus / ytdTargetCpusPerSA) * 1000) / 10) : 0;
    const achRevYTD = ytdTargetRevPerSA > 0 ? Math.min(150, Math.round((ytdRev / ytdTargetRevPerSA) * 1000) / 10) : 0;
    const achTcareYTD = Math.min(150, Math.round((ytdTcRate / targetTcareRate) * 1000) / 10);
    const achCrossYTD = ytdTargetCrossPerSA > 0 ? Math.min(150, Math.round((ytdCrossRev / ytdTargetCrossPerSA) * 1000) / 10) : 0;
    const achYieldYTD = Math.min(150, Math.round((ytdYield / targetYield) * 1000) / 10);

    const periodValues = [achCpusPeriod, achRevPeriod, achTcarePeriod, achCrossPeriod, achYieldPeriod];
    const ytdValues = [achCpusYTD, achRevYTD, achTcareYTD, achCrossYTD, achYieldYTD];

    const avgPeriod = Math.round(periodValues.reduce((a, b) => a + b, 0) / periodValues.length);
    const avgYTD = Math.round(ytdValues.reduce((a, b) => a + b, 0) / ytdValues.length);

    saCalculated[saName] = {
      periodValues,
      ytdValues,
      avgPeriod,
      avgYTD
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

  const spokeLabels = METRIC_DEFS.map(m => m.label);

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
              label: (ctx) => ` ${ctx.dataset.label}: ${ctx.raw}%`
            }
          }
        },
        scales: {
          r: {
            min: 0,
            suggestedMax: 120,
            angleLines: { color: 'rgba(226, 232, 240, 0.9)', lineWidth: 1 },
            grid: { color: 'rgba(226, 232, 240, 0.9)', lineWidth: 1 },
            pointLabels: {
              font: { family: "'Plus Jakarta Sans', sans-serif", size: 10, weight: '700' },
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
          Pencapaian 5 Pilar Utama (${periodLabel}):
        </div>
        <div style="display: flex; flex-wrap: wrap; gap: 6px;">
          ${METRIC_DEFS.map((m, idx) => {
            const pVal = calc.periodValues[idx];
            const yVal = calc.ytdValues[idx];
            const isGood = pVal >= 100;
            return `
              <span class="sa-badge-chip ${isGood ? 'top' : 'caution'}" style="font-size: 10px; padding: 3px 8px;">
                ${m.label}: <strong>${pVal}%</strong> (YTD: ${yVal}%)
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
          suggestedMax: 120,
          angleLines: { color: 'rgba(226, 232, 240, 0.9)' },
          grid: { color: 'rgba(226, 232, 240, 0.9)' },
          pointLabels: {
            font: { family: "'Plus Jakarta Sans', sans-serif", size: 10.5, weight: '700' },
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

content, count_radar = radar_pattern.subn(radar_replacement, content)
print(f"Updated Radar charts section ({count_radar} replacements)")

# -------------------------------------------------------------
# 2. UPDATE CROSS SELLING TABLE (POIN 4)
# -------------------------------------------------------------
cross_pattern = re.compile(
    r'function renderCrossSellingTable\(\)\s*\{.*?'
    r'(?=\nfunction renderDataExplorerTable)',
    re.DOTALL
)

cross_replacement = """function renderCrossSellingTable() {
  const tbody = document.getElementById('cross-tbody');
  if (!tbody || !dashboardData) return;

  const yr = STATE.year;
  const ly = String(parseInt(yr) - 1);
  const saFilter = item => STATE.sa === 'all' || !item.sa || item.sa === STATE.sa;
  const EXCLUDED_CATEGORIES = ['SYNT', 'WIPER FLUID'];

  const curCatMap = {};
  const lyCatMap = {};

  if (dashboardData.cross_selling) {
    dashboardData.cross_selling
      .filter(item => String(item.year) === yr && isMonthInFilter(item.month_name) && saFilter(item))
      .forEach(item => {
        const c = (item.category || 'LAINNYA').toUpperCase().trim();
        if (EXCLUDED_CATEGORIES.includes(c)) return;
        if (!curCatMap[c]) curCatMap[c] = { qty: 0, rev: 0 };
        curCatMap[c].qty += item.qty || 0;
        curCatMap[c].rev += item.revenue || 0;
      });

    dashboardData.cross_selling
      .filter(item => String(item.year) === ly && isMonthInFilter(item.month_name) && saFilter(item))
      .forEach(item => {
        const c = (item.category || 'LAINNYA').toUpperCase().trim();
        if (EXCLUDED_CATEGORIES.includes(c)) return;
        if (!lyCatMap[c]) lyCatMap[c] = { qty: 0, rev: 0 };
        lyCatMap[c].qty += item.qty || 0;
        lyCatMap[c].rev += item.revenue || 0;
      });
  }

  // Calculate Customer Segment Proportion (Retail, Fleet, Sudeco, TPI) in active period
  let retCount = 0, fltCount = 0, sudCount = 0, tpiCount = 0;
  if (dashboardData.breakdown) {
    dashboardData.breakdown
      .filter(item => String(item.year) === yr && isMonthInFilter(item.month_name) && saFilter(item))
      .forEach(item => {
        const seg = (item.fleet_retail || '').toUpperCase();
        if (seg.includes('SUDECO')) sudCount += item.units || 1;
        else if (seg.includes('TPI')) tpiCount += item.units || 1;
        else if (seg.includes('FLEET')) fltCount += item.units || 1;
        else retCount += item.units || 1;
      });
  }
  const totSeg = retCount + fltCount + sudCount + tpiCount || 1;
  const pRet = retCount / totSeg;
  const pFlt = fltCount / totSeg;
  const pSud = sudCount / totSeg;
  const pTpi = tpiCount / totSeg;

  const allCategories = Array.from(new Set([...Object.keys(curCatMap), ...Object.keys(lyCatMap)]));
  allCategories.sort();

  let html = '';
  allCategories.forEach(cat => {
    const cur = curCatMap[cat] || { qty: 0, rev: 0 };
    const lyData = lyCatMap[cat] || { qty: 0, rev: 0 };

    const growthRev = lyData.rev > 0 ? (cur.rev - lyData.rev) / lyData.rev : 0;
    const diffQty = cur.qty - lyData.qty;

    const qRet = Math.round(cur.qty * pRet);
    const qFlt = Math.round(cur.qty * pFlt);
    const qSud = Math.round(cur.qty * pSud);
    const qTpi = Math.max(0, cur.qty - qRet - qFlt - qSud);

    const compCell = cur.qty > 0 ? `
      <div class="seg-comp-pill-wrap" style="display: flex; flex-direction: column; gap: 3px;" title="Retail: ${qRet} (${formatPct(pRet)}) | Fleet: ${qFlt} (${formatPct(pFlt)}) | Sudeco: ${qSud} (${formatPct(pSud)}) | TPI: ${qTpi} (${formatPct(pTpi)})">
        <div style="display: flex; height: 6px; border-radius: 3px; overflow: hidden; background: #e2e8f0;">
          <div style="width: ${pRet*100}%; background: #10b981;" title="Retail: ${qRet}"></div>
          <div style="width: ${pFlt*100}%; background: #2563eb;" title="Fleet: ${qFlt}"></div>
          <div style="width: ${pSud*100}%; background: #8b5cf6;" title="Sudeco: ${qSud}"></div>
          <div style="width: ${pTpi*100}%; background: #f59e0b;" title="TPI: ${qTpi}"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 9.5px; font-weight: 700;">
          <span style="color: #047857;" title="Retail: ${qRet}">Ret ${formatPct(pRet, 0)}</span>
          <span style="color: #1d4ed8;" title="Fleet: ${qFlt}">Flt ${formatPct(pFlt, 0)}</span>
          <span style="color: #6d28d9;" title="Sudeco: ${qSud}">Sud ${formatPct(pSud, 0)}</span>
          <span style="color: #b45309;" title="TPI: ${qTpi}">TPI ${formatPct(pTpi, 0)}</span>
        </div>
      </div>
    ` : `<span style="color: #94a3b8; font-size: 11px;">—</span>`;

    html += `
      <tr>
        <td class="sticky-col" style="font-weight: 600;">${cat}</td>
        <td class="numeric">${formatNum(cur.qty)}</td>
        <td class="numeric">${formatIDR(cur.rev)}</td>
        <td style="min-width: 200px; padding: 6px 12px;">${compCell}</td>
        <td class="numeric" style="color: var(--text-secondary);">${formatNum(lyData.qty)}</td>
        <td class="numeric" style="color: var(--text-secondary);">${formatIDR(lyData.rev)}</td>
        <td class="numeric" style="font-weight: 700; color: ${diffQty >= 0 ? 'var(--status-up)' : 'var(--status-down)'};">
          ${diffQty >= 0 ? '+' : ''}${formatNum(diffQty)}
        </td>
        <td class="numeric" style="font-weight: 700; color: ${growthRev >= 0 ? 'var(--status-up)' : 'var(--status-down)'};">
          ${lyData.rev > 0 ? formatPct(growthRev) : '—'}
        </td>
      </tr>
    `;
  });

  tbody.innerHTML = html;
}
"""

content, count_cross = cross_pattern.subn(cross_replacement, content)
print(f"Updated Cross Selling section ({count_cross} replacements)")

# -------------------------------------------------------------
# 3. UPDATE TIKTOK PARSER (POIN 9)
# -------------------------------------------------------------
tiktok_old = """      if (detectedMonth && i + 5 < rows.length) {
        const parseNums = (r) => (r || []).slice(1).map(x => parseFloat(x.trim())).filter(x => !isNaN(x));
        const dur = parseNums(rows[i+1]);
        const likes = parseNums(rows[i+2]);
        const view = parseNums(rows[i+3]);
        const com = parseNums(rows[i+4]);
        const book = parseNums(rows[i+5]);

        const avg = (arr) => arr.length > 0 ? Math.round(arr.reduce((a,b)=>a+b,0)/arr.length) : null;
        const sum = (arr) => arr.length > 0 ? Math.round(arr.reduce((a,b)=>a+b,0)) : 0;

        monthlyDict[detectedMonth] = {
          month: detectedMonth,
          duration: avg(dur),
          likes: avg(likes),
          viewer: avg(view),
          comments: avg(com),
          booking: sum(book),
          has_data: dur.length > 0
        };
        i += 6;
        continue;
      }"""

tiktok_new = """      if (detectedMonth && i + 5 < rows.length) {
        const extractDaily = (r) => {
          const vals = [];
          if (!r) return vals;
          for (let colIdx = 1; colIdx < r.length; colIdx++) {
            const raw = (r[colIdx] || '').trim().replace(',', '.');
            if (/duration|likes|viewer|comment|booking|\\/day|\\/month/i.test(raw)) break;
            const n = parseFloat(raw);
            if (!isNaN(n)) vals.push(n);
          }
          return vals;
        };

        const durs = extractDaily(rows[i+1]);
        const likes = extractDaily(rows[i+2]);
        const views = extractDaily(rows[i+3]);
        const comms = extractDaily(rows[i+4]);
        const books = extractDaily(rows[i+5]);

        const avg = (arr) => arr.length > 0 ? Math.round(arr.reduce((a,b)=>a+b,0)/arr.length) : null;
        let totBook = books.length > 0 ? Math.round(books.reduce((a,b)=>a+b,0)) : 0;

        // Check if explicit summary exists
        const bookRow = rows[i+5];
        if (bookRow) {
          for (let cIdx = 0; cIdx < bookRow.length; cIdx++) {
            if (/booking \\/month/i.test(bookRow[cIdx]) && cIdx + 1 < bookRow.length) {
              const explicit = parseFloat((bookRow[cIdx+1] || '').trim().replace(',', '.'));
              if (!isNaN(explicit)) totBook = Math.round(explicit);
            }
          }
        }

        monthlyDict[detectedMonth] = {
          month: detectedMonth,
          duration: avg(durs),
          likes: avg(likes),
          viewer: avg(views),
          comments: avg(comms),
          booking: totBook,
          has_data: durs.length > 0
        };
        i += 6;
        continue;
      }"""

if tiktok_old in content:
    content = content.replace(tiktok_old, tiktok_new)
    print("Updated processLiveTikTokCSV in dashboard.js")
else:
    print("Warning: tiktok_old snippet not found exactly in dashboard.js")

# -------------------------------------------------------------
# 4. UPDATE BOOKING CHANNEL TARGETS (POIN 8)
# -------------------------------------------------------------
booking_configs_old = """  const channelConfigs = [
    { key: 'inc_call', canvasId: 'chart-b-inc', badgeId: 'b-inc-total', color: '#2563eb' },
    { key: 'boc', canvasId: 'chart-b-boc', badgeId: 'b-boc-total', color: '#7c3aed' },
    { key: 'sales', canvasId: 'chart-b-sales', badgeId: 'b-sales-total', color: '#4b5563' },
    { key: 'm_toyota', canvasId: 'chart-b-mtoyota', badgeId: 'b-mtoyota-total', color: '#dc2626' },
    { key: 'sa_total', canvasId: 'chart-b-sa-total', badgeId: 'b-sa-total-total', color: '#0f172a' },
    { key: 'sa_didin', canvasId: 'chart-b-didin', badgeId: 'b-didin-total', color: '#0284c7' },
    { key: 'sa_ficky', canvasId: 'chart-b-ficky', badgeId: 'b-ficky-total', color: '#059669' },
    { key: 'sa_acep', canvasId: 'chart-b-acep', badgeId: 'b-acep-total', color: '#d97706' }
  ];"""

booking_configs_new = """  const channelConfigs = [
    { key: 'inc_call', canvasId: 'chart-b-inc', badgeId: 'b-inc-total', color: '#2563eb', target: 35 },
    { key: 'boc', canvasId: 'chart-b-boc', badgeId: 'b-boc-total', color: '#7c3aed', target: 25 },
    { key: 'sales', canvasId: 'chart-b-sales', badgeId: 'b-sales-total', color: '#4b5563', target: 15 },
    { key: 'm_toyota', canvasId: 'chart-b-mtoyota', badgeId: 'b-mtoyota-total', color: '#dc2626', target: 20 },
    { key: 'sa_total', canvasId: 'chart-b-sa-total', badgeId: 'b-sa-total-total', color: '#0f172a', target: 45 },
    { key: 'sa_didin', canvasId: 'chart-b-didin', badgeId: 'b-didin-total', color: '#0284c7', target: 15 },
    { key: 'sa_ficky', canvasId: 'chart-b-ficky', badgeId: 'b-ficky-total', color: '#059669', target: 15 },
    { key: 'sa_acep', canvasId: 'chart-b-acep', badgeId: 'b-acep-total', color: '#d97706', target: 15 }
  ];"""

if booking_configs_old in content:
    content = content.replace(booking_configs_old, booking_configs_new)
    print("Updated booking channel configs with targets")

# Update booking datasets to include target line
dataset_old = """      data: {
        labels: months,
        datasets: [{
          label: ch.title,
          data: ch.monthly || [],
          borderColor: cfg.color,
          backgroundColor: bgCol,
          borderWidth: bWidth,
          borderRadius: bRadius,
          pointRadius: cType === 'bar' ? 0 : 3.5,
          pointHoverRadius: 5.5,
          pointBackgroundColor: cfg.color,
          fill: isFill,
          tension: 0.3,
          spanGaps: false
        }]
      },"""

dataset_new = """      data: {
        labels: months,
        datasets: [
          {
            label: ch.title,
            data: ch.monthly || [],
            borderColor: cfg.color,
            backgroundColor: bgCol,
            borderWidth: bWidth,
            borderRadius: bRadius,
            pointRadius: cType === 'bar' ? 0 : 3.5,
            pointHoverRadius: 5.5,
            pointBackgroundColor: cfg.color,
            fill: isFill,
            tension: 0.3,
            spanGaps: false,
            order: 2
          },
          {
            type: 'line',
            label: `Garis Target (${cfg.target}/bln)`,
            data: months.map(() => cfg.target),
            borderColor: '#ef4444',
            borderWidth: 1.5,
            borderDash: [5, 4],
            pointRadius: 0,
            pointHoverRadius: 0,
            fill: false,
            tension: 0,
            isTarget: true,
            order: 1
          }
        ]
      },"""

if dataset_old in content:
    content = content.replace(dataset_old, dataset_new)
    print("Updated booking datasets to include target lines")

# Update datalabels plugin to ignore target lines
datalabel_old = """    afterDatasetsDraw(chart) {
      const { ctx } = chart;
      chart.data.datasets.forEach((dataset, i) => {
        const meta = chart.getDatasetMeta(i);
        if (meta.hidden) return;"""

datalabel_new = """    afterDatasetsDraw(chart) {
      const { ctx } = chart;
      chart.data.datasets.forEach((dataset, i) => {
        if (dataset.isTarget) return;
        const meta = chart.getDatasetMeta(i);
        if (meta.hidden) return;"""

if datalabel_old in content:
    content = content.replace(datalabel_old, datalabel_new)
    print("Updated datalabels plugin to ignore target lines")

# -------------------------------------------------------------
# 5. ADD FUNNELLING RING AREA & FLEET/RETAIL CHARTS (POIN 6 & 7)
# -------------------------------------------------------------
funnel_hook_old = """  // 1. Monthly Funnel Bar Chart (Abu di awal, Biru di tengah, Ijo di akhir + persentase)
  renderFunnelMonthlyChart(summary);"""

funnel_hook_new = """  // 1. Monthly Funnel Bar Chart (Abu di awal, Biru di tengah, Ijo di akhir + persentase)
  renderFunnelMonthlyChart(summary);

  // 1B. Connected Call vs Cust FU by Ring Area & Fleet/Retail (Revisi Poin 6 & 7)
  renderFunnelRingAndFleetCharts();"""

if funnel_hook_old in content:
    content = content.replace(funnel_hook_old, funnel_hook_new)
    print("Added renderFunnelRingAndFleetCharts call to renderFunnelling")

# Insert renderFunnelRingAndFleetCharts function definition right after renderFunnelMonthlyChart
fn_rf_definition = """
let funnelRingAreaInstance = null;
let funnelFleetRetailInstance = null;

function renderFunnelRingAndFleetCharts() {
  if (!funnellingData) return;

  const ringTrend = funnellingData.monthly_ring_area_trend || {};
  const fleetTrend = funnellingData.monthly_fleet_retail_trend || {};
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agt', 'Sep'];

  // 1. Chart Ring Area (Connected Call vs Cust FU per Ring Area)
  const ringCanvas = document.getElementById('chart-funnel-ring-area');
  if (ringCanvas) {
    if (funnelRingAreaInstance) funnelRingAreaInstance.destroy();

    const ring1Con = months.map(m => ringTrend[m]?.['Ring 1']?.connected || 0);
    const ring1Fu = months.map(m => ringTrend[m]?.['Ring 1']?.cust_fu || 0);

    const ring2Con = months.map(m => ringTrend[m]?.['Ring 2']?.connected || 0);
    const ring2Fu = months.map(m => ringTrend[m]?.['Ring 2']?.cust_fu || 0);

    const ring3Con = months.map(m => ringTrend[m]?.['Ring 3']?.connected || 0);
    const ring3Fu = months.map(m => ringTrend[m]?.['Ring 3']?.cust_fu || 0);

    const outCon = months.map(m => ringTrend[m]?.['Out of Area']?.connected || 0);
    const outFu = months.map(m => ringTrend[m]?.['Out of Area']?.cust_fu || 0);

    funnelRingAreaInstance = new Chart(ringCanvas.getContext('2d'), {
      type: 'bar',
      data: {
        labels: months,
        datasets: [
          {
            label: 'Ring 1 (Connected)',
            data: ring1Con,
            backgroundColor: '#2563eb',
            borderRadius: 3,
            stack: 'connected'
          },
          {
            label: 'Ring 2 (Connected)',
            data: ring2Con,
            backgroundColor: '#10b981',
            borderRadius: 3,
            stack: 'connected'
          },
          {
            label: 'Ring 3 (Connected)',
            data: ring3Con,
            backgroundColor: '#f59e0b',
            borderRadius: 3,
            stack: 'connected'
          },
          {
            label: 'Out Area (Connected)',
            data: outCon,
            backgroundColor: '#8b5cf6',
            borderRadius: 3,
            stack: 'connected'
          },
          {
            type: 'line',
            label: 'Total Cust FU',
            data: months.map((m, i) => ring1Fu[i] + ring2Fu[i] + ring3Fu[i] + outFu[i]),
            borderColor: '#64748b',
            backgroundColor: '#64748b',
            borderWidth: 2,
            borderDash: [4, 4],
            pointRadius: 3,
            tension: 0.2,
            fill: false
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: {
            position: 'top',
            labels: { boxWidth: 10, font: { size: 10, weight: '600' } }
          },
          tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.95)',
            callbacks: {
              footer: (items) => {
                const idx = items[0].dataIndex;
                const totFu = ring1Fu[idx] + ring2Fu[idx] + ring3Fu[idx] + outFu[idx];
                const totCon = ring1Con[idx] + ring2Con[idx] + ring3Con[idx] + outCon[idx];
                const r = totFu > 0 ? ((totCon / totFu) * 100).toFixed(1) : '0';
                return `Total Connected: ${totCon} / ${totFu} (${r}%)`;
              }
            }
          }
        },
        scales: {
          x: { grid: { display: false }, ticks: { font: { size: 10, weight: '700' } } },
          y: { beginAtZero: true, grid: { color: 'rgba(226, 232, 240, 0.5)' } }
        }
      }
    });

    const badge = document.getElementById('ring-area-kpi-badge');
    if (badge) {
      const totAllFu = ring1Fu.reduce((a,b)=>a+b,0) + ring2Fu.reduce((a,b)=>a+b,0) + ring3Fu.reduce((a,b)=>a+b,0) + outFu.reduce((a,b)=>a+b,0);
      const totAllCon = ring1Con.reduce((a,b)=>a+b,0) + ring2Con.reduce((a,b)=>a+b,0) + ring3Con.reduce((a,b)=>a+b,0) + outCon.reduce((a,b)=>a+b,0);
      badge.textContent = `Rasio Rata-rata: ${((totAllCon / totAllFu)*100).toFixed(1)}% Connected`;
    }
  }

  // 2. Chart Fleet / Retail (Connected Call vs Cust FU per Segmen)
  const fleetCanvas = document.getElementById('chart-funnel-fleet-retail');
  if (fleetCanvas) {
    if (funnelFleetRetailInstance) funnelFleetRetailInstance.destroy();

    const retCon = months.map(m => fleetTrend[m]?.['Retail']?.connected || 0);
    const retFu = months.map(m => fleetTrend[m]?.['Retail']?.cust_fu || 0);

    const fltCon = months.map(m => fleetTrend[m]?.['Fleet']?.connected || 0);
    const fltFu = months.map(m => fleetTrend[m]?.['Fleet']?.cust_fu || 0);

    const retPct = months.map((m, i) => retFu[i] > 0 ? Math.round((retCon[i] / retFu[i]) * 100) : 0);
    const fltPct = months.map((m, i) => fltFu[i] > 0 ? Math.round((fltCon[i] / fltFu[i]) * 100) : 0);

    funnelFleetRetailInstance = new Chart(fleetCanvas.getContext('2d'), {
      type: 'bar',
      data: {
        labels: months,
        datasets: [
          {
            type: 'bar',
            label: 'Retail Connected',
            data: retCon,
            backgroundColor: '#059669',
            borderRadius: 3,
            yAxisID: 'y'
          },
          {
            type: 'bar',
            label: 'Retail Cust FU',
            data: retFu,
            backgroundColor: '#a7f3d0',
            borderRadius: 3,
            yAxisID: 'y'
          },
          {
            type: 'bar',
            label: 'Fleet Connected',
            data: fltCon,
            backgroundColor: '#db2777',
            borderRadius: 3,
            yAxisID: 'y'
          },
          {
            type: 'bar',
            label: 'Fleet Cust FU',
            data: fltFu,
            backgroundColor: '#fbcfe8',
            borderRadius: 3,
            yAxisID: 'y'
          },
          {
            type: 'line',
            label: '% Connected Retail',
            data: retPct,
            borderColor: '#047857',
            borderWidth: 2,
            pointRadius: 3,
            yAxisID: 'yPct',
            tension: 0.2
          },
          {
            type: 'line',
            label: '% Connected Fleet',
            data: fltPct,
            borderColor: '#be185d',
            borderWidth: 2,
            pointRadius: 3,
            borderDash: [3, 3],
            yAxisID: 'yPct',
            tension: 0.2
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: {
            position: 'top',
            labels: { boxWidth: 10, font: { size: 10, weight: '600' } }
          },
          tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.95)'
          }
        },
        scales: {
          x: { grid: { display: false }, ticks: { font: { size: 10, weight: '700' } } },
          y: { beginAtZero: true, grid: { color: 'rgba(226, 232, 240, 0.5)' }, title: { display: true, text: 'Volume Call', font: { size: 10 } } },
          yPct: {
            position: 'right',
            beginAtZero: true,
            max: 100,
            grid: { display: false },
            ticks: { callback: v => v + '%', font: { size: 9 } }
          }
        }
      }
    });

    const badgeFlt = document.getElementById('fleet-retail-kpi-badge');
    if (badgeFlt) {
      const totRetFu = retFu.reduce((a,b)=>a+b,0);
      const totRetCon = retCon.reduce((a,b)=>a+b,0);
      const totFltFu = fltFu.reduce((a,b)=>a+b,0);
      const totFltCon = fltCon.reduce((a,b)=>a+b,0);
      badgeFlt.textContent = `Retail: ${((totRetCon/totRetFu)*100).toFixed(1)}% | Fleet: ${((totFltCon/totFltFu)*100).toFixed(1)}%`;
    }
  }
}
"""

funnel_pos = content.find('function renderFunnelMonthlyChart(')
if funnel_pos != -1:
    content = content[:funnel_pos] + fn_rf_definition + "\n" + content[funnel_pos:]
    print("Added renderFunnelRingAndFleetCharts function definition")

# -------------------------------------------------------------
# WRITE UPDATED dashboard.js
# -------------------------------------------------------------
with open(js_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully written all revisions into assets/js/dashboard.js!")
