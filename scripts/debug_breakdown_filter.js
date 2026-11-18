const fs = require('fs');
const data = JSON.parse(fs.readFileSync('data/dashboard_data.json', 'utf8'));

const yr = '2026';
const ly = '2025';

console.log('Total breakdown rows in data:', data.breakdown.length);

// Check isMonthInFilter
const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

function isMonthInFilter(m) {
  // If STATE.month === 'all'
  return true;
}

const saFilter = item => true;

const filteredBreakdown = data.breakdown.filter(item => String(item.year) === yr && isMonthInFilter(item.month_name) && saFilter(item));
console.log('Filtered breakdown rows for 2026:', filteredBreakdown.length);

if (filteredBreakdown.length > 0) {
  console.log('Sample filtered item:', filteredBreakdown[0]);
}

// Now let's check categories in renderBreakdownTable
const categories = [
  { label: 'CPUS (Total Unit Masuk)', filter: item => item.type_ue === 'CPUS' },
  { label: 'SBE (Servis Berkala)', filter: item => item.type_service === 'SBE' },
  { label: 'SEGMEN RETAIL', filter: item => item.fleet_retail === 'RETAIL' }
];

categories.forEach(cat => {
  const matches = filteredBreakdown.filter(item => cat.filter(item));
  console.log(`Cat: ${cat.label} -> matches: ${matches.length}`);
});

// Now let's check Cross Selling
console.log('\n--- CROSS SELLING ---');
console.log('Total cross_selling rows:', data.cross_selling ? data.cross_selling.length : 0);
const filteredCross = (data.cross_selling || []).filter(item => String(item.year) === yr && isMonthInFilter(item.month_name) && saFilter(item));
console.log('Filtered cross_selling rows for 2026:', filteredCross.length);
if (filteredCross.length > 0) {
  console.log('Sample cross item:', filteredCross[0]);
}
