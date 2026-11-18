const fs = require('fs');

// Mock browser objects
global.window = {
  addEventListener: () => {}
};
global.document = {
  addEventListener: () => {},
  querySelectorAll: () => [],
  getElementById: (id) => {
    return {
      id,
      textContent: '',
      innerHTML: '',
      style: {},
      classList: { toggle: () => {}, add: () => {}, remove: () => {} },
      getContext: () => ({
        save: () => {},
        restore: () => {},
        fillText: () => {}
      }),
      addEventListener: () => {}
    };
  }
};
global.Chart = function() {
  return { destroy: () => {}, resize: () => {} };
};

// Load data
const data = JSON.parse(fs.readFileSync('data/dashboard_data.json', 'utf8'));

// Now evaluate dashboard.js
const code = fs.readFileSync('assets/js/dashboard.js', 'utf8');

try {
  eval(code);
  console.log('Script evaluated successfully');
  
  // Set dashboardData and STATE
  dashboardData = data;
  STATE = {
    year: '2026',
    quarter: 'all',
    month: 'all',
    sa: 'all'
  };
  
  console.log('1. Testing renderSARadarCharts()...');
  renderSARadarCharts();
  console.log('renderSARadarCharts() OK!');
  
  console.log('2. Testing renderBreakdownTable()...');
  let breakdownTbody = { innerHTML: '' };
  document.getElementById = (id) => {
    if (id === 'breakdown-tbody') return breakdownTbody;
    return { textContent: '', innerHTML: '', style: {} };
  };
  renderBreakdownTable();
  console.log('renderBreakdownTable() OK! Length of HTML:', breakdownTbody.innerHTML.length);
  if (breakdownTbody.innerHTML.length < 50) {
    console.log('WARNING: breakdownTbody HTML is too short:', breakdownTbody.innerHTML);
  }
  
  console.log('3. Testing renderCrossSellingTable()...');
  let crossTbody = { innerHTML: '' };
  document.getElementById = (id) => {
    if (id === 'cross-tbody') return crossTbody;
    return { textContent: '', innerHTML: '', style: {} };
  };
  renderCrossSellingTable();
  console.log('renderCrossSellingTable() OK! Length of HTML:', crossTbody.innerHTML.length);
  if (crossTbody.innerHTML.length < 50) {
    console.log('WARNING: crossTbody HTML is too short:', crossTbody.innerHTML);
  }
  
} catch (err) {
  console.error('ERROR ENCOUNTERED:', err);
}
