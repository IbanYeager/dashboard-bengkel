const fs = require('fs');

global.window = { addEventListener: () => {} };
const domStore = {};
global.document = {
  addEventListener: () => {},
  querySelectorAll: () => [],
  getElementById: (id) => {
    if (!domStore[id]) {
      domStore[id] = { id, textContent: '', innerHTML: '', title: '', style: {}, classList: { add: () => {}, remove: () => {} } };
    }
    return domStore[id];
  }
};
global.Chart = function() { return { destroy: () => {} }; };

global.mockData = JSON.parse(fs.readFileSync('data/dashboard_data.json', 'utf8'));
let code = fs.readFileSync('assets/js/dashboard.js', 'utf8');
code = code.replace('let dashboardData = null;', 'global.dashboardData = global.mockData; let dashboardData = global.mockData;');
code = code.replace('const STATE =', 'global.STATE =');
eval(code);

// Test 1: September 2026
STATE.year = '2026';
STATE.quarter = 'all';
STATE.month = 'September';
STATE.sa = 'all';
STATE.segment = 'all';

renderHeroKPIs();

console.log('=== SEPTEMBER 2026 EXECUTIVE KPI CARDS ===');
console.log('1. CPUS:', domStore['kpi-cpus-val']?.textContent, 'Target:', domStore['kpi-cpus-target']?.textContent);
console.log('2. Rev:', domStore['kpi-rev-val']?.textContent, 'Target:', domStore['kpi-rev-target']?.textContent);
console.log('3. Rev / Unit:', domStore['kpi-revpcpus-val']?.textContent, 'Achieve:', domStore['kpi-revpcpus-achieve']?.textContent, 'LY:', domStore['kpi-revpcpus-ly']?.textContent);
console.log('4. T-Care:', domStore['kpi-tcare-val']?.textContent, 'Detail:', domStore['kpi-tcare-detail']?.textContent);

// Test 2: Full Year 2026 (YTD)
STATE.year = '2026';
STATE.quarter = 'all';
STATE.month = 'all';
STATE.sa = 'all';
STATE.segment = 'all';

renderHeroKPIs();

console.log('\n=== FULL YEAR 2026 (YTD) EXECUTIVE KPI CARDS ===');
console.log('1. CPUS:', domStore['kpi-cpus-val']?.textContent, 'Target:', domStore['kpi-cpus-target']?.textContent);
console.log('2. Rev:', domStore['kpi-rev-val']?.textContent, 'Target:', domStore['kpi-rev-target']?.textContent);
console.log('3. Rev / Unit:', domStore['kpi-revpcpus-val']?.textContent, 'Achieve:', domStore['kpi-revpcpus-achieve']?.textContent, 'LY:', domStore['kpi-revpcpus-ly']?.textContent);
console.log('4. T-Care:', domStore['kpi-tcare-val']?.textContent, 'Detail:', domStore['kpi-tcare-detail']?.textContent);
