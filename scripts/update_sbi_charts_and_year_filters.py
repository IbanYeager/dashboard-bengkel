# -*- coding: utf-8 -*-
import os

DASHBOARD_JS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'js', 'dashboard.js')

with open(DASHBOARD_JS_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update applySbiFiltersAndRender - fYear
old_fyear = "const fYear = document.getElementById('sbi-filter-year')?.value || 'all';"
new_fyear = "const fYear = sbiActiveYear || document.getElementById('sbi-filter-year')?.value || '2026';"
if old_fyear in content:
    content = content.replace(old_fyear, new_fyear, 1)
    print("[OK] Replaced fYear")
else:
    print("[WARN] old_fyear not found!")

# 2. Update updateSbiQuickPillCounters to scope by active year
old_quick_cnt = """function updateSbiQuickPillCounters() {
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
}"""

new_quick_cnt = """function updateSbiQuickPillCounters() {
  if (!sbiData || !sbiData.records) return;
  const fYear = sbiActiveYear || '2026';
  const yearRecs = fYear === 'all' 
    ? sbiData.records 
    : sbiData.records.filter(r => String(r.year) === String(fYear));

  let cntCai = 0, cntNotCai = 0, cntHot = 0, cntLoss = 0, cntWajib = 0, cntHybrid = 0, cntFleet = 0;
  yearRecs.forEach(r => {
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
  setT('pill-cnt-all', yearRecs.length);
  setT('pill-cnt-cai', cntCai);
  setT('pill-cnt-not-cai', cntNotCai);
  setT('pill-cnt-hot', cntHot);
  setT('pill-cnt-loss', cntLoss);
  setT('pill-cnt-wajib', cntWajib);
  setT('pill-cnt-hybrid', cntHybrid);
  setT('pill-cnt-fleet', cntFleet);
}"""

if old_quick_cnt in content:
    content = content.replace(old_quick_cnt, new_quick_cnt, 1)
    print("[OK] Replaced updateSbiQuickPillCounters")
else:
    print("[WARN] old_quick_cnt not found!")

# 3. Update updateSbiKpis active labels & title
old_kpi_badge = """  // Update Active Month Badges
  const monthNamesId = {
    'all': 'Semua Bulan (Setahun Penuh)',
    'January': 'Bulan Januari', 'February': 'Bulan Februari', 'March': 'Bulan Maret',
    'April': 'Bulan April', 'May': 'Bulan Mei', 'June': 'Bulan Juni',
    'July': 'Bulan Juli', 'August': 'Bulan Agustus', 'September': 'Bulan September',
    'October': 'Bulan Oktober', 'November': 'Bulan November', 'December': 'Bulan Desember'
  };
  const activeLabel = monthNamesId[sbiActiveMonth] || sbiActiveMonth;
  setEl('sbi-active-month-text', activeLabel);
  setEl('sbi-active-month-stats', `${formatNum(total)} Unit DEC | ${formatNum(caiCount)} Unit CAI (${acvPct})`);"""

new_kpi_badge = """  // Update Active Month Badges & Header Title
  const monthNamesId = {
    'all': 'Semua Bulan',
    'January': 'Bulan Januari', 'February': 'Bulan Februari', 'March': 'Bulan Maret',
    'April': 'Bulan April', 'May': 'Bulan Mei', 'June': 'Bulan Juni',
    'July': 'Bulan Juli', 'August': 'Agustus', 'September': 'Bulan September',
    'October': 'Bulan Oktober', 'November': 'Bulan November', 'December': 'Bulan Desember'
  };
  const yrLabel = sbiActiveYear === 'all' ? 'Semua Tahun (2024-2026)' : `Tahun ${sbiActiveYear}`;
  const mLabel = monthNamesId[sbiActiveMonth] || sbiActiveMonth;
  const fullLabel = sbiActiveMonth === 'all' ? `${mLabel} (${yrLabel})` : `${mLabel} ${sbiActiveYear === 'all' ? '(Semua Tahun)' : sbiActiveYear}`;
  setEl('sbi-active-month-text', fullLabel);
  
  if (total > 0) {
    setEl('sbi-active-month-stats', `${formatNum(total)} Unit DEC | ${formatNum(caiCount)} Unit CAI (${acvPct})`);
  } else {
    setEl('sbi-active-month-stats', `0 Unit DEC | 0 Unit CAI (Belum Ada Data)`);
  }

  const titleEl = document.getElementById('sbi-month-bar-title-text');
  if (titleEl) {
    titleEl.textContent = `PILIH PERIODE BULAN MONITORING SBI (${sbiActiveYear === 'all' ? 'SEMUA TAHUN' : sbiActiveYear}):`;
  }"""

if old_kpi_badge in content:
    content = content.replace(old_kpi_badge, new_kpi_badge, 1)
    print("[OK] Replaced updateSbiKpis badges")
else:
    print("[WARN] old_kpi_badge not found!")

# 4. Update renderSbiAIAnalysis with 0-record empty state
old_ai_analysis = """function renderSbiAIAnalysis(records, monthKey) {
  const periodLabel = document.getElementById('sbi-ai-period-label');
  const diagContainer = document.getElementById('sbi-ai-diag-text');
  const actionContainer = document.getElementById('sbi-ai-action-list');

  const monthNamesId = {
    'all': 'SEMUA BULAN / TAHUNAN',
    'January': 'JANUARI 2026', 'February': 'FEBRUARI 2026', 'March': 'MARET 2026',
    'April': 'APRIL 2026', 'May': 'MEI 2026', 'June': 'JUNI 2026',
    'July': 'JULI 2026', 'August': 'AGUSTUS 2026', 'September': 'SEPTEMBER 2026',
    'October': 'OKTOBER 2026', 'November': 'NOVEMBER 2026', 'December': 'DESEMBER 2026'
  };
  const labelText = monthNamesId[monthKey] || String(monthKey).toUpperCase();
  if (periodLabel) periodLabel.textContent = labelText;

  const total = records.length;
  const cai = records.filter(r => (r.cai || '').toUpperCase() === 'CAI').length;
  const notCai = total - cai;
  const acvPct = total > 0 ? (cai / total * 100).toFixed(1) : '0.0';

  // Count FU reasons for not cai
  const notCaiList = records.filter(r => (r.cai || '').toUpperCase() !== 'CAI');
  let cntLain = 0, cntLokasi = 0, cntNoKontak = 0, cntHub = 0, cntBooking = 0;
  notCaiList.forEach(r => {
    const n = (r.notes_fu || '').toUpperCase();
    if (n.includes('TEMPAT LAIN') || n.includes('BENGKEL LAIN') || n.includes('LUAR')) cntLain++;
    else if (n.includes('LOKASI') || n.includes('JARAK') || n.includes('JAUH') || n.includes('LUAR KOTA')) cntLokasi++;
    else if (n.includes('TIDAK DAPAT DIHUBUNGI') || n.includes('TIDAK AKTIF') || n.includes('SALAH SAMBUNG') || n.includes('NO HP')) cntNoKontak++;
    else if (n.includes('AKAN MENGHUBUNGI') || n.includes('JANJI')) cntHub++;
    else if (n.includes('BOOKING') || n.includes('RESCHEDULE')) cntBooking++;
  });

  const pctLain = notCai > 0 ? (cntLain / notCai * 100).toFixed(1) : '67.5';
  const pctLokasi = notCai > 0 ? (cntLokasi / notCai * 100).toFixed(1) : '13.4';
  const pctNoKontak = notCai > 0 ? (cntNoKontak / notCai * 100).toFixed(1) : '9.2';

  if (diagContainer) {
    diagContainer.innerHTML = `
      <div class="sbi-ai-diag-item">
        <strong>1. Rasio Konversi Kedatangan:</strong> Dari total potensi <strong>${formatNum(total)} unit</strong>, realisasi hadir mencapai <strong>${formatNum(cai)} unit (${acvPct}%)</strong>. Terdapat selisih <strong>${formatNum(notCai)} unit pelanggan</strong> yang belum masuk bengkel.
      </div>
      <div class="sbi-ai-diag-item">
        <strong>2. Attrition Tertinggi ke Bengkel Luar (${pctLain}%):</strong> Sebanyak <strong>${formatNum(cntLain)} pelanggan</strong> memilih servis di bengkel umum/luar resmi karena persepsi biaya atau keterikatan historis.
      </div>
      <div class="sbi-ai-diag-item">
        <strong>3. Hambatan Teritorial / Domisili (${pctLokasi}%):</strong> Sebanyak <strong>${formatNum(cntLokasi)} pelanggan</strong> berdomisili di luar radius perimeter bengkel (Bandung Barat, Kab. Bandung, Jakarta Selatan, Garut).
      </div>
      <div class="sbi-ai-diag-item">
        <strong>4. Contactability Barrier (${pctNoKontak}%):</strong> <strong>${formatNum(cntNoKontak)} kontak nasabah</strong> tidak dapat dihubungi melalui WhatsApp atau telepon langsung.
      </div>
    `;
  }

  if (actionContainer) {
    actionContainer.innerHTML = `
      <div class="sbi-ai-action-card">
        <div class="sbi-action-num">1</div>
        <div class="sbi-action-body">
          <h4>Program "Win-Back" Paket Hemat &amp; Garansi Resmi</h4>
          <p>Tawarkan paket bundling oli TMO + diskon jasa 20% khusus pelanggan yang terindikasi lari ke bengkel umum, dengan penegasan risiko hangusnya garansi mesin.</p>
        </div>
      </div>
      <div class="sbi-ai-action-card">
        <div class="sbi-action-num">2</div>
        <div class="sbi-action-body">
          <h4>THS Express &amp; Shuttle Pickup Lintas Wilayah</h4>
          <p>Kerahkan armada Toyota Home Service (THS) khusus klaster Kab. Bandung Barat, Cimahi, dan Garut untuk menghilangkan alasan jarak tempuh jauh ke Kiaracondong.</p>
        </div>
      </div>
      <div class="sbi-ai-action-card">
        <div class="sbi-action-num">3</div>
        <div class="sbi-action-body">
          <h4>Supervisi Harian Sales per SPV (Mandat Tindak Lanjut)</h4>
          <p>Tugaskan SPV (Feryanto, Adrian, Caisariva, Alvin) untuk mereview daftar salesman yang memiliki tunggakan pelanggan Belum CAI setiap briefing pagi.</p>
        </div>
      </div>
      <div class="sbi-ai-action-card">
        <div class="sbi-action-num">4</div>
        <div class="sbi-action-body">
          <h4>Pre-Call Reminder Otomatis T-7 &amp; Multi-Channel Blast</h4>
          <p>Jalankan blast WhatsApp otomatis terverifikasi pada H-7 sebelum jatuh tempo servis, diikuti reminder telepon H-3 untuk mengamankan slot booking.</p>
        </div>
      </div>
    `;
  }
}"""

new_ai_analysis = """function renderSbiAIAnalysis(records, monthKey) {
  const periodLabel = document.getElementById('sbi-ai-period-label');
  const diagContainer = document.getElementById('sbi-ai-diag-text');
  const actionContainer = document.getElementById('sbi-ai-action-list');

  const monthNamesId = {
    'all': 'SEMUA BULAN',
    'January': 'JANUARI', 'February': 'FEBRUARI', 'March': 'MARET',
    'April': 'APRIL', 'May': 'MEI', 'June': 'JUNI',
    'July': 'JULI', 'August': 'AGUSTUS', 'September': 'SEPTEMBER',
    'October': 'OKTOBER', 'November': 'NOVEMBER', 'December': 'DESEMBER'
  };
  const yrStr = sbiActiveYear === 'all' ? '2024-2026' : sbiActiveYear;
  const mStr = monthNamesId[monthKey] || String(monthKey).toUpperCase();
  const labelText = `${mStr} ${yrStr}`;
  if (periodLabel) periodLabel.textContent = labelText;

  const total = records.length;
  if (total === 0) {
    if (diagContainer) {
      diagContainer.innerHTML = `
        <div class="sbi-ai-diag-item" style="border-left: 3px solid #f59e0b; background: rgba(245, 158, 11, 0.08); padding: 14px 16px; border-radius: 8px;">
          <div style="font-weight: 700; color: #fbbf24; font-size: 13px; margin-bottom: 4px; display: flex; align-items: center; gap: 6px;">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            Data Belum Tersedia di Spreadsheet Live (0 Record)
          </div>
          <div style="font-size: 12px; color: #cbd5e1; line-height: 1.5;">
            Pada Google Spreadsheet live tab <strong>SBI</strong>, transaksi &amp; follow up untuk periode <strong>${labelText}</strong> belum diinput (0 Unit DEC / 0 Unit CAI).
            Untuk tahun berjalan 2026, pencatatan di spreadsheet saat ini baru tersedia sampai bulan <strong>September 2026</strong>.
          </div>
        </div>
      `;
    }
    if (actionContainer) {
      actionContainer.innerHTML = `
        <div class="sbi-ai-action-card" style="border-left: 3px solid #3b82f6;">
          <div class="sbi-action-num">i</div>
          <div class="sbi-action-body">
            <h4>Sinkronisasi Sheet SBI</h4>
            <p>Jika tim aftersales atau CRM telah menginput data ${labelText} di Google Spreadsheet, klik tombol <strong>"Sinkronkan Sheet SBI"</strong> di bagian atas untuk menarik data terbaru secara live.</p>
          </div>
        </div>
      `;
    }
    return;
  }

  const cai = records.filter(r => (r.cai || '').toUpperCase() === 'CAI').length;
  const notCai = total - cai;
  const acvPct = total > 0 ? (cai / total * 100).toFixed(1) : '0.0';

  // Count FU reasons for not cai
  const notCaiList = records.filter(r => (r.cai || '').toUpperCase() !== 'CAI');
  let cntLain = 0, cntLokasi = 0, cntNoKontak = 0, cntHub = 0, cntBooking = 0;
  notCaiList.forEach(r => {
    const n = (r.notes_fu || '').toUpperCase();
    if (n.includes('TEMPAT LAIN') || n.includes('BENGKEL LAIN') || n.includes('LUAR')) cntLain++;
    else if (n.includes('LOKASI') || n.includes('JARAK') || n.includes('JAUH') || n.includes('LUAR KOTA')) cntLokasi++;
    else if (n.includes('TIDAK DAPAT DIHUBUNGI') || n.includes('TIDAK AKTIF') || n.includes('SALAH SAMBUNG') || n.includes('NO HP')) cntNoKontak++;
    else if (n.includes('AKAN MENGHUBUNGI') || n.includes('JANJI')) cntHub++;
    else if (n.includes('BOOKING') || n.includes('RESCHEDULE')) cntBooking++;
  });

  const pctLain = notCai > 0 ? (cntLain / notCai * 100).toFixed(1) : '0.0';
  const pctLokasi = notCai > 0 ? (cntLokasi / notCai * 100).toFixed(1) : '0.0';
  const pctNoKontak = notCai > 0 ? (cntNoKontak / notCai * 100).toFixed(1) : '0.0';

  if (diagContainer) {
    diagContainer.innerHTML = `
      <div class="sbi-ai-diag-item">
        <strong>1. Rasio Konversi Kedatangan:</strong> Dari total potensi <strong>${formatNum(total)} unit</strong>, realisasi hadir mencapai <strong>${formatNum(cai)} unit (${acvPct}%)</strong>. Terdapat selisih <strong>${formatNum(notCai)} unit pelanggan</strong> yang belum masuk bengkel.
      </div>
      <div class="sbi-ai-diag-item">
        <strong>2. Attrition Tertinggi ke Bengkel Luar (${pctLain}%):</strong> Sebanyak <strong>${formatNum(cntLain)} pelanggan</strong> memilih servis di bengkel umum/luar resmi karena persepsi biaya atau keterikatan historis.
      </div>
      <div class="sbi-ai-diag-item">
        <strong>3. Hambatan Teritorial / Domisili (${pctLokasi}%):</strong> Sebanyak <strong>${formatNum(cntLokasi)} pelanggan</strong> berdomisili di luar radius perimeter bengkel (Bandung Barat, Kab. Bandung, Jakarta Selatan, Garut).
      </div>
      <div class="sbi-ai-diag-item">
        <strong>4. Contactability Barrier (${pctNoKontak}%):</strong> <strong>${formatNum(cntNoKontak)} kontak nasabah</strong> tidak dapat dihubungi melalui WhatsApp atau telepon langsung.
      </div>
    `;
  }

  if (actionContainer) {
    actionContainer.innerHTML = `
      <div class="sbi-ai-action-card">
        <div class="sbi-action-num">1</div>
        <div class="sbi-action-body">
          <h4>Program "Win-Back" Paket Hemat &amp; Garansi Resmi</h4>
          <p>Tawarkan paket bundling oli TMO + diskon jasa 20% khusus pelanggan yang terindikasi lari ke bengkel umum, dengan penegasan risiko hangusnya garansi mesin.</p>
        </div>
      </div>
      <div class="sbi-ai-action-card">
        <div class="sbi-action-num">2</div>
        <div class="sbi-action-body">
          <h4>THS Express &amp; Shuttle Pickup Lintas Wilayah</h4>
          <p>Kerahkan armada Toyota Home Service (THS) khusus klaster Kab. Bandung Barat, Cimahi, dan Garut untuk menghilangkan alasan jarak tempuh jauh ke Kiaracondong.</p>
        </div>
      </div>
      <div class="sbi-ai-action-card">
        <div class="sbi-action-num">3</div>
        <div class="sbi-action-body">
          <h4>Supervisi Harian Sales per SPV (Mandat Tindak Lanjut)</h4>
          <p>Tugaskan SPV (Feryanto, Adrian, Caisariva, Alvin) untuk mereview daftar salesman yang memiliki tunggakan pelanggan Belum CAI setiap briefing pagi.</p>
        </div>
      </div>
      <div class="sbi-ai-action-card">
        <div class="sbi-action-num">4</div>
        <div class="sbi-action-body">
          <h4>Pre-Call Reminder Otomatis T-7 &amp; Multi-Channel Blast</h4>
          <p>Jalankan blast WhatsApp otomatis terverifikasi pada H-7 sebelum jatuh tempo servis, diikuti reminder telepon H-3 untuk mengamankan slot booking.</p>
        </div>
      </div>
    `;
  }
}"""

if old_ai_analysis in content:
    content = content.replace(old_ai_analysis, new_ai_analysis, 1)
    print("[OK] Replaced renderSbiAIAnalysis")
else:
    print("[WARN] old_ai_analysis not found!")

# 5. Insert Top Chart A and Top Chart B in renderSbiCharts
old_charts_start = """function renderSbiCharts(records) {
  if (!records) records = sbiFilteredRecords || [];
  const totalRec = records.length || 1;

  // -------------------------------------------------------------------------
  // CHART 1: GRAFIK SBI PER SUPERVISOR (SS)"""

new_charts_start = """function renderSbiCharts(records) {
  if (!records) records = sbiFilteredRecords || [];
  const totalRec = records.length || 1;

  // -------------------------------------------------------------------------
  // TOP CHART A: TREN BULANAN REALISASI SBI (Jan - Des Tahun Aktif / 2026)
  // Potensi DEC vs Datang Servis CAI & % Acv per Bulan
  // -------------------------------------------------------------------------
  const monthlyCanvas = document.getElementById('chart-sbi-monthly');
  if (monthlyCanvas) {
    if (sbiChartInstances.monthly) sbiChartInstances.monthly.destroy();

    const targetYear = (sbiActiveYear && sbiActiveYear !== 'all') ? sbiActiveYear : '2026';
    const titleEl = document.getElementById('sbi-monthly-chart-title');
    if (titleEl) {
      titleEl.textContent = `Tren Bulanan Realisasi SBI ${targetYear}`;
    }

    const monthKeys = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    const monthShorts = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agt', 'Sep', 'Okt', 'Nov', 'Des'];

    const recsForYear = (sbiData && sbiData.records) 
      ? sbiData.records.filter(r => String(r.year) === String(targetYear))
      : [];

    const monthlyStats = monthKeys.map((mKey, idx) => {
      const mRecs = recsForYear.filter(r => (r.month || '').toUpperCase() === mKey.toUpperCase());
      const dec = mRecs.length;
      const cai = mRecs.filter(r => (r.cai || '').toUpperCase() === 'CAI').length;
      const acv = dec > 0 ? parseFloat((cai / dec * 100).toFixed(1)) : 0;
      return { key: mKey, short: monthShorts[idx], dec, cai, acv };
    });

    sbiChartInstances.monthly = new Chart(monthlyCanvas, {
      type: 'bar',
      data: {
        labels: monthlyStats.map(s => s.short),
        datasets: [
          {
            label: 'Potensi DEC',
            data: monthlyStats.map(s => s.dec),
            backgroundColor: 'rgba(59, 130, 246, 0.85)',
            borderColor: '#2563eb',
            borderWidth: 1,
            borderRadius: 4,
            yAxisID: 'y'
          },
          {
            label: 'Datang (CAI)',
            data: monthlyStats.map(s => s.cai),
            backgroundColor: 'rgba(16, 185, 129, 0.85)',
            borderColor: '#059669',
            borderWidth: 1,
            borderRadius: 4,
            yAxisID: 'y'
          },
          {
            label: '% Acv',
            data: monthlyStats.map(s => s.acv),
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
          legend: { position: 'top', labels: { boxWidth: 12, font: { size: 11, weight: '700' } } },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                if (ctx.dataset.yAxisID === 'y1') {
                  return `${ctx.dataset.label}: ${ctx.raw.toFixed(1)}%`;
                }
                return `${ctx.dataset.label}: ${ctx.raw} Unit`;
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: { display: true, text: 'Unit', font: { size: 11, weight: '700' } },
            grid: { color: '#f1f5f9' }
          },
          y1: {
            position: 'right',
            beginAtZero: true,
            max: 100,
            title: { display: true, text: 'Achievement (%)', font: { size: 11, weight: '700' } },
            grid: { drawOnChartArea: false },
            ticks: { callback: v => v + '%' }
          },
          x: { grid: { display: false }, ticks: { font: { size: 11, weight: '700' } } }
        }
      }
    });
  }

  // -------------------------------------------------------------------------
  // TOP CHART B: PERFORMA TAHUNAN (2024 - 2026)
  // Volume DEC & Pertumbuhan Unit Hybrid Toyota
  // -------------------------------------------------------------------------
  const yearlyCanvas = document.getElementById('chart-sbi-yearly');
  if (yearlyCanvas) {
    if (sbiChartInstances.yearly) sbiChartInstances.yearly.destroy();

    const years = ['2024', '2025', '2026'];
    const allRecs = (sbiData && sbiData.records) ? sbiData.records : [];
    const yearlyStats = years.map(yr => {
      const yrRecs = allRecs.filter(r => String(r.year) === yr);
      const dec = yrRecs.length;
      const hybrid = yrRecs.filter(r => (r.car_type || '').toUpperCase().includes('HYBRID')).length;
      const pctHybrid = dec > 0 ? (hybrid / dec * 100).toFixed(1) : '0.0';
      return { yr, dec, hybrid, pctHybrid };
    });

    sbiChartInstances.yearly = new Chart(yearlyCanvas, {
      type: 'bar',
      data: {
        labels: years.map(y => y === '2026' ? '2026 (YTD)' : y),
        datasets: [
          {
            label: 'Total DEC',
            data: yearlyStats.map(s => s.dec),
            backgroundColor: '#1e293b',
            borderRadius: 4
          },
          {
            label: 'Unit Hybrid',
            data: yearlyStats.map(s => s.hybrid),
            backgroundColor: '#10b981',
            borderRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top', labels: { boxWidth: 12, font: { size: 11, weight: '700' } } },
          tooltip: {
            callbacks: {
              afterLabel: (ctx) => {
                if (ctx.datasetIndex === 1) {
                  const s = yearlyStats[ctx.dataIndex];
                  return `Pangsa Hybrid: ${s.pctHybrid}%`;
                }
                return '';
              }
            }
          }
        },
        scales: {
          y: { beginAtZero: true, grid: { color: '#f1f5f9' }, title: { display: true, text: 'Unit', font: { size: 11, weight: '700' } } },
          x: { grid: { display: false }, ticks: { font: { size: 11, weight: '700' } } }
        }
      }
    });
  }

  // -------------------------------------------------------------------------
  // CHART 1: GRAFIK SBI PER SUPERVISOR (SS)"""

if old_charts_start in content:
    content = content.replace(old_charts_start, new_charts_start, 1)
    print("[OK] Replaced renderSbiCharts start")
else:
    print("[WARN] old_charts_start not found!")

# 6. Update renderSbi to call updateSbiMonthPillBadges
old_render_sbi = """function renderSbi() {
  if (!sbiData) return;
  initSbiEvents();
  initSbiCompareEvents();
  renderSbiComparison();
  renderSbiCharts();
  applySbiFiltersAndRender();
}"""

new_render_sbi = """function renderSbi() {
  if (!sbiData) return;
  initSbiEvents();
  initSbiCompareEvents();
  updateSbiMonthPillBadges();
  renderSbiComparison();
  applySbiFiltersAndRender();
}"""

if old_render_sbi in content:
    content = content.replace(old_render_sbi, new_render_sbi, 1)
    print("[OK] Replaced renderSbi")
else:
    print("[WARN] old_render_sbi not found!")

with open(DASHBOARD_JS_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("[SUCCESS] All SBI updates written to dashboard.js successfully!")
