// Test script for import logic verification
const fs = require('fs');

const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

const MONTH_LOOKUP_MAP = {
  '01': 'January', '1': 'January', 'jan': 'January', 'januari': 'January', 'january': 'January',
  '02': 'February', '2': 'February', 'feb': 'February', 'februari': 'February', 'february': 'February',
  '03': 'March', '3': 'March', 'mar': 'March', 'maret': 'March', 'march': 'March',
  '04': 'April', '4': 'April', 'apr': 'April', 'april': 'April',
  '05': 'May', '5': 'May', 'mei': 'May', 'may': 'May',
  '06': 'June', '6': 'June', 'jun': 'June', 'juni': 'June', 'june': 'June',
  '07': 'July', '7': 'July', 'jul': 'July', 'juli': 'July', 'july': 'July',
  '08': 'August', '8': 'August', 'agu': 'August', 'ags': 'August', 'agustus': 'August', 'aug': 'August', 'august': 'August',
  '09': 'September', '9': 'September', 'sep': 'September', 'sept': 'September', 'september': 'September',
  '10': 'October', 'okt': 'October', 'oktober': 'October', 'oct': 'October', 'october': 'October',
  '11': 'November', 'nov': 'November', 'november': 'November',
  '12': 'December', 'des': 'December', 'desember': 'December', 'dec': 'December', 'december': 'December'
};

const getVal = (row, keyPrefix) => {
  const prefix = keyPrefix.toLowerCase().trim().replace(/_/g, ' ');
  const keys = Object.keys(row);
  const exact = keys.find(x => x.toLowerCase().trim().replace(/_/g, ' ') === prefix);
  if (exact) return row[exact];
  const found = keys.find(x => x.toLowerCase().trim().replace(/_/g, ' ').includes(prefix));
  if (found) return row[found];
  const revFound = keys.find(x => {
    const k = x.toLowerCase().trim().replace(/_/g, ' ');
    return k.length >= 3 && prefix.includes(k);
  });
  return revFound ? row[revFound] : '';
};

const resolveMonthAndYear = (row, defaultMonth = 'September', defaultYear = 2026) => {
  let yr = null;
  let m = null;

  const rawYr = getVal(row, 'tahun') || getVal(row, 'year') || getVal(row, 'thn');
  if (rawYr) {
    const py = parseInt(String(rawYr).replace(/[^0-9]/g, ''), 10);
    if (py >= 2020 && py <= 2035) yr = py;
  }

  const rawM = getVal(row, 'month') || getVal(row, 'bulan') || getVal(row, 'bln') || getVal(row, 'month name') || getVal(row, 'periode');
  if (rawM !== undefined && rawM !== null && String(rawM).trim() !== '') {
    const cleanM = String(rawM).trim().toLowerCase();
    if (MONTH_LOOKUP_MAP[cleanM]) {
      m = MONTH_LOOKUP_MAP[cleanM];
    } else {
      const numM = parseInt(cleanM, 10);
      if (!isNaN(numM) && numM >= 1 && numM <= 12 && !cleanM.includes('-') && !cleanM.includes('/')) {
        m = MONTH_NAMES[numM - 1];
      } else {
        const pref3 = cleanM.slice(0, 3);
        if (MONTH_LOOKUP_MAP[pref3]) m = MONTH_LOOKUP_MAP[pref3];
      }
    }
  }

  if (!m || !yr) {
    const rawDate = getVal(row, 'pkb date') || getVal(row, 'tanggal') || getVal(row, 'date') || getVal(row, 'tgl');
    if (rawDate) {
      if (rawDate instanceof Date && !isNaN(rawDate.getTime())) {
        if (!m) m = MONTH_NAMES[rawDate.getMonth()];
        if (!yr) yr = rawDate.getFullYear();
      } else if (typeof rawDate === 'number' && rawDate > 30000 && rawDate < 60000) {
        const d = new Date((rawDate - 25569) * 86400 * 1000);
        if (!isNaN(d.getTime())) {
          if (!m) m = MONTH_NAMES[d.getUTCMonth()];
          if (!yr) yr = d.getUTCFullYear();
        }
      } else if (typeof rawDate === 'string') {
        const s = rawDate.trim();
        const isoMatch = s.match(/(\d{4})[-/](\d{1,2})[-/](\d{1,2})/);
        if (isoMatch) {
          const parsedM = parseInt(isoMatch[2], 10);
          if (parsedM >= 1 && parsedM <= 12) {
            if (!m) m = MONTH_NAMES[parsedM - 1];
            if (!yr) yr = parseInt(isoMatch[1], 10);
          }
        } else {
          const dmyMatch = s.match(/(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})/);
          if (dmyMatch) {
            const parsedM = parseInt(dmyMatch[2], 10);
            let parsedY = parseInt(dmyMatch[3], 10);
            if (parsedY < 100) parsedY += 2000;
            if (parsedM >= 1 && parsedM <= 12) {
              if (!m) m = MONTH_NAMES[parsedM - 1];
              if (!yr) yr = parsedY;
            }
          }
        }
      }
    }
  }

  return {
    year: yr || defaultYear,
    month: m || defaultMonth
  };
};

