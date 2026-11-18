import re

js_file = 'assets/js/dashboard.js'
with open(js_file, 'r', encoding='utf-8') as f:
    content = f.read()

# -------------------------------------------------------------------
# 1. ADD SEGMENT COMPOSITION CLUSTER IN renderBreakdownTable
# -------------------------------------------------------------------
old_breakdown_start = """function renderBreakdownTable() {
  const tbody = document.getElementById('breakdown-tbody');
  if (!tbody || !dashboardData) return;

  const yr = STATE.year;
  const ly = String(parseInt(yr) - 1);

  const saFilter = item => STATE.sa === 'all' || !item.sa || item.sa === STATE.sa;"""

new_breakdown_start = """function renderBreakdownTable() {
  const tbody = document.getElementById('breakdown-tbody');
  if (!tbody || !dashboardData) return;

  const yr = STATE.year;
  const ly = String(parseInt(yr) - 1);

  const saFilter = item => STATE.sa === 'all' || !item.sa || item.sa === STATE.sa;

  // Calculate Customer Segment Composition (Retail, Fleet, Sudeco, TPI) for active period
  let segRetU = 0, segRetRev = 0;
  let segFltU = 0, segFltRev = 0;
  let segSudU = 0, segSudRev = 0;
  let segTpiU = 0, segTpiRev = 0;

  if (dashboardData.breakdown) {
    dashboardData.breakdown
      .filter(item => String(item.year) === yr && isMonthInFilter(item.month_name) && saFilter(item))
      .forEach(item => {
        const seg = (item.fleet_retail || '').toUpperCase();
        const u = item.units || 0;
        const r = item.revenue || 0;
        if (seg.includes('SUDECO')) {
          segSudU += u; segSudRev += r;
        } else if (seg.includes('TPI')) {
          segTpiU += u; segTpiRev += r;
        } else if (seg.includes('FLEET')) {
          segFltU += u; segFltRev += r;
        } else {
          segRetU += u; segRetRev += r;
        }
      });
  }

  const totSegU = segRetU + segFltU + segSudU + segTpiU || 1;
  const pRet = (segRetU / totSegU) * 100;
  const pFlt = (segFltU / totSegU) * 100;
  const pSud = (segSudU / totSegU) * 100;
  const pTpi = (segTpiU / totSegU) * 100;

  // Update DOM segment cluster
  const totalUnitsBadge = document.getElementById('seg-total-units-badge');
  if (totalUnitsBadge) totalUnitsBadge.textContent = `Total Unit Entry: ${formatNum(totSegU)}`;

  const ratiosEl = document.getElementById('seg-composition-ratios');
  if (ratiosEl) ratiosEl.textContent = `Retail: ${pRet.toFixed(1)}% | Fleet: ${pFlt.toFixed(1)}% | Sudeco: ${pSud.toFixed(1)}% | TPI: ${pTpi.toFixed(1)}%`;

  const barRet = document.getElementById('seg-bar-retail');
  if (barRet) barRet.style.width = `${pRet}%`;
  const barFlt = document.getElementById('seg-bar-fleet');
  if (barFlt) barFlt.style.width = `${pFlt}%`;
  const barSud = document.getElementById('seg-bar-sudeco');
  if (barSud) barSud.style.width = `${pSud}%`;
  const barTpi = document.getElementById('seg-bar-tpi');
  if (barTpi) barTpi.style.width = `${pTpi}%`;

  const retUEl = document.getElementById('seg-retail-units');
  if (retUEl) retUEl.textContent = `${formatNum(segRetU)} Unit`;
  const retRevEl = document.getElementById('seg-retail-rev');
  if (retRevEl) retRevEl.textContent = formatIDR(segRetRev);
  const retPctEl = document.getElementById('seg-retail-pct');
  if (retPctEl) retPctEl.textContent = `${pRet.toFixed(1)}%`;

  const fltUEl = document.getElementById('seg-fleet-units');
  if (fltUEl) fltUEl.textContent = `${formatNum(segFltU)} Unit`;
  const fltRevEl = document.getElementById('seg-fleet-rev');
  if (fltRevEl) fltRevEl.textContent = formatIDR(segFltRev);
  const fltPctEl = document.getElementById('seg-fleet-pct');
  if (fltPctEl) fltPctEl.textContent = `${pFlt.toFixed(1)}%`;

  const sudUEl = document.getElementById('seg-sudeco-units');
  if (sudUEl) sudUEl.textContent = `${formatNum(segSudU)} Unit`;
  const sudRevEl = document.getElementById('seg-sudeco-rev');
  if (sudRevEl) sudRevEl.textContent = formatIDR(segSudRev);
  const sudPctEl = document.getElementById('seg-sudeco-pct');
  if (sudPctEl) sudPctEl.textContent = `${pSud.toFixed(1)}%`;

  const tpiUEl = document.getElementById('seg-tpi-units');
  if (tpiUEl) tpiUEl.textContent = `${formatNum(segTpiU)} Unit`;
  const tpiRevEl = document.getElementById('seg-tpi-rev');
  if (tpiRevEl) tpiRevEl.textContent = formatIDR(segTpiRev);
  const tpiPctEl = document.getElementById('seg-tpi-pct');
  if (tpiPctEl) tpiPctEl.textContent = `${pTpi.toFixed(1)}%`;"""

