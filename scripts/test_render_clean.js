const fs = require('fs');

const elements = {};
function makeElement(id) {
  return {
    id,
    innerHTML: '',
    textContent: '',
    value: 'all',
    style: {},
    classList: { add: ()=>{}, remove: ()=>{} },
    addEventListener: ()=>{}
  };
}
const doc = {
  getElementById: (id) => {
    if (!elements[id]) elements[id] = makeElement(id);
    return elements[id];
  },
  querySelectorAll: () => [],
  querySelector: () => makeElement('q'),
  addEventListener: () => {}
};
global.document = doc;
global.window = { addEventListener: () => {} };

// Read dashboard.js
const jsCode = fs.readFileSync('assets/js/dashboard.js', 'utf8');

// Run within a Function wrapper
const runDashboard = new Function('fs', 'elements', jsCode + `
  tcareData = JSON.parse(fs.readFileSync('data/tcare_data.json', 'utf8'));
  console.log('tcareData loaded with records:', tcareData.records.length);
  renderTcare();
  console.log('tbody rows count:', (elements['tcare-monitoring-tbody']?.innerHTML?.match(/<tr/g) || []).length);
  console.log('stepper program rows:', (elements['tcare-stepper-program-container']?.innerHTML?.match(/tcare-prog-row/g) || []).length);
  console.log('stepper vtype rows:', (elements['tcare-stepper-vtype-container']?.innerHTML?.match(/tcare-prog-row/g) || []).length);
  console.log('retail rows count:', (elements['tcare-retail-tbody']?.innerHTML?.match(/<tr/g) || []).length);
  console.log('fleet rows count:', (elements['tcare-fleet-tbody']?.innerHTML?.match(/<tr/g) || []).length);
  console.log('potency rows count:', (elements['tcare-potency-tbody']?.innerHTML?.match(/<tr/g) || []).length);
  console.log('matrix rows count:', (elements['tcare-matrix-tbody']?.innerHTML?.match(/<tr/g) || []).length);
  console.log('raw table rows count:', (elements['tcare-raw-table-body']?.innerHTML?.match(/<tr/g) || []).length);
`);

try {
  runDashboard(fs, elements);
  console.log('SUCCESS: All T-Care tables rendered cleanly!');
} catch (err) {
  console.error('ERROR during execution:', err);
}