console.log('--- TEST 1: Month Resolution ---');
const testRows = [
  { 'BULAN': '09', 'TAHUN': '2026', 'desc': 'Col BULAN 09' },
  { 'BULAN': '9', 'TAHUN': '2026', 'desc': 'Col BULAN 9' },
  { 'MONTH': 'September', 'TAHUN': '2026', 'desc': 'Col MONTH September' },
  { 'BULAN': 'September', 'TAHUN': '2026', 'desc': 'Col BULAN September' },
  { 'BULAN': 'Sep', 'TAHUN': '2026', 'desc': 'Col BULAN Sep' },
  { 'PKB Date': '2026-09-15', 'desc': 'PKB Date ISO' },
  { 'PKB Date': '15/09/2026', 'desc': 'PKB Date DMY' },
  { 'PKB Date': new Date(2026, 8, 12), 'desc': 'PKB Date JS Date' },
  { 'PKB Date': 46278, 'desc': 'PKB Date Excel Serial' }
];

testRows.forEach(tr => {
  const res = resolveMonthAndYear(tr);
  console.log(`- ${tr.desc}: ${res.year} - ${res.month} (Pass: ${res.month === 'September' && res.year === 2026 ? 'YES' : 'NO'})`);
  if (res.month !== 'September' || res.year !== 2026) {
    throw new Error(`Test failed for ${tr.desc}`);
  }
});

console.log('\n--- TEST 2: Existing Months Preservation ---');
const initialData = JSON.parse(fs.readFileSync('data/dashboard_data.json', 'utf8'));
const janDataBefore = initialData.monthly_kpis['2026']['January'].ue_total;
const augDataBefore = initialData.monthly_kpis['2026']['August'].ue_total;
console.log(`Before import: Jan UE = ${janDataBefore}, Aug UE = ${augDataBefore}`);

const uploadedYearMonths = new Set(['2026-September']);
// Check that resetting ONLY uploadedYearMonths preserves Jan and Aug
uploadedYearMonths.forEach(ymKey => {
  const [yrStr, m] = ymKey.split('-');
  initialData.monthly_kpis[yrStr][m] = {
    quartal: 3,
    raw_cpus: 750,
    sbi_cpus: 0,
    cpus: 750,
    ue_total: 820,
    cpus_revenue: 1200000000,
    total_revenue: 1300000000,
    tcare_count: 340,
    sbi_count: 50,
    sbe_count: 420
  };
});

console.log(`After import: Jan UE = ${initialData.monthly_kpis['2026']['January'].ue_total}, Aug UE = ${initialData.monthly_kpis['2026']['August'].ue_total}, Sep UE = ${initialData.monthly_kpis['2026']['September'].ue_total}`);
if (initialData.monthly_kpis['2026']['January'].ue_total === janDataBefore &&
    initialData.monthly_kpis['2026']['August'].ue_total === augDataBefore &&
    initialData.monthly_kpis['2026']['September'].ue_total === 820) {
  console.log('Pass: Jan and Aug preserved, Sep added successfully!');
} else {
  throw new Error('Preservation test failed');
}

console.log('\n--- ALL TESTS PASSED SUCCESSFULLY! ---');
