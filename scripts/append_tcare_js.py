import os

code = r'''
// ==========================================================================
// T-CARE EXECUTIVE INTELLIGENCE & RETENTION DASHBOARD
// Layout faithfully following Google Sheet "DASHBOARD"
// ==========================================================================
let tcareData = null;
let tcareCurrentMatrixTab = 'by_customer_type';
let tcareRawPage = 1;
let tcareRawPageSize = 25;
let tcareFilteredRecords = [];
let tcareActiveQuickFilter = 'all';
let tcareEventsInitialized = false;

async function loadTcareData() {
  try {
    const cacheBuster = '?v=' + Date.now();
    let res = await fetch('data/tcare_data.json' + cacheBuster);
    if (!res.ok) {
      res = await fetch('data/tcare_data.json');
    }
    if (res.ok) {
      tcareData = await res.json();
      console.log('T-Care data loaded:', tcareData?.records?.length, 'records');
      renderTcare();
    }
  } catch (err) {
    console.error('Error loading T-Care data:', err);
  }
}

function initTcareEvents() {
  if (tcareEventsInitialized) return;
  tcareEventsInitialized = true;

  // Matrix Sub-Tabs
  document.querySelectorAll('.btn-tcare-matrix-tab').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.btn-tcare-matrix-tab').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      tcareCurrentMatrixTab = btn.getAttribute('data-matrix') || 'by_customer_type';
      renderTcareSegmentedMatrix();
    });
  });

  // Raw Filter dropdowns
  ['tcare-raw-filter-program', 'tcare-raw-filter-ring', 'tcare-raw-filter-custtype', 'tcare-raw-filter-vcat', 'tcare-raw-filter-dealer'].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener('change', () => {
        tcareRawPage = 1;
        applyTcareRawFiltersAndRender();
      });
    }
  });

  // Raw Search Input
  const searchInp = document.getElementById('tcare-raw-search-input');
  if (searchInp) {
    searchInp.addEventListener('input', () => {
      tcareRawPage = 1;
      applyTcareRawFiltersAndRender();
    });
  }

  // Quick Filter Pills
  document.querySelectorAll('[data-tcare-quick]').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('[data-tcare-quick]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      tcareActiveQuickFilter = btn.getAttribute('data-tcare-quick') || 'all';
      tcareRawPage = 1;
      applyTcareRawFiltersAndRender();
    });
  });

  // Page Size Select
  const pageSizeSelect = document.getElementById('tcare-raw-page-size');
  if (pageSizeSelect) {
    pageSizeSelect.addEventListener('change', (e) => {
      tcareRawPageSize = e.target.value === 'all' ? 999999 : parseInt(e.target.value, 10);
      tcareRawPage = 1;
      renderTcareRawTable();
    });
  }

  // Export CSV
  const btnExport = document.getElementById('btn-export-tcare-raw');
  if (btnExport) {
    btnExport.addEventListener('click', exportTcareRawCsv);
  }

  // Sync Button
  const btnSync = document.getElementById('btn-sync-tcare');
  if (btnSync) {
    btnSync.addEventListener('click', syncTcareData);
  }

  // Modal Close
  const modalClose = document.getElementById('btn-close-tcare-modal');
  const modal = document.getElementById('tcare-detail-modal');
  if (modalClose && modal) {
    modalClose.addEventListener('click', () => {
      modal.classList.remove('active');
    });
    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.classList.remove('active');
    });
  }
}

async function syncTcareData() {
  const btn = document.getElementById('btn-sync-tcare');
  const spinIcon = document.getElementById('tcare-sync-spinner');
  try {
    if (btn) btn.disabled = true;
    if (spinIcon) spinIcon.style.animation = 'spin 0.8s linear infinite';
    await loadTcareData();
    if (typeof showFloatingToast === 'function') {
      showFloatingToast('Data T-Care berhasil dimuat ulang & disinkronkan!', 'success');
    } else {
      alert('Data T-Care berhasil dimuat ulang!');
    }
  } catch (err) {
    alert('Gagal sinkronisasi: ' + err.message);
  } finally {
    if (btn) btn.disabled = false;
    if (spinIcon) spinIcon.style.animation = '';
  }
}

function renderTcare() {
  if (!tcareData) return;
  initTcareEvents();
  renderTcareMonitoringTable();
  renderTcareCharacteristics();
  renderTcareMilestoneSteppers();
  renderTcareCustomerTypeCompare();
  renderTcareMasterPotencyGrid();
  renderTcareSegmentedMatrix();
  applyTcareRawFiltersAndRender();
}

function renderTcareMonitoringTable() {
  const tbody = document.getElementById('tcare-monitoring-tbody');
  if (!tbody || !tcareData.program_summary) return;

  tbody.innerHTML = tcareData.program_summary.map(item => {
    const isTotal = item.program === 'TOTAL';
    const trClass = isTotal ? 'style="background: #f1f5f9; font-weight: 800; border-top: 2px solid #cbd5e1;"' : '';
    return `
      <tr ${trClass}>
        <td style="font-weight: 700; color: #0f172a;">${escapeHtml(item.program)}</td>
        <td style="text-align: right; font-weight: 600;">${formatNumber(item.dec)}</td>
        <td class="td-same-outlet" style="text-align: right;">${formatNumber(item.same_outlet.volume)}</td>
        <td class="td-same-outlet" style="text-align: right; font-weight: 700;">${escapeHtml(item.same_outlet.rate)}</td>
        <td class="td-tunas-group" style="text-align: right;">${formatNumber(item.tunas_group.volume)}</td>
        <td class="td-tunas-group" style="text-align: right; font-weight: 700;">${escapeHtml(item.tunas_group.rate)}</td>
        <td class="td-other-dealer" style="text-align: right;">${formatNumber(item.other_dealer.volume)}</td>
        <td class="td-other-dealer" style="text-align: right; font-weight: 700;">${escapeHtml(item.other_dealer.rate)}</td>
        <td class="td-total-rate" style="text-align: right;">${formatNumber(item.total_cai)}</td>
        <td class="td-total-rate" style="text-align: right; color: #2563eb; font-weight: 800;">${escapeHtml(item.overall_rate)}</td>
      </tr>
    `;
  }).join('');

  // Update KPI bottom badges
  const pMap = {};
  tcareData.program_summary.forEach(p => { pMap[p.program] = p; });
  if (pMap['T-CARE']) {
    const elR = document.getElementById('kpi-tcare-rate');
    const elV = document.getElementById('kpi-tcare-vol');
    if (elR) elR.textContent = pMap['T-CARE'].overall_rate;
    if (elV) elV.textContent = `${formatNumber(pMap['T-CARE'].total_cai)} / ${formatNumber(pMap['T-CARE'].dec)} DEC`;
  }
  if (pMap['T-CARE LITE']) {
    const elR = document.getElementById('kpi-lite-rate');
    const elV = document.getElementById('kpi-lite-vol');
    if (elR) elR.textContent = pMap['T-CARE LITE'].overall_rate;
    if (elV) elV.textContent = `${formatNumber(pMap['T-CARE LITE'].total_cai)} / ${formatNumber(pMap['T-CARE LITE'].dec)} DEC`;
  }
  if (pMap['T-CARE LITE+']) {
    const elR = document.getElementById('kpi-liteplus-rate');
    const elV = document.getElementById('kpi-liteplus-vol');
    if (elR) elR.textContent = pMap['T-CARE LITE+'].overall_rate;
    if (elV) elV.textContent = `${formatNumber(pMap['T-CARE LITE+'].total_cai)} / ${formatNumber(pMap['T-CARE LITE+'].dec)} DEC`;
  }
}

function renderTcareCharacteristics() {
  const k = tcareData.komposisi;
  if (!k) return;

  const setEl = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  };

  // Customer Type
  if (k.customer_type) {
    setEl('tcare-comp-retail', formatNumber(k.customer_type.retail?.count || 0));
    setEl('tcare-comp-retail-pct', k.customer_type.retail?.rate || '0%');
    setEl('tcare-comp-fleet', formatNumber(k.customer_type.fleet?.count || 0));
    setEl('tcare-comp-fleet-pct', k.customer_type.fleet?.rate || '0%');
  }

  // Ring Area
  if (k.ring_area) {
    setEl('tcare-comp-r1', formatNumber(k.ring_area.ring1?.count || 0));
    setEl('tcare-comp-r1-pct', k.ring_area.ring1?.rate || '0%');
    setEl('tcare-comp-r2', formatNumber(k.ring_area.ring2?.count || 0));
    setEl('tcare-comp-r2-pct', k.ring_area.ring2?.rate || '0%');
    setEl('tcare-comp-r3', formatNumber(k.ring_area.ring3?.count || 0));
    setEl('tcare-comp-r3-pct', k.ring_area.ring3?.rate || '0%');
    setEl('tcare-comp-ooa', formatNumber(k.ring_area.out_of_area?.count || 0));
    setEl('tcare-comp-ooa-pct', k.ring_area.out_of_area?.rate || '0%');
  }

  // Punctuality
  if (k.punctuality) {
    setEl('tcare-comp-punctual', formatNumber(k.punctuality.punctual?.count || 0));
    setEl('tcare-comp-punctual-pct', k.punctuality.punctual?.rate || '0%');
    setEl('tcare-comp-non-punctual', formatNumber(k.punctuality.non_punctual?.count || 0));
    setEl('tcare-comp-non-punctual-pct', k.punctuality.non_punctual?.rate || '0%');
  }

  // Vehicle Type
  if (k.vehicle_type) {
    setEl('tcare-comp-midlow', formatNumber(k.vehicle_type.middle_low?.count || 0));
    setEl('tcare-comp-midlow-pct', k.vehicle_type.middle_low?.rate || '0%');
    setEl('tcare-comp-midup', formatNumber(k.vehicle_type.middle_up?.count || 0));
    setEl('tcare-comp-midup-pct', k.vehicle_type.middle_up?.rate || '0%');
    setEl('tcare-comp-hybrid', formatNumber(k.vehicle_type.hybrid?.count || 0));
    setEl('tcare-comp-hybrid-pct', k.vehicle_type.hybrid?.rate || '0%');
  }
}

function renderTcareMilestoneSteppers() {
  // Stepper A: By Program
  const cProg = document.getElementById('tcare-stepper-program-container');
  if (cProg && tcareData.cai_own_sales_by_program) {
    cProg.innerHTML = tcareData.cai_own_sales_by_program.map(item => {
      const steps = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th'].map(m => {
        const rate = item.rates?.[m] || '0%';
        const numVal = parseFloat(rate) || 0;
        let bg = '#f8fafc';
        let color = '#475569';
        if (numVal >= 80) { bg = '#ecfdf5'; color = '#059669'; }
        else if (numVal >= 50) { bg = '#eff6ff'; color = '#2563eb'; }
        else if (numVal >= 20) { bg = '#fffbeb'; color = '#d97706'; }
        else if (numVal > 0) { bg = '#fef2f2'; color = '#dc2626'; }
        return `
          <div class="tcare-step-box" style="background: ${bg};">
            <div class="tcare-step-num">${m}</div>
            <div class="tcare-step-pct" style="color: ${color};">${escapeHtml(rate)}</div>
          </div>
        `;
      }).join('');

      return `
        <div class="tcare-prog-row">
          <div>
            <div class="tcare-prog-label">${escapeHtml(item.program)}</div>
            <div style="font-size: 10.5px; color: #64748b;">Potensi: <strong>${formatNumber(item.potensi)}</strong></div>
          </div>
          ${steps}
        </div>
      `;
    }).join('');
  }

  // Stepper B: By Vehicle Type
  const cVtype = document.getElementById('tcare-stepper-vtype-container');
  if (cVtype && tcareData.cai_own_sales_by_vehicle_type) {
    cVtype.innerHTML = tcareData.cai_own_sales_by_vehicle_type.map(item => {
      const steps = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th'].map(m => {
        const rate = item.rates?.[m] || '0%';
        const numVal = parseFloat(rate) || 0;
        let bg = '#f8fafc';
        let color = '#475569';
        if (numVal >= 80) { bg = '#ecfdf5'; color = '#059669'; }
        else if (numVal >= 50) { bg = '#eff6ff'; color = '#2563eb'; }
        else if (numVal >= 20) { bg = '#fffbeb'; color = '#d97706'; }
        else if (numVal > 0) { bg = '#fef2f2'; color = '#dc2626'; }
        return `
          <div class="tcare-step-box" style="background: ${bg};">
            <div class="tcare-step-num">${m}</div>
            <div class="tcare-step-pct" style="color: ${color};">${escapeHtml(rate)}</div>
          </div>
        `;
      }).join('');

      return `
        <div class="tcare-prog-row">
          <div>
            <div class="tcare-prog-label">${escapeHtml(item.category)}</div>
            <div style="font-size: 10.5px; color: #64748b;">Potensi: <strong>${formatNumber(item.potensi)}</strong></div>
          </div>
          ${steps}
        </div>
      `;
    }).join('');
  }
}

function renderTcareCustomerTypeCompare() {
  const comp = tcareData.customer_type_comparison;
  if (!comp) return;

  const renderGroup = (tbodyId, grpData) => {
    const tbody = document.getElementById(tbodyId);
    if (!tbody || !grpData) return;
    const progs = [
      { name: 'T-CARE', data: grpData.t_care },
      { name: 'T-CARE LITE', data: grpData.t_care_lite },
      { name: 'T-CARE LITE+', data: grpData.t_care_lite_plus }
    ];
    let totalPot = 0;
    let totalCai = 0;

    const rows = progs.map(p => {
      const pot = p.data?.potensi || 0;
      const cai = p.data?.cai || 0;
      const rate = p.data?.rate || '0%';
      totalPot += pot;
      totalCai += cai;
      return `
        <tr>
          <td style="font-weight: 600;">${escapeHtml(p.name)}</td>
          <td style="text-align: right;">${formatNumber(pot)}</td>
          <td style="text-align: right;">${formatNumber(cai)}</td>
          <td style="text-align: right; font-weight: 800; color: #2563eb;">${escapeHtml(rate)}</td>
        </tr>
      `;
    });

    const totRate = totalPot > 0 ? ((totalCai / totalPot) * 100).toFixed(1) + '%' : '0%';
    rows.push(`
      <tr style="background: #f1f5f9; font-weight: 800; border-top: 2px solid #cbd5e1;">
        <td>TOTAL</td>
        <td style="text-align: right;">${formatNumber(totalPot)}</td>
        <td style="text-align: right;">${formatNumber(totalCai)}</td>
        <td style="text-align: right; color: #059669; font-weight: 900;">${totRate}</td>
      </tr>
    `);
    tbody.innerHTML = rows.join('');
  };

  renderGroup('tcare-retail-tbody', comp.retail);
  renderGroup('tcare-fleet-tbody', comp.fleet);
}

function renderTcareMasterPotencyGrid() {
  const tbody = document.getElementById('tcare-potency-tbody');
  if (!tbody || !tcareData.retention_potency_summary) return;

  tbody.innerHTML = tcareData.retention_potency_summary.map(item => {
    const isTotal = item.program.includes('TOTAL');
    const trClass = isTotal ? 'style="background: #f1f5f9; font-weight: 800; border-top: 2px solid #cbd5e1;"' : '';
    const mCols = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th'].map(m => {
      const d = item.milestones?.[m] || { potensi: 0, cai: 0, rate: '0%' };
      return `
        <td style="text-align: right;">${formatNumber(d.potensi)}</td>
        <td style="text-align: right;">${formatNumber(d.cai)}</td>
        <td style="text-align: right; font-weight: 700; color: #2563eb;">${escapeHtml(d.rate)}</td>
      `;
    }).join('');

    return `
      <tr ${trClass}>
        <td style="font-weight: 700; color: #0f172a;">${escapeHtml(item.program)}</td>
        ${mCols}
      </tr>
    `;
  }).join('');
}

function renderTcareSegmentedMatrix() {
  const tbody = document.getElementById('tcare-matrix-tbody');
  if (!tbody || !tcareData.segmented_matrices) return;

  const rows = tcareData.segmented_matrices[tcareCurrentMatrixTab] || [];
  if (rows.length === 0) {
    tbody.innerHTML = '<tr><td colspan="53" style="text-align: center; padding: 20px;">Tidak ada data matriks</td></tr>';
    return;
  }

  tbody.innerHTML = rows.map(r => {
    const isSub = r.category.includes('TOTAL') && !r.category.includes('GRAND');
    const isGrand = r.category.includes('GRAND');
    let trClass = '';
    if (isGrand) trClass = 'class="row-grandtotal"';
    else if (isSub) trClass = 'class="row-subtotal"';

    const intervalsHtml = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th'].map(m => {
      const iv = r.intervals?.[m] || { potensi: 0, same_outlet: 0, tunas_group: 0, other_dealer: 0, cai: 0, rate: '0%' };
      return `
        <td>${formatNumber(iv.potensi)}</td>
        <td class="td-same-outlet">${formatNumber(iv.same_outlet)}</td>
        <td class="td-tunas-group">${formatNumber(iv.tunas_group)}</td>
        <td class="td-other-dealer">${formatNumber(iv.other_dealer)}</td>
        <td>${formatNumber(iv.cai)}</td>
        <td style="font-weight: 700; color: #2563eb;">${escapeHtml(iv.rate)}</td>
      `;
    }).join('');

    const c = r.cumulative || { potensi: 0, same_outlet: 0, tunas_group: 0, other_dealer: 0, total_own_sales: 0, pct_so: '0%', pct_tg: '0%', pct_od: '0%', pct_total_rate: '0%' };
    const cumulHtml = `
      <td style="background: #faf5ff; font-weight: 700;">${formatNumber(c.potensi)}</td>
      <td style="background: #ecfdf5;">${formatNumber(c.same_outlet)}</td>
      <td style="background: #eff6ff;">${formatNumber(c.tunas_group)}</td>
      <td style="background: #fffbeb;">${formatNumber(c.other_dealer)}</td>
      <td style="background: #f1f5f9; font-weight: 700;">${formatNumber(c.total_own_sales)}</td>
      <td style="background: #ecfdf5; font-weight: 600;">${escapeHtml(c.pct_so)}</td>
      <td style="background: #eff6ff; font-weight: 600;">${escapeHtml(c.pct_tg)}</td>
      <td style="background: #fffbeb; font-weight: 600;">${escapeHtml(c.pct_od)}</td>
      <td style="background: #e0e7ff; font-weight: 800; color: #3730a3;">${escapeHtml(c.pct_total_rate)}</td>
    `;

    return `
      <tr ${trClass}>
        <td class="cell-text-left">${escapeHtml(r.category)}</td>
        <td class="cell-text-left">${escapeHtml(r.program)}</td>
        ${intervalsHtml}
        ${cumulHtml}
      </tr>
    `;
  }).join('');
}

function applyTcareRawFiltersAndRender() {
  if (!tcareData?.records) return;

  const progVal = document.getElementById('tcare-raw-filter-program')?.value || 'all';
  const ringVal = document.getElementById('tcare-raw-filter-ring')?.value || 'all';
  const custVal = document.getElementById('tcare-raw-filter-custtype')?.value || 'all';
  const vcatVal = document.getElementById('tcare-raw-filter-vcat')?.value || 'all';
  const dlrVal = document.getElementById('tcare-raw-filter-dealer')?.value || 'all';
  const search = (document.getElementById('tcare-raw-search-input')?.value || '').toLowerCase().trim();

  tcareFilteredRecords = tcareData.records.filter(r => {
    if (progVal !== 'all' && (r.program || '').toUpperCase() !== progVal.toUpperCase()) return false;
    if (ringVal !== 'all' && (r.ring_area || '').toUpperCase() !== ringVal.toUpperCase()) return false;
    if (custVal !== 'all' && (r.cust_type || '').toUpperCase() !== custVal.toUpperCase()) return false;
    if (vcatVal !== 'all' && (r.vehicle_category || '').toUpperCase() !== vcatVal.toUpperCase()) return false;
    if (dlrVal !== 'all' && (r.last_dealer || '').toUpperCase() !== dlrVal.toUpperCase()) return false;

    // Quick pills
    if (tcareActiveQuickFilter === 'tcare' && !((r.program || '').toUpperCase().includes('T-CARE') && !(r.program || '').toUpperCase().includes('LITE'))) return false;
    if (tcareActiveQuickFilter === 'lite' && (r.program || '').toUpperCase() !== 'T-CARE LITE') return false;
    if (tcareActiveQuickFilter === 'liteplus' && !(r.program || '').toUpperCase().includes('LITE+')) return false;
    if (tcareActiveQuickFilter === 'ring1' && (r.ring_area || '').toUpperCase() !== 'RING 1') return false;
    if (tcareActiveQuickFilter === 'hybrid' && (r.vehicle_category || '').toUpperCase() !== 'HYBRID') return false;
    if (tcareActiveQuickFilter === 'fleet' && (r.cust_type || '').toUpperCase() !== 'FLEET') return false;

    // Search query
    if (search) {
      const match = (r.vin || '').toLowerCase().includes(search) ||
                    (r.customer_name || '').toLowerCase().includes(search) ||
                    (r.model || '').toLowerCase().includes(search) ||
                    (r.phone || '').toLowerCase().includes(search) ||
                    (r.sales_person || '').toLowerCase().includes(search) ||
                    (r.spv || '').toLowerCase().includes(search) ||
                    (r.address || '').toLowerCase().includes(search);
      if (!match) return false;
    }
    return true;
  });

  renderTcareRawTable();
}

function renderTcareRawTable() {
  const tbody = document.getElementById('tcare-raw-table-body');
  const countTotalEl = document.getElementById('tcare-raw-count-total');
  const countRangeEl = document.getElementById('tcare-raw-count-range');
  const pageInfoEl = document.getElementById('tcare-raw-page-info');
  const pagBtnsEl = document.getElementById('tcare-raw-pagination-buttons');

  if (!tbody) return;

  const total = tcareFilteredRecords.length;
  if (countTotalEl) countTotalEl.textContent = formatNumber(total);

  if (total === 0) {
    tbody.innerHTML = '<tr><td colspan="12" style="text-align: center; padding: 24px; color: #64748b;">Tidak ada data T-Care yang cocok dengan filter yang dipilih</td></tr>';
    if (countRangeEl) countRangeEl.textContent = '0 - 0';
    if (pageInfoEl) pageInfoEl.textContent = 'Halaman 0 dari 0';
    if (pagBtnsEl) pagBtnsEl.innerHTML = '';
    return;
  }

  const totalPages = Math.ceil(total / tcareRawPageSize);
  if (tcareRawPage > totalPages) tcareRawPage = totalPages;
  if (tcareRawPage < 1) tcareRawPage = 1;

  const startIdx = (tcareRawPage - 1) * tcareRawPageSize;
  const endIdx = Math.min(startIdx + tcareRawPageSize, total);

  if (countRangeEl) countRangeEl.textContent = `${startIdx + 1} - ${endIdx}`;
  if (pageInfoEl) pageInfoEl.textContent = `Halaman ${tcareRawPage} dari ${totalPages}`;

  const pageData = tcareFilteredRecords.slice(startIdx, endIdx);

  tbody.innerHTML = pageData.map((rec, idx) => {
    let progBadge = 'background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe;';
    if ((rec.program || '').includes('LITE+')) progBadge = 'background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0;';
    else if ((rec.program || '').includes('LITE')) progBadge = 'background: #fefce8; color: #854d0e; border: 1px solid #fef08a;';

    let dlrBadge = 'background: #f1f5f9; color: #475569;';
    if ((rec.last_dealer || '').includes('SAME')) dlrBadge = 'background: #ecfdf5; color: #065f46; font-weight: 700;';
    else if ((rec.last_dealer || '').includes('TUNAS')) dlrBadge = 'background: #eff6ff; color: #1e40af; font-weight: 700;';
    else if ((rec.last_dealer || '').includes('OTHER')) dlrBadge = 'background: #fffbeb; color: #92400e; font-weight: 700;';

    return `
      <tr>
        <td style="text-align: center; color: #64748b; font-size: 11px;">${startIdx + idx + 1}</td>
        <td><strong style="font-family: monospace; font-size: 11px; color: #1e293b;">${escapeHtml(rec.vin || '-')}</strong></td>
        <td><span style="font-weight: 600; color: #0f172a;">${escapeHtml(rec.model || '-')}</span></td>
        <td style="font-size: 11px; color: #475569;">${escapeHtml(rec.dec_ym || '-')}</td>
        <td><strong style="color: #0f172a;">${escapeHtml(rec.customer_name || '-')}</strong></td>
        <td><span class="tag-badge" style="font-size: 10px; background: #f8fafc; border: 1px solid #e2e8f0; color: #334155;">${escapeHtml(rec.ring_area || '-')}</span></td>
        <td><span style="font-size: 11px; color: #475569;">${escapeHtml(rec.cust_type || '-')}</span></td>
        <td><span class="tag-badge" style="${progBadge} font-size: 10px; font-weight: 700;">${escapeHtml(rec.program || '-')}</span></td>
        <td style="font-size: 11px; color: #1e293b;">${escapeHtml(rec.last_service || '-')}</td>
        <td><span class="tag-badge" style="${dlrBadge} font-size: 10px;">${escapeHtml(rec.last_dealer || '-')}</span></td>
        <td style="font-size: 11px; color: #64748b; max-width: 160px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${escapeHtml(rec.last_fu_history || '-')}">${escapeHtml(rec.last_fu_history || '-')}</td>
        <td style="text-align: center;">
          <button type="button" class="btn-sbi-action" onclick="openTcareDetailModalById(${rec.id})" title="Lihat Profil Lengkap">
            👁️ Detail
          </button>
        </td>
      </tr>
    `;
  }).join('');

  // Pagination buttons
  renderTcarePaginationButtons(totalPages);
}

function renderTcarePaginationButtons(totalPages) {
  const pagBtnsEl = document.getElementById('tcare-raw-pagination-buttons');
  if (!pagBtnsEl) return;

  let btns = '';
  btns += `<button type="button" class="btn-sbi-page" ${tcareRawPage === 1 ? 'disabled' : ''} onclick="changeTcareRawPage(1)">&laquo;</button>`;
  btns += `<button type="button" class="btn-sbi-page" ${tcareRawPage === 1 ? 'disabled' : ''} onclick="changeTcareRawPage(${tcareRawPage - 1})">&lsaquo;</button>`;

  const maxVisible = 5;
  let startP = Math.max(1, tcareRawPage - 2);
  let endP = Math.min(totalPages, startP + maxVisible - 1);
  if (endP - startP < maxVisible - 1) {
    startP = Math.max(1, endP - maxVisible + 1);
  }

  for (let p = startP; p <= endP; p++) {
    btns += `<button type="button" class="btn-sbi-page ${p === tcareRawPage ? 'active' : ''}" onclick="changeTcareRawPage(${p})">${p}</button>`;
  }

  btns += `<button type="button" class="btn-sbi-page" ${tcareRawPage === totalPages ? 'disabled' : ''} onclick="changeTcareRawPage(${tcareRawPage + 1})">&rsaquo;</button>`;
  btns += `<button type="button" class="btn-sbi-page" ${tcareRawPage === totalPages ? 'disabled' : ''} onclick="changeTcareRawPage(${totalPages})">&raquo;</button>`;

  pagBtnsEl.innerHTML = btns;
}

window.changeTcareRawPage = function(p) {
  tcareRawPage = p;
  renderTcareRawTable();
  document.querySelector('#pane-tcare .sbi-table-wrap')?.scrollTo({ top: 0, behavior: 'smooth' });
};

window.openTcareDetailModalById = function(id) {
  if (!tcareData?.records) return;
  const rec = tcareData.records.find(r => r.id === id);
  if (rec) openTcareDetailModal(rec);
};

function openTcareDetailModal(rec) {
  const modal = document.getElementById('tcare-detail-modal');
  const titleEl = document.getElementById('tcare-modal-title');
  const progBadge = document.getElementById('tcare-modal-prog-badge');
  const dlrBadge = document.getElementById('tcare-modal-dealer-badge');
  const body = document.getElementById('tcare-modal-body-content');

  if (!modal || !body) return;

  if (titleEl) titleEl.textContent = `${rec.customer_name || 'Pelanggan'} — ${rec.model || 'Unit'}`;
  if (progBadge) progBadge.textContent = rec.program || 'T-CARE';
  if (dlrBadge) dlrBadge.textContent = rec.last_dealer || '-';

  // Format phone WA link
  let phoneClean = (rec.phone || '').replace(/[^0-9]/g, '');
  if (phoneClean.startsWith('0')) phoneClean = '62' + phoneClean.slice(1);
  const waBtnHtml = phoneClean ? `
    <a href="https://wa.me/${phoneClean}" target="_blank" rel="noopener noreferrer" style="display: inline-flex; align-items: center; gap: 4px; background: #25d366; color: #ffffff; padding: 2px 7px; border-radius: 4px; font-size: 10px; font-weight: 700; text-decoration: none; margin-left: 6px;">
      WhatsApp
    </a>
  ` : '';

  body.innerHTML = `
    <!-- 1. Data Kendaraan -->
    <div class="sbi-detail-section">
      <div class="sbi-detail-section-title">
        <span>🚗</span> Data Spesifikasi Kendaraan
      </div>
      <div class="sbi-detail-grid">
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Nomor Rangka (VIN)</span>
          <span class="sbi-detail-val" style="font-family: monospace; font-size: 13px; font-weight: 800; color: #1e3a8a;">${escapeHtml(rec.vin || '-')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Model Kendaraan</span>
          <span class="sbi-detail-val" style="font-weight: 700;">${escapeHtml(rec.model || '-')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Kategori Unit</span>
          <span class="sbi-detail-val">${escapeHtml(rec.vehicle_category || '-')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Kategori LCGC</span>
          <span class="sbi-detail-val">${escapeHtml(rec.lcgc || '-')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Tanggal Delivery</span>
          <span class="sbi-detail-val">${escapeHtml(rec.delivery_date || '-')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">DEC Delivery (Bulan &amp; Tahun)</span>
          <span class="sbi-detail-val" style="color: #2563eb; font-weight: 700;">${escapeHtml(rec.dec_month || '')} ${escapeHtml(rec.dec_year || '')} (${escapeHtml(rec.dec_ym || '-')})</span>
        </div>
      </div>
    </div>

    <!-- 2. Profil Pelanggan & Wilayah -->
    <div class="sbi-detail-section">
      <div class="sbi-detail-section-title">
        <span>👤</span> Profil Pelanggan &amp; Domisili
      </div>
      <div class="sbi-detail-grid">
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Nama Pelanggan</span>
          <span class="sbi-detail-val" style="font-size: 14px; font-weight: 800;">${escapeHtml(rec.customer_name || '-')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Tipe Pelanggan (Segmentasi)</span>
          <span class="sbi-detail-val">${escapeHtml(rec.cust_type || 'Retail')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Nomor Telepon / Handphone</span>
          <span class="sbi-detail-val">${escapeHtml(rec.phone || '-')} ${waBtnHtml}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Ring Area Domisili</span>
          <span class="sbi-detail-val" style="font-weight: 700; color: #d97706;">${escapeHtml(rec.ring_area || '-')}</span>
        </div>
        <div class="sbi-detail-item" style="grid-column: span 2;">
          <span class="sbi-detail-label">Alamat Lengkap</span>
          <span class="sbi-detail-val">${escapeHtml(rec.address || '-')}</span>
        </div>
      </div>
    </div>

    <!-- 3. Status Program T-Care & Riwayat Servis -->
    <div class="sbi-detail-section">
      <div class="sbi-detail-section-title">
        <span>📋</span> Status Program &amp; Servis Berkala
      </div>
      <div class="sbi-detail-grid">
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Program T-Care Terdaftar</span>
          <span class="sbi-detail-val" style="color: #2563eb; font-weight: 800;">${escapeHtml(rec.program || '-')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Servis Terakhir yang Dilakukan</span>
          <span class="sbi-detail-val" style="font-weight: 700;">${escapeHtml(rec.last_service || '-')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Tanggal Servis Terakhir</span>
          <span class="sbi-detail-val">${escapeHtml(rec.last_service_date || '-')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Bengkel / Dealer Terakhir</span>
          <span class="sbi-detail-val" style="color: #059669; font-weight: 700;">${escapeHtml(rec.last_dealer || '-')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Habit Servis Pelanggan</span>
          <span class="sbi-detail-val">${escapeHtml(rec.habit_status || '-')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Status Dealer Terakhir</span>
          <span class="sbi-detail-val">${escapeHtml(rec.dlr_status || '-')}</span>
        </div>
      </div>
    </div>

    <!-- 4. Tim Sales & History Follow Up -->
    <div class="sbi-detail-section">
      <div class="sbi-detail-section-title">
        <span>🤝</span> Tim Sales &amp; Catatan Follow Up
      </div>
      <div class="sbi-detail-grid">
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Nama Sales Person</span>
          <span class="sbi-detail-val">${escapeHtml(rec.sales_person || '-')}</span>
        </div>
        <div class="sbi-detail-item">
          <span class="sbi-detail-label">Supervisor (SPV)</span>
          <span class="sbi-detail-val">${escapeHtml(rec.spv || '-')}</span>
        </div>
        <div class="sbi-detail-item" style="grid-column: span 2;">
          <span class="sbi-detail-label">Catatan Riwayat Follow Up Terakhir</span>
          <span class="sbi-detail-val" style="background: #f8fafc; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0; font-style: italic;">
            ${escapeHtml(rec.last_fu_history || 'Belum ada catatan follow up')}
          </span>
        </div>
      </div>
    </div>
  `;

  modal.classList.add('active');
}

function exportTcareRawCsv() {
  if (!tcareFilteredRecords || tcareFilteredRecords.length === 0) {
    alert('Tidak ada data yang dapat diekspor!');
    return;
  }

  const headers = [
    'No', 'VIN', 'Model Kendaraan', 'Delivery Date', 'DEC Month', 'DEC Year', 'DEC Y-M',
    'Nama Pelanggan', 'No HP', 'Alamat', 'Ring Area', 'Tipe Pelanggan', 'Kategori Mobil',
    'LCGC', 'Program T-Care', 'Servis Terakhir', 'Tanggal Servis Terakhir', 'Bengkel Terakhir',
    'Habit Servis', 'Status Dealer', 'Sales Person', 'SPV', 'Riwayat Follow Up'
  ];

  const rows = tcareFilteredRecords.map((r, i) => [
    i + 1,
    `"${(r.vin || '').replace(/"/g, '""')}"`,
    `"${(r.model || '').replace(/"/g, '""')}"`,
    `"${(r.delivery_date || '').replace(/"/g, '""')}"`,
    `"${(r.dec_month || '').replace(/"/g, '""')}"`,
    `"${(r.dec_year || '').replace(/"/g, '""')}"`,
    `"${(r.dec_ym || '').replace(/"/g, '""')}"`,
    `"${(r.customer_name || '').replace(/"/g, '""')}"`,
    `"${(r.phone || '').replace(/"/g, '""')}"`,
    `"${(r.address || '').replace(/"/g, '""')}"`,
    `"${(r.ring_area || '').replace(/"/g, '""')}"`,
    `"${(r.cust_type || '').replace(/"/g, '""')}"`,
    `"${(r.vehicle_category || '').replace(/"/g, '""')}"`,
    `"${(r.lcgc || '').replace(/"/g, '""')}"`,
    `"${(r.program || '').replace(/"/g, '""')}"`,
    `"${(r.last_service || '').replace(/"/g, '""')}"`,
    `"${(r.last_service_date || '').replace(/"/g, '""')}"`,
    `"${(r.last_dealer || '').replace(/"/g, '""')}"`,
    `"${(r.habit_status || '').replace(/"/g, '""')}"`,
    `"${(r.dlr_status || '').replace(/"/g, '""')}"`,
    `"${(r.sales_person || '').replace(/"/g, '""')}"`,
    `"${(r.spv || '').replace(/"/g, '""')}"`,
    `"${(r.last_fu_history || '').replace(/"/g, '""')}"`
  ]);

  const csvContent = '\uFEFF' + [headers.join(','), ...rows.map(e => e.join(','))].join('\r\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `tcare_data_kiaracondong_${new Date().toISOString().slice(0, 10)}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
'''

target_file = r'c:\laragon\www\dashboard_bengkel\assets\js\dashboard.js'
with open(target_file, 'a', encoding='utf-8') as f:
    f.write(code)

print('Appended T-Care code to assets/js/dashboard.js successfully.')
