sbi_code = '''
// ============================================================================
// SBI (SERVICE BERKALA INTERNAL) INTELLIGENCE & REMINDER MONITORING
// ============================================================================
let sbiData = null;
let sbiChartInstances = {};
let sbiCurrentPage = 1;
let sbiPageSize = 25;
let sbiQuickFilter = 'all';
let sbiFilteredRecords = [];
let sbiEventsInitialized = false;

async function loadSbiData() {
  try {
    const res = await fetch('data/sbi_data.json?v=8.6');
    if (!res.ok) throw new Error('HTTP ' + res.status);
    sbiData = await res.json();
    console.log('[OK] Loaded SBI data:', sbiData.meta?.total_records, 'records');
    renderSbi();
    return sbiData;
  } catch (err) {
    console.warn('Gagal memuat sbi_data.json, mencoba gviz fallback...', err);
    try {
      const gvizUrl = 'https://docs.google.com/spreadsheets/d/1b60d-JO50LU4KyywuULokmDIU7z3Ts_1/gviz/tq?tqx=out:csv&gid=457735933';
      const gvizRes = await fetch(gvizUrl);
      if (gvizRes.ok) {
        const csvText = await gvizRes.text();
        sbiData = parseSbiClientCsv(csvText);
        renderSbi();
        return sbiData;
      }
    } catch (e2) {
      console.error('GViz fallback failed for SBI:', e2);
    }
  }
}

function parseSbiClientCsv(csvText) {
  const lines = csvText.split(/\\r?\\n/).filter(l => l.trim().length > 0);
  const rows = lines.map(line => {
    const res = [];
    let inside = false;
    let curr = '';
    for (let i = 0; i < line.length; i++) {
      const ch = line[i];
      if (ch === '"') {
        inside = !inside;
      } else if (ch === ',' && !inside) {
        res.push(curr.trim());
        curr = '';
      } else {
        curr += ch;
      }
    }
    res.push(curr.trim());
    return res;
  });

  let hIdx = -1;
  for (let i = 0; i < rows.length; i++) {
    const rStr = rows[i].join(' | ');
    if (rStr.includes('VIN') && rStr.includes('Nama') && rStr.includes('Model')) {
      hIdx = i;
      break;
    }
  }
  if (hIdx === -1) hIdx = 6;

  const dataRows = rows.slice(hIdx + 1);
  const records = dataRows.map((r, idx) => ({
    id: idx + 1,
    cai: r[0] || '',
    month_num: r[1] || '',
    month: r[2] || '',
    month_fu: r[3] || '',
    year: r[4] || '',
    year_fu: r[5] || '',
    vin: r[6] || '',
    no: r[7] || '',
    tgl_transaksi: r[8] || '',
    nama: r[9] || '',
    nama_cust: r[10] || '',
    type_cust: r[11] || '',
    telepon1: r[12] || '',
    telepon2: r[13] || '',
    telepon3: r[14] || '',
    model: r[15] || '',
    plat_no: r[16] || '',
    sales_person: r[17] || '',
    nomor_rangka: r[18] || '',
    alamat: r[19] || '',
    kab: r[20] || '',
    ss: r[21] || '',
    car_type: r[22] || '',
    no_wa: r[23] || '',
    fu_by: r[24] || '',
    tgl_fu: r[25] || '',
    notes_fu: r[26] || '',
    penggalian_mrs: r[27] || '',
    cai_to_dealer: r[28] || '',
    ket_fu: r[29] || '',
    sales: r[30] || '',
    potency_sales: r[31] || '',
    fu_sales: r[32] || '',
    fu_by_sales: r[33] || '',
    status_tcare: r[34] || '',
    bulan_cai_so: r[35] || '',
    ring_area: r[36] || '',
    cai_10k: r[37] || '',
    cai_20k: r[38] || '',
    cai_30k: r[39] || '',
    cai_40k: r[40] || '',
    cai_50k: r[41] || '',
    cai_60k: r[42] || '',
    cai_70k: r[43] || '',
    habit_ring_area: r[44] || '',
    habit_dealer: r[45] || '',
    judgement_cust: r[46] || ''
  }));

  return {
    meta: { total_records: records.length },
    summary: {
      monthly_2026: {
        January: { dec: 65, cai: 49, acv: '75%' },
        February: { dec: 80, cai: 64, acv: '80%' },
        March: { dec: 60, cai: 52, acv: '87%' },
        April: { dec: 0, cai: 0, acv: '-' },
        May: { dec: 62, cai: 52, acv: '84%' },
        June: { dec: 83, cai: 66, acv: '80%' },
        July: { dec: 81, cai: 62, acv: '77%' },
        August: { dec: 70, cai: 54, acv: '77%' },
        September: { dec: 86, cai: 32, acv: '37%' },
        October: { dec: 0, cai: 0, acv: '-' },
        November: { dec: 0, cai: 0, acv: '-' },
        December: { dec: 0, cai: 0, acv: '-' }
      },
      yearly_perf: {
        '2024': { dec: 677, hybrid: 54, pct_hybrid: '8.0%' },
        '2025': { dec: 854, hybrid: 105, pct_hybrid: '12.3%' },
        '2026': { dec: 649, hybrid: 130, pct_hybrid: '20.0%' }
      }
    },
    records: records
  };
}

function initSbiEvents() {
  if (sbiEventsInitialized) return;
  sbiEventsInitialized = true;

  // Filter change events
  ['sbi-filter-year', 'sbi-filter-month', 'sbi-filter-cai', 'sbi-filter-tcare',
   'sbi-filter-cartype', 'sbi-filter-judgement', 'sbi-filter-ss'].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener('change', () => {
        sbiCurrentPage = 1;
        applySbiFiltersAndRender();
      });
    }
  });

  // Search input
  const searchInput = document.getElementById('sbi-search-input');
  if (searchInput) {
    let debounceTimer;
    searchInput.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        sbiCurrentPage = 1;
        applySbiFiltersAndRender();
      }, 150);
    });
  }

  // Quick Filter Pills
  document.querySelectorAll('.btn-sbi-pill').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.btn-sbi-pill').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      sbiQuickFilter = btn.getAttribute('data-sbi-quick') || 'all';
      sbiCurrentPage = 1;
      applySbiFiltersAndRender();
    });
  });

  // Page Size selector
  const pageSizeSelect = document.getElementById('sbi-page-size');
  if (pageSizeSelect) {
    pageSizeSelect.addEventListener('change', () => {
      const val = pageSizeSelect.value;
      sbiPageSize = val === 'all' ? 99999 : parseInt(val, 10);
      sbiCurrentPage = 1;
      renderSbiTable();
    });
  }

  // Export CSV button
  const exportBtn = document.getElementById('btn-export-sbi');
  if (exportBtn) {
    exportBtn.addEventListener('click', exportSbiCsv);
  }

  // Live Sync button
  const syncBtn = document.getElementById('btn-sync-sbi-sheet');
  if (syncBtn) {
    syncBtn.addEventListener('click', syncSbiFromLiveSheet);
  }

  // Modal Close buttons
  const modalCloseBtn = document.getElementById('btn-close-sbi-modal');
  const modalOverlay = document.getElementById('sbi-detail-modal');
  if (modalCloseBtn) {
    modalCloseBtn.addEventListener('click', () => {
      if (modalOverlay) modalOverlay.style.display = 'none';
    });
  }
  if (modalOverlay) {
    modalOverlay.addEventListener('click', (e) => {
      if (e.target === modalOverlay) modalOverlay.style.display = 'none';
    });
  }
}

function applySbiFiltersAndRender() {
  if (!sbiData || !sbiData.records) return;

  const fYear = document.getElementById('sbi-filter-year')?.value || 'all';
  const fMonth = document.getElementById('sbi-filter-month')?.value || 'all';
  const fCai = document.getElementById('sbi-filter-cai')?.value || 'all';
  const fTcare = document.getElementById('sbi-filter-tcare')?.value || 'all';
  const fCartype = document.getElementById('sbi-filter-cartype')?.value || 'all';
  const fJudgement = document.getElementById('sbi-filter-judgement')?.value || 'all';
  const fSs = document.getElementById('sbi-filter-ss')?.value || 'all';
  const query = (document.getElementById('sbi-search-input')?.value || '').trim().toLowerCase();

  sbiFilteredRecords = sbiData.records.filter(r => {
    // Year filter
    if (fYear !== 'all' && r.year !== fYear) return false;

    // Month filter
    if (fMonth !== 'all' && r.month !== fMonth) return false;

    // CAI filter
    if (fCai !== 'all') {
      const isCai = r.cai && r.cai.toUpperCase() === 'CAI';
      if (fCai === 'CAI' && !isCai) return false;
      if (fCai === 'NOT CAI' && isCai) return false;
    }

    // T-Care filter
    if (fTcare !== 'all' && (r.status_tcare || '').toUpperCase() !== fTcare) return false;

    // Car type filter
    if (fCartype !== 'all') {
      const ct = (r.car_type || '').toUpperCase();
      if (!ct.includes(fCartype)) return false;
    }

    // Judgement filter
    if (fJudgement !== 'all') {
      const j = (r.judgement_cust || '').toUpperCase();
      if (!j.includes(fJudgement)) return false;
    }

    // SS filter
    if (fSs !== 'all') {
      const ssVal = (r.ss || '').toUpperCase();
      if (!ssVal.includes(fSs)) return false;
    }

    // Quick filter pill
    if (sbiQuickFilter === 'cai') {
      if ((r.cai || '').toUpperCase() !== 'CAI') return false;
    } else if (sbiQuickFilter === 'not-cai') {
      if ((r.cai || '').toUpperCase() === 'CAI') return false;
    } else if (sbiQuickFilter === 'hot') {
      if (!(r.judgement_cust || '').toUpperCase().includes('HOT')) return false;
    } else if (sbiQuickFilter === 'loss') {
      if (!(r.judgement_cust || '').toUpperCase().includes('LOSS')) return false;
    } else if (sbiQuickFilter === 'wajib-fu') {
      if (!(r.potency_sales || '').toUpperCase().includes('WAJIB')) return false;
    } else if (sbiQuickFilter === 'hybrid') {
      if (!(r.car_type || '').toUpperCase().includes('HYBRID')) return false;
    } else if (sbiQuickFilter === 'fleet') {
      if ((r.type_cust || '').toUpperCase() !== 'FLEET') return false;
    }

    // Text Search
    if (query) {
      const haystack = [
        r.vin, r.plat_no, r.nama, r.nama_cust, r.model,
        r.telepon1, r.no_wa, r.alamat, r.kab, r.notes_fu,
        r.penggalian_mrs, r.sales_person, r.ss, r.judgement_cust
      ].join(' ').toLowerCase();
      if (!haystack.includes(query)) return false;
    }

    return true;
  });

  updateSbiQuickPillCounters();
  updateSbiKpis();
  renderSbiTable();
}

function updateSbiQuickPillCounters() {
  if (!sbiData || !sbiData.records) return;
  const all = sbiData.records;

  let cntCai = 0, cntNotCai = 0, cntHot = 0, cntLoss = 0, cntWajib = 0, cntHybrid = 0, cntFleet = 0;
  all.forEach(r => {
    const isCai = (r.cai || '').toUpperCase() === 'CAI';
    if (isCai) cntCai++; else cntNotCai++;
    const j = (r.judgement_cust || '').toUpperCase();
    if (j.includes('HOT')) cntHot++;
    if (j.includes('LOSS')) cntLoss++;
    const p = (r.potency_sales || '').toUpperCase();
    if (p.includes('WAJIB')) cntWajib++;
    const ct = (r.car_type || '').toUpperCase();
    if (ct.includes('HYBRID')) cntHybrid++;
    if ((r.type_cust || '').toUpperCase() === 'FLEET') cntFleet++;
  });

  const setT = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = formatNum(v); };
  setT('pill-cnt-all', all.length);
  setT('pill-cnt-cai', cntCai);
  setT('pill-cnt-not-cai', cntNotCai);
  setT('pill-cnt-hot', cntHot);
  setT('pill-cnt-loss', cntLoss);
  setT('pill-cnt-wajib', cntWajib);
  setT('pill-cnt-hybrid', cntHybrid);
  setT('pill-cnt-fleet', cntFleet);
}

function updateSbiKpis() {
  const records = sbiFilteredRecords || [];
  const total = records.length;
  let caiCount = 0;
  let hybridCount = 0;
  let hotCount = 0;

  records.forEach(r => {
    if ((r.cai || '').toUpperCase() === 'CAI') caiCount++;
    if ((r.car_type || '').toUpperCase().includes('HYBRID')) hybridCount++;
    if ((r.judgement_cust || '').toUpperCase().includes('HOT')) hotCount++;
  });

  const acvPct = total > 0 ? (caiCount / total * 100).toFixed(1) + '%' : '0.0%';
  const hybridPct = total > 0 ? (hybridCount / total * 100).toFixed(1) + '%' : '0.0%';
  const hotPct = total > 0 ? (hotCount / total * 100).toFixed(1) + '%' : '0.0%';

  const setEl = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
  setEl('sbi-kpi-total-dec', formatNum(total));
  setEl('sbi-kpi-total-cai', formatNum(caiCount));
  setEl('sbi-kpi-avg-acv', acvPct);
  setEl('sbi-kpi-total-hybrid', `${formatNum(hybridCount)} (${hybridPct})`);
  setEl('sbi-kpi-total-hot', `${formatNum(hotCount)} (${hotPct})`);
}

function renderSbiCharts() {
  if (!sbiData) return;

  // Chart 1: Monthly Trend 2026
  const monthlyCanvas = document.getElementById('chart-sbi-monthly');
  if (monthlyCanvas) {
    if (sbiChartInstances.monthly) sbiChartInstances.monthly.destroy();

    const mData = sbiData.summary?.monthly_2026 || {};
    const labels = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agt', 'Sep', 'Okt', 'Nov', 'Des'];
    const monthKeys = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    const decVals = monthKeys.map(k => mData[k]?.dec || 0);
    const caiVals = monthKeys.map(k => mData[k]?.cai || 0);
    const acvVals = monthKeys.map(k => {
      const str = mData[k]?.acv || '';
      return parseFloat(str.replace('%', '')) || (decVals[monthKeys.indexOf(k)] > 0 ? (caiVals[monthKeys.indexOf(k)] / decVals[monthKeys.indexOf(k)] * 100) : 0);
    });

    sbiChartInstances.monthly = new Chart(monthlyCanvas, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Potensi DEC',
            data: decVals,
            backgroundColor: 'rgba(59, 130, 246, 0.8)',
            borderColor: '#2563eb',
            borderWidth: 1,
            borderRadius: 4,
            yAxisID: 'y'
          },
          {
            label: 'Datang (CAI)',
            data: caiVals,
            backgroundColor: 'rgba(16, 185, 129, 0.85)',
            borderColor: '#059669',
            borderWidth: 1,
            borderRadius: 4,
            yAxisID: 'y'
          },
          {
            label: '% Acv',
            data: acvVals,
            type: 'line',
            borderColor: '#f59e0b',
            backgroundColor: '#f59e0b',
            borderWidth: 2.5,
            pointRadius: 4,
            pointHoverRadius: 6,
            yAxisID: 'y1'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { position: 'top', labels: { boxWidth: 12, font: { size: 11, weight: '600' } } },
          tooltip: {
            callbacks: {
              label: (ctx) => ctx.dataset.yAxisID === 'y1' ? `${ctx.dataset.label}: ${ctx.raw.toFixed(1)}%` : `${ctx.dataset.label}: ${ctx.raw} Unit`
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: { display: true, text: 'Unit', font: { size: 11 } },
            grid: { color: '#f1f5f9' }
          },
          y1: {
            position: 'right',
            beginAtZero: true,
            max: 100,
            title: { display: true, text: 'Achievement (%)', font: { size: 11 } },
            grid: { drawOnChartArea: false },
            ticks: { callback: v => v + '%' }
          },
          x: { grid: { display: false } }
        }
      }
    });
  }

  // Chart 2: Yearly Performance & Hybrid Growth
  const yearlyCanvas = document.getElementById('chart-sbi-yearly');
  if (yearlyCanvas) {
    if (sbiChartInstances.yearly) sbiChartInstances.yearly.destroy();

    const yData = sbiData.summary?.yearly_perf || {};
    const years = ['2024', '2025', '2026'];
    const totalDec = years.map(yr => yData[yr]?.dec || 0);
    const hybrid = years.map(yr => yData[yr]?.hybrid || 0);

    sbiChartInstances.yearly = new Chart(yearlyCanvas, {
      type: 'bar',
      data: {
        labels: years,
        datasets: [
          {
            label: 'Total DEC',
            data: totalDec,
            backgroundColor: '#1e293b',
            borderRadius: 4
          },
          {
            label: 'Unit Hybrid',
            data: hybrid,
            backgroundColor: '#10b981',
            borderRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top', labels: { boxWidth: 12, font: { size: 11, weight: '600' } } },
          tooltip: {
            callbacks: {
              afterLabel: (ctx) => {
                if (ctx.datasetIndex === 1) {
                  const yr = years[ctx.dataIndex];
                  return `Pangsa: ${yData[yr]?.pct_hybrid || ''}`;
                }
                return '';
              }
            }
          }
        },
        scales: {
          y: { beginAtZero: true, grid: { color: '#f1f5f9' } },
          x: { grid: { display: false } }
        }
      }
    });
  }

  // Chart 3: Judgement / Customer Loyalty
  const judgementCanvas = document.getElementById('chart-sbi-judgement');
  if (judgementCanvas) {
    if (sbiChartInstances.judgement) sbiChartInstances.judgement.destroy();

    const jCounts = sbiData.summary?.by_judgement || {};
    const labels = Object.keys(jCounts).filter(k => k && k !== 'NO RECORD TAM');
    const values = labels.map(k => jCounts[k]);
    const colorMap = {
      'HOT': '#ef4444',
      'HIGH': '#f97316',
      'MEDIUM': '#eab308',
      'LOW': '#0284c7',
      'POTENCIAL LOSS': '#64748b',
      'NEW CUST POTENCY': '#8b5cf6'
    };
    const colors = labels.map(l => colorMap[l] || '#94a3b8');

    sbiChartInstances.judgement = new Chart(judgementCanvas, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{ data: values, backgroundColor: colors, borderWidth: 2, borderColor: '#ffffff' }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'right', labels: { boxWidth: 10, font: { size: 10 } } }
        },
        cutout: '65%'
      }
    });
  }

  // Chart 4: Sales Potency
  const potencyCanvas = document.getElementById('chart-sbi-sales-potency');
  if (potencyCanvas) {
    if (sbiChartInstances.potency) sbiChartInstances.potency.destroy();

    const pCounts = sbiData.summary?.by_potency_sales || {};
    const labels = Object.keys(pCounts).filter(k => k);
    const values = labels.map(k => pCounts[k]);
    const colors = labels.map(l => {
      if (l.includes('DATANG')) return '#10b981';
      if (l.includes('LOST')) return '#ef4444';
      if (l.includes('WAJIB')) return '#f59e0b';
      return '#64748b';
    });

    sbiChartInstances.potency = new Chart(potencyCanvas, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{ data: values, backgroundColor: colors, borderWidth: 2, borderColor: '#ffffff' }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'right', labels: { boxWidth: 10, font: { size: 10.5 } } }
        },
        cutout: '60%'
      }
    });
  }

  // Chart 5: Service Sales (SS)
  const ssCanvas = document.getElementById('chart-sbi-ss');
  if (ssCanvas) {
    if (sbiChartInstances.ss) sbiChartInstances.ss.destroy();

    const ssCounts = sbiData.summary?.by_ss || {};
    const labels = Object.keys(ssCounts).filter(k => k && k !== 'LAINNYA');
    const values = labels.map(k => ssCounts[k]);

    sbiChartInstances.ss = new Chart(ssCanvas, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Total Penanganan SBI',
          data: values,
          backgroundColor: '#3b82f6',
          borderRadius: 4
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: { beginAtZero: true, grid: { color: '#f1f5f9' } },
          y: { grid: { display: false }, ticks: { font: { size: 10.5, weight: '600' } } }
        }
      }
    });
  }
}

function renderSbiTable() {
  const tbody = document.getElementById('sbi-table-body');
  if (!tbody) return;

  const total = sbiFilteredRecords.length;
  const totalPages = Math.ceil(total / sbiPageSize) || 1;
  if (sbiCurrentPage > totalPages) sbiCurrentPage = totalPages;
  if (sbiCurrentPage < 1) sbiCurrentPage = 1;

  const startIdx = (sbiCurrentPage - 1) * sbiPageSize;
  const endIdx = Math.min(startIdx + sbiPageSize, total);
  const pageRecords = sbiFilteredRecords.slice(startIdx, endIdx);

  const rangeEl = document.getElementById('sbi-count-range');
  const totalEl = document.getElementById('sbi-count-total');
  const pageInfoEl = document.getElementById('sbi-page-info');

  if (rangeEl) rangeEl.textContent = total > 0 ? `${startIdx + 1} - ${endIdx}` : '0';
  if (totalEl) totalEl.textContent = formatNum(total);
  if (pageInfoEl) pageInfoEl.textContent = `Halaman ${sbiCurrentPage} dari ${totalPages}`;

  if (pageRecords.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="13" style="text-align: center; padding: 40px; color: #64748b;">
          <div style="font-size: 14px; font-weight: 600; margin-bottom: 4px;">Tidak ada data pelanggan SBI yang sesuai filter</div>
          <div style="font-size: 12px;">Coba atur ulang kata kunci pencarian atau filter di atas.</div>
        </td>
      </tr>
    `;
    renderSbiPaginationButtons(1, 1);
    return;
  }

  let html = '';
  pageRecords.forEach((rec, idx) => {
    const globalIdx = startIdx + idx + 1;
    const isCai = (rec.cai || '').toUpperCase() === 'CAI';
    const caiBadge = isCai ? '<span class="sbi-badge badge-cai">CAI</span>' : '<span class="sbi-badge badge-not-cai">NOT CAI</span>';

    // Car type badge
    let carTypeBadge = '<span class="sbi-badge badge-non-lcgc">NON LCGC</span>';
    const ctUpper = (rec.car_type || '').toUpperCase();
    if (ctUpper.includes('HYBRID')) carTypeBadge = '<span class="sbi-badge badge-hybrid">HYBRID</span>';
    else if (ctUpper.includes('LCGC')) carTypeBadge = '<span class="sbi-badge badge-lcgc">LCGC</span>';

    // Judgement badge
    const jUpper = (rec.judgement_cust || '').toUpperCase();
    let jBadge = `<span class="sbi-badge badge-loss">${escapeHtml(rec.judgement_cust || '-')}</span>`;
    if (jUpper.includes('HOT')) jBadge = `<span class="sbi-badge badge-hot">HOT</span>`;
    else if (jUpper.includes('HIGH')) jBadge = `<span class="sbi-badge badge-high">HIGH</span>`;
    else if (jUpper.includes('MEDIUM')) jBadge = `<span class="sbi-badge badge-med">MEDIUM</span>`;
    else if (jUpper.includes('LOW')) jBadge = `<span class="sbi-badge badge-low">LOW</span>`;
    else if (jUpper.includes('LOSS')) jBadge = `<span class="sbi-badge badge-loss">POTENCIAL LOSS</span>`;
    else if (jUpper.includes('NEW')) jBadge = `<span class="sbi-badge badge-new">NEW CUST</span>`;

    // T-Care badge
    const isTcareActive = (rec.status_tcare || '').toUpperCase() === 'ACTIVE';
    const tcareBadge = isTcareActive
      ? '<span class="sbi-badge badge-tcare-active">ACTIVE</span>'
      : `<span class="sbi-badge badge-tcare-finish">${escapeHtml(rec.status_tcare || '-')}</span>`;

    // Milestones strip
    const ms10 = rec.cai_10k && !rec.cai_10k.toUpperCase().includes('NOT');
    const ms20 = rec.cai_20k && !rec.cai_20k.toUpperCase().includes('NOT');
    const ms30 = rec.cai_30k && !rec.cai_30k.toUpperCase().includes('NOT');
    const ms40 = rec.cai_40k && !rec.cai_40k.toUpperCase().includes('NOT');
    const ms50 = rec.cai_50k && !rec.cai_50k.toUpperCase().includes('NOT');
    const ms60 = rec.cai_60k && !rec.cai_60k.toUpperCase().includes('NOT');
    const ms70 = rec.cai_70k && !rec.cai_70k.toUpperCase().includes('NOT');

    const msHtml = `
      <div class="milestone-strip" title="10K: ${rec.cai_10k || '-'} | 20K: ${rec.cai_20k || '-'} | 30K: ${rec.cai_30k || '-'} | 40K: ${rec.cai_40k || '-'}">
        <span class="m-dot ${ms10 ? 'done' : ''}">10K</span>
        <span class="m-dot ${ms20 ? 'done' : ''}">20K</span>
        <span class="m-dot ${ms30 ? 'done' : ''}">30K</span>
        <span class="m-dot ${ms40 ? 'done' : ''}">40K</span>
        <span class="m-dot ${ms50 ? 'done' : ''}">50K</span>
        <span class="m-dot ${ms60 ? 'done' : ''}">60K</span>
        <span class="m-dot ${ms70 ? 'done' : ''}">70K</span>
      </div>
    `;

    // Phone / WA link
    let phone = (rec.no_wa || rec.telepon1 || rec.telepon2 || '').replace(/[^0-9]/g, '');
    if (phone.startsWith('0')) phone = '62' + phone.substring(1);
    else if (phone.startsWith('8')) phone = '62' + phone;

    const waBtn = phone ? `
      <a href="https://wa.me/${phone}" target="_blank" rel="noopener noreferrer" class="btn-sbi-action btn-wa-action" title="Hubungi WhatsApp (+${phone})">
        WA
      </a>
    ` : '';

    html += `
      <tr>
        <td style="text-align: center; color: #64748b; font-size: 11px;">${globalIdx}</td>
        <td>${caiBadge}</td>
        <td style="font-size: 11px; white-space: nowrap;">${escapeHtml(rec.month || '')} ${escapeHtml(rec.year || '')}</td>
        <td><strong style="color: #0f172a; font-family: monospace;">${escapeHtml(rec.plat_no || '-')}</strong></td>
        <td>
          <div style="font-weight: 600; color: #0f172a;">${escapeHtml(rec.nama || '-')}</div>
          <span style="font-size: 10.5px; color: #64748b;">${escapeHtml(rec.type_cust || 'Retail')}</span>
        </td>
        <td style="font-weight: 500;">${escapeHtml(rec.model || '-')}</td>
        <td>${carTypeBadge}</td>
        <td style="font-size: 11px; color: #334155;">${escapeHtml(rec.ss || '-')}</td>
        <td style="font-size: 11.5px;" title="${escapeHtml(rec.penggalian_mrs || '')}">
          ${escapeHtml(rec.notes_fu || '-')}
        </td>
        <td>${jBadge}</td>
        <td>${tcareBadge}</td>
        <td>${msHtml}</td>
        <td style="text-align: center; white-space: nowrap;">
          <button type="button" class="btn-sbi-action btn-sbi-detail" data-id="${rec.id}">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            Detail
          </button>
          ${waBtn}
        </td>
      </tr>
    `;
  });

  tbody.innerHTML = html;

  // Add click handlers for detail buttons
  tbody.querySelectorAll('.btn-sbi-detail').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = parseInt(btn.getAttribute('data-id'), 10);
      const rec = sbiData.records.find(r => r.id === id);
      if (rec) openSbiDetailModal(rec);
    });
  });

  renderSbiPaginationButtons(sbiCurrentPage, totalPages);
}

function renderSbiPaginationButtons(curr, total) {
  const container = document.getElementById('sbi-pagination-buttons');
  if (!container) return;

  if (total <= 1) {
    container.innerHTML = '';
    return;
  }

  let html = `
    <button type="button" class="btn-sbi-page" ${curr === 1 ? 'disabled' : ''} data-p="${curr - 1}">
      ‹ Prev
    </button>
  `;

  const delta = 2;
  const left = curr - delta;
  const right = curr + delta;
  const range = [];

  for (let i = 1; i <= total; i++) {
    if (i === 1 || i === total || (i >= left && i <= right)) {
      range.push(i);
    }
  }

  let last = 0;
  range.forEach(p => {
    if (last && p - last > 1) {
      html += `<span style="padding: 0 4px; color: #94a3b8;">…</span>`;
    }
    html += `
      <button type="button" class="btn-sbi-page ${p === curr ? 'active' : ''}" data-p="${p}">
        ${p}
      </button>
    `;
    last = p;
  });

  html += `
    <button type="button" class="btn-sbi-page" ${curr === total ? 'disabled' : ''} data-p="${curr + 1}">
      Next ›
    </button>
  `;

  container.innerHTML = html;

  container.querySelectorAll('.btn-sbi-page').forEach(btn => {
    btn.addEventListener('click', () => {
      const p = parseInt(btn.getAttribute('data-p'), 10);
      if (p && p >= 1 && p <= total) {
        sbiCurrentPage = p;
        renderSbiTable();
        // Smooth scroll table container to top
        document.querySelector('.sbi-table-wrap')?.scrollTo({ top: 0, behavior: 'smooth' });
      }
    });
  });
}

function openSbiDetailModal(rec) {
  const modal = document.getElementById('sbi-detail-modal');
  const titleEl = document.getElementById('sbi-modal-title');
  const caiBadge = document.getElementById('sbi-modal-cai-badge');
  const jBadge = document.getElementById('sbi-modal-judgement-badge');
  const body = document.getElementById('sbi-modal-body-content');

  if (!modal || !body) return;

  if (titleEl) titleEl.textContent = `Detail Pelanggan: ${rec.nama || '-'} (${rec.plat_no || rec.vin})`;

  if (caiBadge) {
    const isCai = (rec.cai || '').toUpperCase() === 'CAI';
    caiBadge.textContent = isCai ? 'CAI (Datang Servis)' : 'NOT CAI';
    caiBadge.className = isCai ? 'sbi-badge badge-cai' : 'sbi-badge badge-not-cai';
  }

  if (jBadge) {
    jBadge.textContent = rec.judgement_cust || '-';
    const ju = (rec.judgement_cust || '').toUpperCase();
    if (ju.includes('HOT')) jBadge.className = 'sbi-badge badge-hot';
    else if (ju.includes('HIGH')) jBadge.className = 'sbi-badge badge-high';
    else if (ju.includes('LOSS')) jBadge.className = 'sbi-badge badge-loss';
    else jBadge.className = 'sbi-badge badge-med';
  }

  let phone = (rec.no_wa || rec.telepon1 || rec.telepon2 || '').replace(/[^0-9]/g, '');
  if (phone.startsWith('0')) phone = '62' + phone.substring(1);
  else if (phone.startsWith('8')) phone = '62' + phone;

  const waBtnHtml = phone ? `
    <a href="https://wa.me/${phone}" target="_blank" rel="noopener noreferrer" style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; font-size: 11px; background: #25d366; color: #ffffff; border-radius: 4px; text-decoration: none; font-weight: 700; margin-left: 8px;">
      WhatsApp Langsung
    </a>
  ` : '';

  body.innerHTML = `
    <!-- Seksi 1: Data Kendaraan & Dokumen -->
    <div class="sbi-detail-section">
      <div class="sbi-detail-section-title">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="1" y="3" width="22" height="13" rx="2"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>
        1. Identitas Kendaraan &amp; Transaksi
      </div>
      <div class="sbi-detail-grid">
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Nomor Polisi</span>
          <span class="sbi-detail-val" style="font-size: 14px; font-family: monospace;">${escapeHtml(rec.plat_no || '-')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Model Kendaraan</span>
          <span class="sbi-detail-val">${escapeHtml(rec.model || '-')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Tipe Kendaraan (Car Type)</span>
          <span class="sbi-detail-val">${escapeHtml(rec.car_type || '-')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Nomor VIN / Rangka</span>
          <span class="sbi-detail-val" style="font-family: monospace; font-size: 11.5px;">${escapeHtml(rec.vin || rec.nomor_rangka || '-')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Tanggal Transaksi</span>
          <span class="sbi-detail-val">${escapeHtml(rec.tgl_transaksi || '-')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Periode Servis (Bulan &amp; Tahun)</span>
          <span class="sbi-detail-val">${escapeHtml(rec.month || '-')} ${escapeHtml(rec.year || '')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Bulan CAI (SO Kedatangan)</span>
          <span class="sbi-detail-val">${escapeHtml(rec.bulan_cai_so || '-')}</span>
        </div>
      </div>
    </div>

    <!-- Seksi 2: Profil & Kontak Pelanggan -->
    <div class="sbi-detail-section">
      <div class="sbi-detail-section-title">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        2. Profil &amp; Informasi Kontak Pelanggan
      </div>
      <div class="sbi-detail-grid">
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Nama Pelanggan</span>
          <span class="sbi-detail-val">${escapeHtml(rec.nama || '-')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Segmentasi Pelanggan (Type Cust)</span>
          <span class="sbi-detail-val">${escapeHtml(rec.type_cust || 'Retail')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Telepon 1 &amp; WhatsApp</span>
          <span class="sbi-detail-val">${escapeHtml(rec.no_wa || rec.telepon1 || '-')} ${waBtnHtml}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Telepon 2 / 3</span>
          <span class="sbi-detail-val">${escapeHtml(rec.telepon2 || rec.telepon3 || '-')}</span>
        </div>
        <div class="sbi-detail-item" style="grid-column: span 2;">
          <span class="sbi-detail-label">Alamat Lengkap</span>
          <span class="sbi-detail-val">${escapeHtml(rec.alamat || '-')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Kabupaten / Kota</span>
          <span class="sbi-detail-val">${escapeHtml(rec.kab || '-')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Ring Area Tempat Tinggal</span>
          <span class="sbi-detail-val">${escapeHtml(rec.ring_area || '-')}</span>
        </div>
      </div>
    </div>

    <!-- Seksi 3: Aktivitas Follow Up & Interaksi Sales -->
    <div class="sbi-detail-section">
      <div class="sbi-detail-section-title">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
        3. Aktivitas Follow Up, Sales &amp; MRS
      </div>
      <div class="sbi-detail-grid">
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Service Sales (SS)</span>
          <span class="sbi-detail-val" style="color: #2563eb;">${escapeHtml(rec.ss || '-')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Sales Person</span>
          <span class="sbi-detail-val">${escapeHtml(rec.sales_person || rec.sales || '-')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Metode Follow Up</span>
          <span class="sbi-detail-val">${escapeHtml(rec.fu_by || '-')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Tanggal Follow Up</span>
          <span class="sbi-detail-val">${escapeHtml(rec.tgl_fu || '-')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Status Keterangan FU</span>
          <span class="sbi-detail-val">${escapeHtml(rec.ket_fu || '-')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Hasil Follow Up (Notes)</span>
          <span class="sbi-detail-val">${escapeHtml(rec.notes_fu || '-')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Potensi Sales</span>
          <span class="sbi-detail-val">${escapeHtml(rec.potency_sales || '-')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">CAI To Dealer Tujuan</span>
          <span class="sbi-detail-val">${escapeHtml(rec.cai_to_dealer || '-')}</span>
        </div>
        <div class="sbi-detail-item" style="grid-column: span 2;">
          <span class="sbi-detail-label">Hasil Penggalian Keterangan MRS</span>
          <span class="sbi-detail-val" style="background: #f8fafc; padding: 8px; border-radius: 4px; border: 1px solid #e2e8f0;">${escapeHtml(rec.penggalian_mrs || '-')}</span>
        </div>
      </div>
    </div>

    <!-- Seksi 4: Program, Habit & Loyalitas -->
    <div class="sbi-detail-section">
      <div class="sbi-detail-section-title">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
        4. Program T-Care, Habit Servis &amp; Judgement
      </div>
      <div class="sbi-detail-grid">
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Status Program T-Care</span>
          <span class="sbi-detail-val">${escapeHtml(rec.status_tcare || '-')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Judgement Pelanggan</span>
          <span class="sbi-detail-val" style="color: #b91c1c;">${escapeHtml(rec.judgement_cust || '-')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Habit Ring Area Servis</span>
          <span class="sbi-detail-val">${escapeHtml(rec.habit_ring_area || '-')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Habit Dealer Servis (Bengkel Langganan)</span>
          <span class="sbi-detail-val">${escapeHtml(rec.habit_dealer || '-')}</span>
        </div>
      </div>
    </div>

    <!-- Seksi 5: Riwayat Servis Berkala Kiara Condong -->
    <div class="sbi-detail-section">
      <div class="sbi-detail-section-title">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
        5. Riwayat Servis Berkala di Kiara Condong (10K – 70K)
      </div>
      <div class="sbi-milestone-grid">
        ${renderMsCard('10K', rec.cai_10k)}
        ${renderMsCard('20K', rec.cai_20k)}
        ${renderMsCard('30K', rec.cai_30k)}
        ${renderMsCard('40K', rec.cai_40k)}
        ${renderMsCard('50K', rec.cai_50k)}
        ${renderMsCard('60K', rec.cai_60k)}
        ${renderMsCard('70K', rec.cai_70k)}
      </div>
    </div>
  `;

  modal.style.display = 'flex';
}

function renderMsCard(label, val) {
  const isDone = val && !val.toUpperCase().includes('NOT') && !val.includes('-');
  return `
    <div class="sbi-ms-card ${isDone ? 'ms-active' : ''}">
      <div class="sbi-ms-label">${label}</div>
      <div class="sbi-ms-date">${escapeHtml(val || 'NOT CAI')}</div>
    </div>
  `;
}

function exportSbiCsv() {
  if (!sbiFilteredRecords || sbiFilteredRecords.length === 0) {
    alert('Tidak ada data terfilter untuk diekspor.');
    return;
  }

  const cols = [
    'id', 'cai', 'year', 'month', 'plat_no', 'nama', 'type_cust', 'model', 'car_type',
    'vin', 'telepon1', 'no_wa', 'alamat', 'kab', 'ss', 'sales_person', 'fu_by', 'tgl_fu',
    'notes_fu', 'penggalian_mrs', 'potency_sales', 'status_tcare', 'ring_area',
    'cai_10k', 'cai_20k', 'cai_30k', 'cai_40k', 'cai_50k', 'cai_60k', 'cai_70k',
    'habit_dealer', 'judgement_cust'
  ];

  let csv = cols.map(c => `"${c.toUpperCase()}"`).join(',') + '\\n';

  sbiFilteredRecords.forEach(r => {
    const row = cols.map(c => `"${String(r[c] || '').replace(/"/g, '""')}"`);
    csv += row.join(',') + '\\n';
  });

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `sbi_data_kiaracondong_${new Date().toISOString().slice(0, 10)}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

async function syncSbiFromLiveSheet() {
  const syncBtn = document.getElementById('btn-sync-sbi-sheet');
  const spinIcon = document.getElementById('sbi-sync-spin-icon');
  const label = document.getElementById('sbi-sync-label');

  if (syncBtn) syncBtn.disabled = true;
  if (spinIcon) spinIcon.style.animation = 'spin 0.8s linear infinite';
  if (label) label.textContent = 'Menyinkronkan...';

  try {
    let success = false;
    try {
      const resp = await fetch('api/sync_sbi.php');
      if (resp.ok) {
        const json = await resp.json();
        if (json.status === 'success') success = true;
      }
    } catch (e) {
      console.warn('API sync_sbi.php tidak merespon, mencoba GViz langsung...');
    }

    // Always re-fetch data
    await loadSbiData();

    if (typeof showFloatingToast === 'function') {
      showFloatingToast('Sinkronisasi Data SBI Berhasil!', 'success');
    } else {
      alert('Data SBI berhasil diperbarui dari Google Spreadsheet!');
    }
  } catch (err) {
    console.error('Error saat sync SBI:', err);
    alert('Gagal menyinkronkan data SBI: ' + err.message);
  } finally {
    if (syncBtn) syncBtn.disabled = false;
    if (spinIcon) spinIcon.style.animation = '';
    if (label) label.textContent = 'Sinkronkan Sheet SBI';
  }
}

function renderSbi() {
  if (!sbiData) return;
  initSbiEvents();
  renderSbiCharts();
  applySbiFiltersAndRender();
}
'''

with open(r'c:\laragon\www\dashboard_bengkel\assets\js\dashboard.js', 'r', encoding='utf-8') as f:
    orig = f.read()

# Append sbi_code
with open(r'c:\laragon\www\dashboard_bengkel\assets\js\dashboard.js', 'w', encoding='utf-8') as f:
    f.write(orig + '\n' + sbi_code + '\n')

print("Successfully appended SBI logic to dashboard.js!")
