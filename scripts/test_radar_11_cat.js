const fs = require('fs');

global.window = { addEventListener: () => {} };
const domStore = {};
global.document = {
  addEventListener: () => {},
  querySelectorAll: () => [],
  getElementById: (id) => {
    if (!domStore[id]) {
      domStore[id] = { 
        id, 
        textContent: '', 
        innerHTML: '', 
        title: '', 
        style: {}, 
        classList: { add: () => {}, remove: () => {} },
        getContext: () => ({ save: () => {}, restore: () => {} })
      };
    }
    return domStore[id];
  }
};

let capturedCharts = {};
global.Chart = function(ctx, config) {
  const chartId = Object.keys(domStore).find(k => domStore[k].getContext && domStore[k].getContext() === ctx) || 'unknown';
  capturedCharts[chartId] = config;
  return { destroy: () => {}, resize: () => {} };
};

global.mockData = JSON.parse(fs.readFileSync('data/dashboard_data.json', 'utf8'));
let code = fs.readFileSync('assets/js/dashboard.js', 'utf8');
code = code.replace('let dashboardData = null;', 'global.dashboardData = global.mockData; let dashboardData = global.mockData;');
code = code.replace('const STATE =', 'global.STATE =');
eval(code);

// Test renderSARadarCharts for September 2026
STATE.year = '2026';
STATE.quarter = 'all';
STATE.month = 'September';
STATE.sa = 'all';
STATE.segment = 'all';

renderSARadarCharts();

console.log('=== RADAR CHARTS (10 COMMODITIES) ===');
console.log('DIDIN Badge:', domStore['radar-badge-didin']?.textContent);
console.log('FICKY Badge:', domStore['radar-badge-ficky']?.textContent);
console.log('ACEP Badge:', domStore['radar-badge-acep']?.textContent);

console.log('\nDIDIN Radar Labels count:', capturedCharts['unknown']?.data?.labels?.length);
console.log('Labels:', capturedCharts['unknown']?.data?.labels);
console.log('DIDIN Highlights:', domStore['radar-highlights-didin']?.innerHTML?.includes('Pencapaian 10 Komoditas Produk'));