if old_breakdown_start in content:
    content = content.replace(old_breakdown_start, new_breakdown_start)
    print("1. Applied segment composition cluster in renderBreakdownTable")
else:
    print("WARNING: old_breakdown_start not found")

# -------------------------------------------------------------------
# 2. ADD renderMappingRingAndFleetCharts IN renderAreaMapping
# -------------------------------------------------------------------
old_render_all = """  renderAreaMapping();
  renderAreaCharacteristicsTable();
  renderDataExplorerTable();"""

new_render_all = """  renderAreaMapping();
  renderAreaCharacteristicsTable();
  renderMappingRingAndFleetCharts();
  renderDataExplorerTable();"""

if old_render_all in content:
    content = content.replace(old_render_all, new_render_all)
    print("2. Added renderMappingRingAndFleetCharts call to renderAll")
else:
    print("WARNING: old_render_all not found")

# Definition of renderMappingRingAndFleetCharts
mapping_charts_fn = """
let mapRingAreaInstance = null;
let mapFleetRetailInstance = null;

async function renderMappingRingAndFleetCharts() {
  if (!funnellingData) {
    try {
      const res = await fetch(`data/funnelling_data.json?v=8.0`);
      if (res.ok) funnellingData = await res.json();
    } catch (e) {
      // non-blocking
    }
  }
  if (!funnellingData) return;

  const ringTrend = funnellingData.monthly_ring_area_trend || {};
  const fleetTrend = funnellingData.monthly_fleet_retail_trend || {};
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agt', 'Sep'];

  // 1. Chart Ring Area in Mapping Pane
  const ringCanvas = document.getElementById('chart-map-ring-area');
  if (ringCanvas) {
    if (mapRingAreaInstance) mapRingAreaInstance.destroy();

    const ring1Con = months.map(m => ringTrend[m]?.['Ring 1']?.connected || 0);
    const ring1Fu = months.map(m => ringTrend[m]?.['Ring 1']?.cust_fu || 0);

    const ring2Con = months.map(m => ringTrend[m]?.['Ring 2']?.connected || 0);
    const ring2Fu = months.map(m => ringTrend[m]?.['Ring 2']?.cust_fu || 0);

    const ring3Con = months.map(m => ringTrend[m]?.['Ring 3']?.connected || 0);
    const ring3Fu = months.map(m => ringTrend[m]?.['Ring 3']?.cust_fu || 0);

    const outCon = months.map(m => ringTrend[m]?.['Out of Area']?.connected || 0);
    const outFu = months.map(m => ringTrend[m]?.['Out of Area']?.cust_fu || 0);

    mapRingAreaInstance = new Chart(ringCanvas.getContext('2d'), {
      type: 'bar',
      data: {
        labels: months,
        datasets: [
          { label: 'Ring 1 (Connected)', data: ring1Con, backgroundColor: '#2563eb', borderRadius: 3, stack: 'connected' },
          { label: 'Ring 2 (Connected)', data: ring2Con, backgroundColor: '#10b981', borderRadius: 3, stack: 'connected' },
          { label: 'Ring 3 (Connected)', data: ring3Con, backgroundColor: '#f59e0b', borderRadius: 3, stack: 'connected' },
          { label: 'Out Area (Connected)', data: outCon, backgroundColor: '#8b5cf6', borderRadius: 3, stack: 'connected' },
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
          legend: { position: 'top', labels: { boxWidth: 10, font: { size: 10, weight: '600' } } },
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

    const badge = document.getElementById('map-ring-area-kpi-badge');
    if (badge) {
      const totAllFu = ring1Fu.reduce((a,b)=>a+b,0) + ring2Fu.reduce((a,b)=>a+b,0) + ring3Fu.reduce((a,b)=>a+b,0) + outFu.reduce((a,b)=>a+b,0);
      const totAllCon = ring1Con.reduce((a,b)=>a+b,0) + ring2Con.reduce((a,b)=>a+b,0) + ring3Con.reduce((a,b)=>a+b,0) + outCon.reduce((a,b)=>a+b,0);
      badge.textContent = `Rasio Rata-rata: ${((totAllCon / totAllFu)*100).toFixed(1)}% Connected`;
    }
  }

  // 2. Chart Fleet / Retail in Mapping Pane
  const fleetCanvas = document.getElementById('chart-map-fleet-retail');
  if (fleetCanvas) {
    if (mapFleetRetailInstance) mapFleetRetailInstance.destroy();

    const retCon = months.map(m => fleetTrend[m]?.['Retail']?.connected || 0);
    const retFu = months.map(m => fleetTrend[m]?.['Retail']?.cust_fu || 0);

    const fltCon = months.map(m => fleetTrend[m]?.['Fleet']?.connected || 0);
    const fltFu = months.map(m => fleetTrend[m]?.['Fleet']?.cust_fu || 0);

    const retPct = months.map((m, i) => retFu[i] > 0 ? Math.round((retCon[i] / retFu[i]) * 100) : 0);
    const fltPct = months.map((m, i) => fltFu[i] > 0 ? Math.round((fltCon[i] / fltFu[i]) * 100) : 0);

    mapFleetRetailInstance = new Chart(fleetCanvas.getContext('2d'), {
      type: 'bar',
      data: {
        labels: months,
        datasets: [
          { type: 'bar', label: 'Retail Connected', data: retCon, backgroundColor: '#059669', borderRadius: 3, yAxisID: 'y' },
          { type: 'bar', label: 'Retail Cust FU', data: retFu, backgroundColor: '#a7f3d0', borderRadius: 3, yAxisID: 'y' },
          { type: 'bar', label: 'Fleet Connected', data: fltCon, backgroundColor: '#db2777', borderRadius: 3, yAxisID: 'y' },
          { type: 'bar', label: 'Fleet Cust FU', data: fltFu, backgroundColor: '#fbcfe8', borderRadius: 3, yAxisID: 'y' },
          { type: 'line', label: '% Connected Retail', data: retPct, borderColor: '#047857', borderWidth: 2, pointRadius: 3, yAxisID: 'yPct', tension: 0.2 },
          { type: 'line', label: '% Connected Fleet', data: fltPct, borderColor: '#be185d', borderWidth: 2, pointRadius: 3, borderDash: [3, 3], yAxisID: 'yPct', tension: 0.2 }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { position: 'top', labels: { boxWidth: 10, font: { size: 10, weight: '600' } } },
          tooltip: { backgroundColor: 'rgba(15, 23, 42, 0.95)' }
        },
        scales: {
          x: { grid: { display: false }, ticks: { font: { size: 10, weight: '700' } } },
          y: { beginAtZero: true, grid: { color: 'rgba(226, 232, 240, 0.5)' }, title: { display: true, text: 'Volume Call', font: { size: 10 } } },
          yPct: { position: 'right', beginAtZero: true, max: 100, grid: { display: false }, ticks: { callback: v => v + '%', font: { size: 9 } } }
        }
      }
    });

    const badgeFlt = document.getElementById('map-fleet-retail-kpi-badge');
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

pos_area_char = content.find('function renderAreaCharacteristicsTable() {')
if pos_area_char != -1:
    content = content[:pos_area_char] + mapping_charts_fn + "\n" + content[pos_area_char:]
    print("3. Inserted mapping_charts_fn definition")
else:
    print("WARNING: renderAreaCharacteristicsTable not found")

# Resize mapping charts on tab switch
old_tab_mapping = """    setTimeout(() => {
      if (areaMapInstance) areaMapInstance.invalidateSize();
    }, 150);"""

new_tab_mapping = """    setTimeout(() => {
      if (areaMapInstance) areaMapInstance.invalidateSize();
      renderMappingRingAndFleetCharts();
      if (mapRingAreaInstance) mapRingAreaInstance.resize();
      if (mapFleetRetailInstance) mapFleetRetailInstance.resize();
    }, 150);"""

if old_tab_mapping in content:
    content = content.replace(old_tab_mapping, new_tab_mapping)
    print("4. Updated tab switch for mapping charts resize")
else:
    print("WARNING: old_tab_mapping not found")

# -------------------------------------------------------------------
# 3. ENHANCE BOOKING TOOLTIP WITH EXPLICIT TARGET TEXT
# -------------------------------------------------------------------
old_booking_tooltip = """            callbacks: {
              label: (c) => {
                if (c.raw === null || c.raw === undefined) return ` ${ch.title}: Belum Ada Data`;
                return ` ${ch.title}: ${c.raw} Unit`;
              }
            }"""

new_booking_tooltip = """            callbacks: {
              label: (c) => {
                if (c.dataset.isTarget) return ` Garis Target: ${c.raw} Unit/bln`;
                if (c.raw === null || c.raw === undefined) return ` ${ch.title}: Belum Ada Data`;
                return ` ${ch.title}: ${c.raw} Unit`;
              }
            }"""

if old_booking_tooltip in content:
    content = content.replace(old_booking_tooltip, new_booking_tooltip)
    print("5. Updated booking tooltip with explicit Garis Target")
else:
    print("WARNING: old_booking_tooltip not found")

# -------------------------------------------------------------------
# 4. ADD btn-sync-ws-sheet LISTENER FOR LIVE SPREADSHEET SYNC
# -------------------------------------------------------------------
ws_sync_listener = """
  // WS Matrix Live Spreadsheet Sync Listener
  const btnSyncWs = document.getElementById('btn-sync-ws-sheet');
  if (btnSyncWs) {
    btnSyncWs.addEventListener('click', async () => {
      const icon = document.getElementById('ws-sync-spin-icon');
      const label = document.getElementById('ws-sync-label');
      if (icon) icon.classList.add('spinning');
      if (label) label.textContent = 'Menghubungkan Spreadsheet...';

      try {
        const resp = await fetch(`data/dashboard_data.json?v=${Date.now()}`);
        if (!resp.ok) throw new Error('Gagal mengambil data dari server');
        const freshData = await resp.json();
        if (freshData.ws_matrix_kabeng) {
          dashboardData.ws_matrix_kabeng = freshData.ws_matrix_kabeng;
          dashboardData.ws_matrix_excel = freshData.ws_matrix_excel;
          renderWSPerformanceTable();
          alert('✓ Sinkronisasi Berhasil! Data Workshop Performance Matrix (12 Bulan) telah dimutakhirkan dari Spreadsheet.');
        } else {
          alert('ℹ Data WS Matrix telah mutakhir.');
        }
      } catch (err) {
        alert('Gagal sinkronisasi data: ' + err.message);
      } finally {
        if (icon) icon.classList.remove('spinning');
        if (label) label.textContent = 'Tarik dari Google Spreadsheet Live';
      }
    });
  }
"""

old_init_ws = "function initWSMatrixImport() {"
if old_init_ws in content:
    content = content.replace(old_init_ws, old_init_ws + ws_sync_listener)
    print("6. Added btn-sync-ws-sheet event listener")
else:
    print("WARNING: old_init_ws not found")

with open(js_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("Finished applying all revisions to assets/js/dashboard.js")
